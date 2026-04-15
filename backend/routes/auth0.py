"""
Auth0 Social Login — Verify Auth0 JWT, sync user to PostgreSQL, return local JWT.
"""

import json
import urllib.request
from datetime import datetime, timedelta, timezone

import jwt as pyjwt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.config import settings
from backend.database import fetch_one, execute, execute_returning
from backend.routes.auth import create_access_token

router = APIRouter()

# ──── Auth0 JWKS cache ────

_jwks_cache = {"keys": [], "fetched_at": None}


def _fetch_jwks():
    """Fetch Auth0's JSON Web Key Set (public keys for RS256 verification)."""
    global _jwks_cache
    now = datetime.now(timezone.utc)

    # Cache for 1 hour
    if _jwks_cache["fetched_at"] and (now - _jwks_cache["fetched_at"]).total_seconds() < 3600:
        return _jwks_cache["keys"]

    if not settings.AUTH0_DOMAIN:
        raise HTTPException(status_code=500, detail="AUTH0_DOMAIN not configured")

    jwks_url = f"https://{settings.AUTH0_DOMAIN}/.well-known/jwks.json"
    try:
        req = urllib.request.Request(jwks_url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            jwks = json.loads(resp.read())
            _jwks_cache["keys"] = jwks.get("keys", [])
            _jwks_cache["fetched_at"] = now
            return _jwks_cache["keys"]
    except Exception as e:
        print(f"⚠️ Failed to fetch Auth0 JWKS: {e}")
        if _jwks_cache["keys"]:
            return _jwks_cache["keys"]  # Use stale cache
        raise HTTPException(status_code=500, detail="Failed to fetch Auth0 public keys")


def verify_auth0_token(token: str) -> dict:
    """
    Verify an Auth0 JWT using RS256 + JWKS.
    Returns the decoded payload (sub, email, name, picture, etc.).
    """
    jwks_keys = _fetch_jwks()

    # Decode header to find the key ID (kid)
    try:
        unverified_header = pyjwt.get_unverified_header(token)
    except pyjwt.exceptions.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token format")

    kid = unverified_header.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Token missing key ID")

    # Find the matching public key
    rsa_key = None
    for key in jwks_keys:
        if key.get("kid") == kid:
            rsa_key = key
            break

    if not rsa_key:
        # Refresh cache and try again
        _jwks_cache["fetched_at"] = None
        jwks_keys = _fetch_jwks()
        for key in jwks_keys:
            if key.get("kid") == kid:
                rsa_key = key
                break

    if not rsa_key:
        raise HTTPException(status_code=401, detail="Unable to find matching Auth0 signing key")

    # Build the public key and verify
    try:
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))

        payload = pyjwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE or None,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
            options={
                "verify_aud": bool(settings.AUTH0_AUDIENCE),
                "verify_iss": True,
                "verify_exp": True,
            },
        )
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Auth0 token expired")
    except pyjwt.InvalidAudienceError:
        raise HTTPException(status_code=401, detail="Invalid audience in Auth0 token")
    except pyjwt.InvalidIssuerError:
        raise HTTPException(status_code=401, detail="Invalid issuer in Auth0 token")
    except pyjwt.PyJWTError as e:
        raise HTTPException(status_code=401, detail=f"Auth0 token verification failed: {e}")


# ──── Schemas ────

class Auth0CallbackRequest(BaseModel):
    token: str


class Auth0UserInfoRequest(BaseModel):
    """Alternative: receive user info directly from Auth0 SPA SDK."""
    access_token: str
    user_info: dict = None


# ──── Routes ────

