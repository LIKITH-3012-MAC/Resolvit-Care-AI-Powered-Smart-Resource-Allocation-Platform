"""
Authentication API — Signup, Login, JWT, OTP, Password Reset
All auth is handled by this FastAPI router (no external Node.js service).
"""

import os
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt, JWTError
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field

from backend.database import fetch_one, fetch_all, execute, execute_returning
from backend.config import settings

router = APIRouter()

# ──── JWT helpers ────

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(request: Request):
    """Dependency to extract and verify the current user from JWT.
    Supports both local JWTs (HS256) and Auth0 JWTs (RS256).
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    token = auth_header.split(" ", 1)[1]

    # 1. Try local JWT verification first
    payload = verify_token(token)
    if payload:
        user_id = payload.get("sub")
        user = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
        if user:
            return user

    # 2. Try Auth0 JWT verification
    if settings.AUTH0_DOMAIN:
        try:
            from backend.routes.auth0 import verify_auth0_token
            auth0_payload = verify_auth0_token(token)
            auth0_sub = auth0_payload.get("sub", "")
            email = auth0_payload.get("email", "")

            # Find user by auth0_sub or email
            user = None
            if auth0_sub:
                user = await fetch_one("SELECT * FROM users WHERE auth0_sub = $1", auth0_sub)
            if not user and email:
                user = await fetch_one("SELECT * FROM users WHERE email = $1", email.lower())
            if user:
                return user
        except Exception:
            pass  # Auth0 verification also failed

    raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_optional_user(request: Request):
    """Optional dependency to extract user from JWT.
    Returns None if token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ", 1)[1]

    # 1. Try local JWT
    payload = verify_token(token)
    if payload:
        user_id = payload.get("sub")
        user = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
        if user:
            return user

    # 2. Try Auth0 JWT
    if settings.AUTH0_DOMAIN:
        try:
            from backend.routes.auth0 import verify_auth0_token
            auth0_payload = verify_auth0_token(token)
            auth0_sub = auth0_payload.get("sub", "")
            email = auth0_payload.get("email", "")

            user = None
            if auth0_sub:
                user = await fetch_one("SELECT * FROM users WHERE auth0_sub = $1", auth0_sub)
            if not user and email:
                user = await fetch_one("SELECT * FROM users WHERE email = $1", email.lower())
            if user:
                return user
        except Exception:
            pass

    return None


# ──── Password helpers ────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ──── OTP helpers ────

def generate_otp() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode()).hexdigest()


# ──── Schemas ────

class SignupOtpRequest(BaseModel):
    email: str


class VerifyOtpRequest(BaseModel):
    email: str
    otp: str


class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str = Field(..., min_length=8)
    role: str = "volunteer"


class LoginRequest(BaseModel):
    email: str
    password: str


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    email: str
    password: str = Field(..., min_length=8)


# ──── Routes ────

@router.post("/request-signup-otp")
async def request_signup_otp(req: SignupOtpRequest):
    """Generate OTP for signup email verification."""
    email = req.email.strip().lower()

    # Check if email is already registered
    existing = await fetch_one("SELECT id FROM users WHERE email = $1", email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Please login instead.")

    # Check rate limit for OTP resends
    recent = await fetch_one(
        """SELECT resend_count FROM email_otps 
           WHERE email = $1 AND purpose = 'signup_verification' AND is_used = FALSE
           ORDER BY created_at DESC LIMIT 1""",
        email
    )
    resend_count = (recent["resend_count"] if recent else 0)

    if resend_count >= 5:
        raise HTTPException(status_code=429, detail="Too many OTP requests. Try again later.")

    # Generate OTP
    otp = generate_otp()
    otp_hashed = hash_otp(otp)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)

    # Invalidate previous OTPs for this email
    await execute(
        "UPDATE email_otps SET is_used = TRUE WHERE email = $1 AND purpose = 'signup_verification' AND is_used = FALSE",
        email
    )

    # Store OTP
    await execute(
        """INSERT INTO email_otps (email, otp_hash, purpose, resend_count, expires_at)
           VALUES ($1, $2, 'signup_verification', $3, $4)""",
        email, otp_hashed, resend_count + 1, expires_at
    )

    # In production, send via email service (Resend/SendGrid)
    # For now, log it and also return in dev mode for easy testing
    print(f"📧 OTP for {email}: {otp}")

    response = {
        "message": f"OTP sent to {email}",
        "resend_remaining": max(0, 5 - resend_count - 1),
        "expires_in_seconds": 600,
    }

    # In dev/debug mode, include OTP for testing convenience
    if settings.DEBUG:
        response["_dev_otp"] = otp

    return response


