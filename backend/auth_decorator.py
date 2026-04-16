"""
Authentication Security Layer — FastAPI version.
Provides middleware to parse JWT/Auth0 tokens and dependencies for route protection.
"""

from fastapi import Request, HTTPException, Depends
from backend.routes.auth import verify_token
from backend.config import settings
from backend.database import fetch_one

async def get_current_user_from_request(request: Request):
    """
    Core authentication logic: extracts token, verifies it, and fetches user.
    Used by middleware and direct dependencies.
    """
    auth_header = request.headers.get("Authorization", "")
    token = None
    
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
    
    if not token:
        return None
    
    # 1. Try local JWT
    try:
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
            user = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
            if user:
                return user
    except Exception:
        pass

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

async def auth_middleware(request: Request, call_next):
    """
    FastAPI middleware to populate request.state.user.
    Does not block request if auth fails.
    """
    user = await get_current_user_from_request(request)
    request.state.user = user
    response = await call_next(request)
    return response

# Dependencies for protecting routes

async def token_required(request: Request):
    """Dependency: Ensures user is authenticated."""
    if not hasattr(request.state, "user") or request.state.user is None:
        user = await get_current_user_from_request(request)
        if not user:
            raise HTTPException(status_code=401, detail="Authentication required")
        request.state.user = user
    return request.state.user

async def optional_token(request: Request):
    """Dependency: Populates user if present, else None."""
    if not hasattr(request.state, "user"):
        request.state.user = await get_current_user_from_request(request)
    return request.state.user
