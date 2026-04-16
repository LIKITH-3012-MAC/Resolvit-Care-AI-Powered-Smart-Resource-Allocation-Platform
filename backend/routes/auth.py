"""
Authentication Flask Blueprint — Signup, Login, JWT, OTP, Password Reset
Converted from FastAPI to Flask for unified architecture.
"""

import os
import uuid
import secrets
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
from flask import Blueprint, request, jsonify, abort
from jose import jwt, JWTError

from backend.database import fetch_one, fetch_all, execute, execute_returning
from backend.config import settings

auth_bp = Blueprint('auth_bp', __name__)

# ──── JWT helpers ────

ALGORITHM = "HS256"
TOKEN_EXPIRE_HOURS = int(os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24"))


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=TOKEN_EXPIRE_HOURS))
    to_encode.update({"exp": expire.timestamp() if isinstance(expire, datetime) else expire})
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

@auth_bp.route("/request-signup-otp", methods=["POST"])
async def request_signup_otp():
    """Generate OTP for signup email verification."""
    data = request.json
    if not data or "email" not in data:
        return jsonify({"error": "Email is required"}), 400
        
    email = data["email"].strip().lower()

    # Check if email is already registered
    existing = await fetch_one("SELECT id FROM users WHERE email = $1", email)
    if existing:
        return jsonify({"error": "Email already registered. Please login instead."}), 400

    # Check rate limit for OTP resends
    recent = await fetch_one(
        """SELECT resend_count FROM email_otps 
           WHERE email = $1 AND purpose = 'signup_verification' AND is_used = FALSE
           ORDER BY created_at DESC LIMIT 1""",
        email
    )
    resend_count = (recent["resend_count"] if recent else 0)

    if resend_count >= 5:
        return jsonify({"error": "Too many OTP requests. Try again later."}), 429

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

    return jsonify(response_data)


@auth_bp.route("/verify-signup-otp", methods=["POST"])
async def verify_signup_otp():
    """Verify the OTP sent to email."""
    data = request.json
    if not data or "email" not in data or "otp" not in data:
        return jsonify({"error": "Email and OTP are required"}), 400
        
    email = data["email"].strip().lower()
    otp_hashed = hash_otp(data["otp"].strip())

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
        return jsonify({"error": "Invalid or expired OTP"}), 400

    if record["verify_attempt_count"] >= 5:
        return jsonify({"error": "Too many verification attempts"}), 429

    await execute("UPDATE email_otps SET is_used = TRUE WHERE id = $1", record["id"])
    return jsonify({"message": "Email verified successfully", "verified": True})


@auth_bp.route("/register", methods=["POST"])
async def register():
    """Create a new user account."""
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400
        
    email = data["email"].strip().lower()
    name = data.get("name", "").strip()
    password = data["password"]
    
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing = await fetch_one("SELECT id FROM users WHERE email = $1", email)
    if existing:
        return jsonify({"error": "Email already registered"}), 400

    allowed_roles = ["volunteer", "reporter", "coordinator"]
    role = data.get("role", "volunteer")
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

    return jsonify({
        "accessToken": token,
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        },
        "message": "Account created successfully"
    })


@auth_bp.route("/login", methods=["POST"])
async def login():
    """Authenticate user."""
    data = request.json
    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400
        
    email = data["email"].strip().lower()
    password = data["password"]

    user = await fetch_one(
        "SELECT id, email, name, password_hash, role, status FROM users WHERE email = $1",
        email
    )

    if not user:
        return jsonify({"error": "Invalid email or password"}), 401
    if user["status"] != "active":
        return jsonify({"error": "Account is suspended"}), 403
    if not user["password_hash"]:
        return jsonify({"error": "Use social login"}), 401

    if not check_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid email or password"}), 401

    await execute("UPDATE users SET last_login_at = NOW() WHERE id = $1", user["id"])
    token = create_access_token({"sub": str(user["id"]), "email": email, "role": user["role"]})

    await execute(
        """INSERT INTO audit_logs (user_id, email, event_type, metadata)
           VALUES ($1, $2, 'login', '{"method":"password"}'::jsonb)""",
        user["id"], email
    )

    return jsonify({
        "accessToken": token,
        "user": {
            "id": str(user["id"]),
            "email": user["email"],
            "name": user["name"],
            "role": user["role"],
        }
    })

@auth_bp.route("/me", methods=["GET"])
async def get_me():
    """Get current user profile."""
    # This will use the g.current_user set by the decorator in app.py or registered manually
    # For now, we'll keep it simple
    from backend.auth_decorator import token_required
    return await get_me_logic()

async def get_me_logic():
    # Helper to be called by the decorated route
    from flask import g
    user = g.current_user
    return jsonify({
        "id": str(user["id"]),
        "email": user["email"],
        "name": user["name"],
        "role": user["role"],
        "status": user["status"]
    })
