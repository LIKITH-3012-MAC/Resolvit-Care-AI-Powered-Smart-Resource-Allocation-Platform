"""
Auth0 Social Login — Flask Blueprint version.
Verify Auth0 JWT, sync user to PostgreSQL, return local JWT.
"""

import json
import urllib.request
from datetime import datetime, timezone
import jwt as pyjwt
from flask import Blueprint, request, jsonify, abort
from backend.config import settings
from backend.database import fetch_one, execute, execute_returning
from backend.routes.auth import create_access_token

auth0_bp = Blueprint('auth0_bp', __name__)

# ──── Auth0 JWKS cache ────
_jwks_cache = {"keys": [], "fetched_at": None}

def _fetch_jwks():
    global _jwks_cache
    now = datetime.now(timezone.utc)
    if _jwks_cache["fetched_at"] and (now - _jwks_cache["fetched_at"]).total_seconds() < 3600:
        return _jwks_cache["keys"]

    if not settings.AUTH0_DOMAIN:
        abort(500, description="AUTH0_DOMAIN not configured")

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
        return _jwks_cache["keys"] or abort(500, description="Failed to fetch Auth0 public keys")

def verify_auth0_token(token: str) -> dict:
    jwks_keys = _fetch_jwks()
    try:
        unverified_header = pyjwt.get_unverified_header(token)
    except pyjwt.exceptions.DecodeError:
        abort(401, description="Invalid token format")

    kid = unverified_header.get("kid")
    rsa_key = next((key for key in jwks_keys if key.get("kid") == kid), None)

    if not rsa_key:
        _jwks_cache["fetched_at"] = None
        jwks_keys = _fetch_jwks()
        rsa_key = next((key for key in jwks_keys if key.get("kid") == kid), None)

    if not rsa_key:
        abort(401, description="Unable to find matching Auth0 signing key")

    try:
        from jwt.algorithms import RSAAlgorithm
        public_key = RSAAlgorithm.from_jwk(json.dumps(rsa_key))
        payload = pyjwt.decode(
            token, public_key, algorithms=["RS256"],
            audience=settings.AUTH0_AUDIENCE or None,
            issuer=f"https://{settings.AUTH0_DOMAIN}/",
            options={"verify_aud": bool(settings.AUTH0_AUDIENCE), "verify_iss": True, "verify_exp": True}
        )
        return payload
    except Exception as e:
        abort(401, description=f"Auth0 token verification failed: {e}")

@auth0_bp.route("/auth0-callback", methods=["POST"])
async def auth0_callback():
    data = request.json
    if not data or "token" not in data:
        return jsonify({"error": "Auth0 token required"}), 400
        
    payload = verify_auth0_token(data["token"])
    auth0_sub = payload.get("sub", "")
    email = payload.get("email") or payload.get(f"https://{settings.AUTH0_DOMAIN}/email") or ""
    name = payload.get("name") or payload.get("nickname") or (email.split("@")[0] if email else "User")
    picture = payload.get("picture", "")

    user = await fetch_one("SELECT * FROM users WHERE auth0_sub = $1", auth0_sub)
    if not user and email:
        user = await fetch_one("SELECT * FROM users WHERE email = $1", email.lower())

    if user:
        await execute(
            """UPDATE users SET auth0_sub = $1, auth_provider = 'auth0',
               avatar_url = $2, name = $3, last_login_at = NOW(), email_verified = TRUE
               WHERE id = $4""", auth0_sub, picture, name, user["id"]
        )
        user_id, role, user_email = str(user["id"]), user["role"], user["email"]
    else:
        new_user = await execute_returning(
            """INSERT INTO users (email, name, auth0_sub, auth_provider, avatar_url, email_verified, role, status)
               VALUES ($1, $2, $3, 'auth0', $4, TRUE, 'volunteer', 'active')
               RETURNING id, email, name, role""", email.lower(), name, auth0_sub, picture
        )
        user_id, role, user_email = str(new_user["id"]), new_user["role"], new_user["email"]

    token = create_access_token({"sub": user_id, "email": user_email, "role": role})
    return jsonify({
        "accessToken": token,
        "user": {"id": user_id, "email": user_email, "name": name, "role": role, "picture": picture},
        "message": "Auth0 login successful"
    })
