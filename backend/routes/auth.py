"""
Authentication FastAPI Router — Signup, Login, JWT, OTP, Password Reset
Converted back from Flask to FastAPI for unified architecture.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Body, Request, Depends
from jose import jwt, JWTError

from backend.database import fetch_one, execute, execute_returning
from backend.config import settings

router = APIRouter()

# ──── JWT helpers ────

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire.timestamp()})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
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


# ──── Routes ────

@router.post("/request-signup-otp")
async def request_signup_otp(payload: dict = Body(...)):
    """Generate OTP for signup email verification."""
    email = payload.get("email", "").strip().lower()
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")

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

    print(f"📧 OTP for {email}: {otp}")

    response_data = {
        "message": f"OTP sent to {email}",
        "resend_remaining": max(0, 5 - resend_count - 1),
        "expires_in_seconds": 600,
    }

    if settings.DEBUG:
        response_data["_dev_otp"] = otp

    return response_data


@router.post("/verify-signup-otp")
async def verify_signup_otp(payload: dict = Body(...)):
    """Verify the OTP sent to email."""
    email = payload.get("email", "").strip().lower()
    otp = payload.get("otp", "").strip()
    
    if not email or not otp:
        raise HTTPException(status_code=400, detail="Email and OTP are required")
        
    otp_hashed = hash_otp(otp)

    record = await fetch_one(
        """SELECT * FROM email_otps 
           WHERE email = $1 AND otp_hash = $2 AND purpose = 'signup_verification' 
           AND is_used = FALSE AND expires_at > NOW()
           ORDER BY created_at DESC LIMIT 1""",
        email, otp_hashed
    )

    if not record:
        await execute(
            """UPDATE email_otps SET verify_attempt_count = verify_attempt_count + 1 
               WHERE email = $1 AND purpose = 'signup_verification' AND is_used = FALSE""",
            email
        )
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    if record["verify_attempt_count"] >= 5:
        raise HTTPException(status_code=429, detail="Too many verification attempts")

    await execute("UPDATE email_otps SET is_used = TRUE WHERE id = $1", record["id"])
    return {"message": "Email verified successfully", "verified": True}


@router.post("/register")
async def register(payload: dict = Body(...)):
    """Create a new user account."""
    email = payload.get("email", "").strip().lower()
    name = payload.get("name", "").strip()
    password = payload.get("password", "")
    role = payload.get("role", "volunteer")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
        
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    existing = await fetch_one("SELECT id FROM users WHERE email = $1", email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    allowed_roles = ["volunteer", "reporter", "coordinator"]
    if role not in allowed_roles:
        role = "volunteer"

    pw_hash = hash_password(password)

    user = await execute_returning(
        """INSERT INTO users (email, name, password_hash, role, email_verified, status)
           VALUES ($1, $2, $3, $4, TRUE, 'active')
           RETURNING id, email, name, role""",
        email, name, pw_hash, role
    )

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
async def login(payload: dict = Body(...)):
    """Authenticate user."""
    email = payload.get("email", "").strip().lower()
    password = payload.get("password", "")

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    user = await fetch_one(
        "SELECT id, email, name, password_hash, role, status FROM users WHERE email = $1",
        email
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user["status"] != "active":
        raise HTTPException(status_code=403, detail="Account is suspended")
    if not user["password_hash"]:
        raise HTTPException(status_code=401, detail="Use social login")

    if not check_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await execute("UPDATE users SET last_login_at = NOW() WHERE id = $1", user["id"])
    token = create_access_token({"sub": str(user["id"]), "email": email, "role": user["role"]})

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

@router.get("/me")
async def get_me(request: Request):
    """Get current user profile."""
    # Note: In FastAPI, we usually use Depends() for this.
    # We will implement the dependency in auth_decorator.py
    # But for now, we'll keep the logic here or wait for the decorator update.
    user = getattr(request.state, "user", None)
    if not user:
         raise HTTPException(status_code=401, detail="Not authenticated")
         
    return {
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "status": user["status"]
    }