@router.post("/verify-signup-otp")
async def verify_signup_otp(req: VerifyOtpRequest):
    """Verify the OTP sent to email."""
    email = req.email.strip().lower()
    otp_hashed = hash_otp(req.otp.strip())

    record = await fetch_one(
        """SELECT * FROM email_otps 
           WHERE email = $1 AND otp_hash = $2 AND purpose = 'signup_verification' 
           AND is_used = FALSE AND expires_at > NOW()
           ORDER BY created_at DESC LIMIT 1""",
        email, otp_hashed
    )

    if not record:
        # Increment attempt counter
        await execute(
            """UPDATE email_otps SET verify_attempt_count = verify_attempt_count + 1 
               WHERE email = $1 AND purpose = 'signup_verification' AND is_used = FALSE""",
            email
        )
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    # Check if too many attempts
    if record["verify_attempt_count"] >= 5:
        raise HTTPException(status_code=429, detail="Too many verification attempts")

    # Mark as used
    await execute("UPDATE email_otps SET is_used = TRUE WHERE id = $1", record["id"])

    return {"message": "Email verified successfully", "verified": True}


@router.post("/register")
async def register(req: RegisterRequest):
    """Create a new user account (must verify OTP first)."""
    email = req.email.strip().lower()

    # Check if email already exists
    existing = await fetch_one("SELECT id FROM users WHERE email = $1", email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Validate role
    allowed_roles = ["volunteer", "reporter", "coordinator"]
    role = req.role if req.role in allowed_roles else "volunteer"

    # Hash password
    pw_hash = hash_password(req.password)

    # Create user
    user = await execute_returning(
        """INSERT INTO users (email, name, password_hash, role, email_verified, status)
           VALUES ($1, $2, $3, $4, TRUE, 'active')
           RETURNING id, email, name, role, created_at""",
        email, req.name.strip(), pw_hash, role
    )

    # Generate JWT
    token = create_access_token({"sub": str(user["id"]), "email": email, "role": role})

    return {
        "accessToken": token,
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
        "message": "Account created successfully"
    }


@router.post("/login")
async def login(req: LoginRequest):
    """Authenticate user with email and password."""
    email = req.email.strip().lower()

    # Find user
    user = await fetch_one(
        "SELECT id, email, name, password_hash, role, status FROM users WHERE email = $1",
        email
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is suspended or deactivated")

    if not user["password_hash"]:
        raise HTTPException(status_code=401, detail="Please use social login or reset your password")

    # Check password
    if not check_password(req.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Update last login
    await execute("UPDATE users SET last_login_at = NOW() WHERE id = $1", user["id"])

    # Generate JWT
    token = create_access_token({"sub": str(user["id"]), "email": email, "role": user["role"]})

    # Audit log
    await execute(
        """INSERT INTO audit_logs (user_id, email, event_type, metadata)
           VALUES ($1, $2, 'login', '{"method":"password"}'::jsonb)""",
        user["id"], email
    )

    return {
        "accessToken": token,
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    }


@router.post("/refresh")
async def refresh_token(request: Request):
    """Refresh the access token (use existing valid token)."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = auth_header.split(" ", 1)[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Issue fresh token
    new_token = create_access_token({
        "sub": payload["sub"],
        "email": payload.get("email"),
        "role": payload.get("role"),
    })

    return {"accessToken": new_token}


@router.post("/logout")
async def logout():
    """Logout endpoint (client-side token clearing)."""
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Request a password reset."""
    email = req.email.strip().lower()
    user = await fetch_one("SELECT id FROM users WHERE email = $1", email)

    # Always return success to prevent email enumeration
    response = {"message": "If this email is registered, a reset link has been sent."}

    if not user:
        return response

    # Generate reset token
    raw_token = secrets.token_urlsafe(32)
    token_hashed = hashlib.sha256(raw_token.encode()).hexdigest()
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)

    await execute(
        """INSERT INTO password_reset_tokens (user_id, email, token_hash, expires_at)
           VALUES ($1, $2, $3, $4)""",
        user["id"], email, token_hashed, expires_at
    )

    print(f"🔑 Reset token for {email}: {raw_token}")

    if settings.DEBUG:
        response["_dev_token"] = raw_token

    return response


@router.get("/validate-reset-token")
async def validate_reset_token(token: str, email: str):
    """Validate a password reset token."""
    token_hashed = hashlib.sha256(token.encode()).hexdigest()

    record = await fetch_one(
        """SELECT * FROM password_reset_tokens 
           WHERE email = $1 AND token_hash = $2 AND used_at IS NULL AND expires_at > NOW()""",
        email.strip().lower(), token_hashed
    )

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    return {"valid": True}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Reset password with a valid token."""
    email = req.email.strip().lower()
    token_hashed = hashlib.sha256(req.token.encode()).hexdigest()

    record = await fetch_one(
        """SELECT * FROM password_reset_tokens 
           WHERE email = $1 AND token_hash = $2 AND used_at IS NULL AND expires_at > NOW()""",
        email, token_hashed
    )

    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Update password
    pw_hash = hash_password(req.password)
    await execute("UPDATE users SET password_hash = $1 WHERE email = $2", pw_hash, email)

    # Mark token as used
    await execute("UPDATE password_reset_tokens SET used_at = NOW() WHERE id = $1", record["id"])

    return {"message": "Password reset successfully. You can now login with your new password."}


@router.get("/me")
async def get_me(user=Depends(get_current_user)):
    """Get current user profile."""
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "status": user["status"],
        "created_at": str(user["created_at"]),
    }
