import functools
from flask import request, jsonify, g
from backend.routes.auth import verify_token
from backend.config import settings
from backend.database import fetch_one

def token_required(f):
    """Flask decorator to protect routes with JWT (local or Auth0)."""
    @functools.wraps(f)
    async def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        # 1. Try local JWT
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
            user = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
            if user:
                g.current_user = user
                return await f(*args, **kwargs)

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
                    g.current_user = user
                    return await f(*args, **kwargs)
            except Exception:
                pass

        return jsonify({"error": "Invalid or expired token"}), 401
    
    return decorated

def optional_token(f):
    """Flask decorator for optional authentication."""
    @functools.wraps(f)
    async def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        
        if not token:
            g.current_user = None
            return await f(*args, **kwargs)
        
        # Try local JWT
        payload = verify_token(token)
        if payload:
            user_id = payload.get("sub")
            user = await fetch_one("SELECT * FROM users WHERE id = $1", user_id)
            if user:
                g.current_user = user
                return await f(*args, **kwargs)

        # Try Auth0 JWT
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
                    g.current_user = user
                    return await f(*args, **kwargs)
            except Exception:
                pass

        g.current_user = None
        return await f(*args, **kwargs)
    
    return decorated