@router.post("/auth0-callback")
async def auth0_callback(req: Auth0CallbackRequest):
    """
    Receive Auth0 access token from frontend, verify it,
    sync user to PostgreSQL, return local JWT.
    """
    # Verify the Auth0 token
    payload = verify_auth0_token(req.token)

    auth0_sub = payload.get("sub", "")
    email = payload.get("email") or payload.get(f"https://{settings.AUTH0_DOMAIN}/email") or ""
    name = payload.get("name") or payload.get("nickname") or email.split("@")[0] if email else "User"
    picture = payload.get("picture", "")

    if not email and not auth0_sub:
        raise HTTPException(status_code=400, detail="Could not extract user identity from Auth0 token")

    # ── User sync: upsert into PostgreSQL ──

    # 1. Check by auth0_sub first
    user = None
    if auth0_sub:
        user = await fetch_one(
            "SELECT * FROM users WHERE auth0_sub = $1",
            auth0_sub
        )

    # 2. Check by email
    if not user and email:
        user = await fetch_one(
            "SELECT * FROM users WHERE email = $1",
            email.lower()
        )

    if user:
        # Update existing user with Auth0 info
        await execute(
            """UPDATE users SET
                 auth0_sub = COALESCE($1, auth0_sub),
                 auth_provider = COALESCE(NULLIF($2, ''), auth_provider),
                 avatar_url = COALESCE(NULLIF($3, ''), avatar_url),
                 name = COALESCE(NULLIF($4, ''), name),
                 last_login_at = NOW(),
                 email_verified = TRUE
               WHERE id = $5""",
            auth0_sub,
            "auth0",
            picture,
            name,
            user["id"]
        )
        user_id = str(user["id"])
        role = user["role"]
        user_name = user["name"] or name
        user_email = user["email"]
    else:
        # Create new user
        if not email:
            raise HTTPException(status_code=400, detail="Email is required for new user registration")

        new_user = await execute_returning(
            """INSERT INTO users (email, name, auth0_sub, auth_provider, avatar_url, email_verified, role, status)
               VALUES ($1, $2, $3, 'auth0', $4, TRUE, 'volunteer', 'active')
               RETURNING id, email, name, role""",
            email.lower(),
            name,
            auth0_sub,
            picture,
        )
        user_id = str(new_user["id"])
        role = new_user["role"]
        user_name = new_user["name"]
        user_email = new_user["email"]

    # Generate local JWT
    token = create_access_token({
        "sub": user_id,
        "email": user_email if user else email.lower(),
        "role": role,
    })

    # Audit log
    await execute(
        """INSERT INTO audit_logs (user_id, email, event_type, metadata)
           VALUES ($1::uuid, $2, 'login', $3::jsonb)""",
        user_id,
        user_email if user else email.lower(),
        json.dumps({"method": "auth0", "provider": auth0_sub.split("|")[0] if "|" in auth0_sub else "auth0"}),
    )

    return {
        "accessToken": token,
        "user": {
            "id": user_id,
            "email": user_email if user else email.lower(),
            "name": user_name if user else name,
            "role": role,
            "picture": picture,
        },
        "message": "Auth0 login successful",
    }


@router.post("/auth0-userinfo")
async def auth0_userinfo_callback(req: Auth0UserInfoRequest):
    """
    Alternative flow: Frontend sends Auth0 access_token + userinfo
    (for when the access token is opaque / not a JWT).
    Useful when Auth0 audience is not set (default Auth0 tokens are opaque).
    """
    # If user_info is provided directly (from Auth0 SPA SDK getUser())
    if req.user_info:
        user_info = req.user_info
    else:
        # Fetch from Auth0 userinfo endpoint
        try:
            userinfo_url = f"https://{settings.AUTH0_DOMAIN}/userinfo"
            http_req = urllib.request.Request(
                userinfo_url,
                headers={"Authorization": f"Bearer {req.access_token}"}
            )
            with urllib.request.urlopen(http_req, timeout=10) as resp:
                user_info = json.loads(resp.read())
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to fetch user info from Auth0: {e}")

    auth0_sub = user_info.get("sub", "")
    email = user_info.get("email", "")
    name = user_info.get("name") or user_info.get("nickname") or (email.split("@")[0] if email else "User")
    picture = user_info.get("picture", "")

    if not email:
        raise HTTPException(status_code=400, detail="Email not available from Auth0")

    # Same upsert logic
    user = None
    if auth0_sub:
        user = await fetch_one("SELECT * FROM users WHERE auth0_sub = $1", auth0_sub)
    if not user and email:
        user = await fetch_one("SELECT * FROM users WHERE email = $1", email.lower())

    if user:
        await execute(
            """UPDATE users SET
                 auth0_sub = COALESCE($1, auth0_sub),
                 auth_provider = 'auth0',
                 avatar_url = COALESCE(NULLIF($2, ''), avatar_url),
                 name = COALESCE(NULLIF($3, ''), name),
                 last_login_at = NOW(),
                 email_verified = TRUE
               WHERE id = $4""",
            auth0_sub, picture, name, user["id"]
        )
        user_id = str(user["id"])
        role = user["role"]
        user_name = user["name"] or name
        user_email = user["email"]
    else:
        new_user = await execute_returning(
            """INSERT INTO users (email, name, auth0_sub, auth_provider, avatar_url, email_verified, role, status)
               VALUES ($1, $2, $3, 'auth0', $4, TRUE, 'volunteer', 'active')
               RETURNING id, email, name, role""",
            email.lower(), name, auth0_sub, picture,
        )
        user_id = str(new_user["id"])
        role = new_user["role"]
        user_name = new_user["name"]
        user_email = new_user["email"]

    token = create_access_token({"sub": user_id, "email": user_email or email.lower(), "role": role})

    return {
        "accessToken": token,
        "user": {
            "id": user_id,
            "email": user_email or email.lower(),
            "name": user_name or name,
            "role": role,
            "picture": picture,
        },
        "message": "Auth0 login successful",
    }
