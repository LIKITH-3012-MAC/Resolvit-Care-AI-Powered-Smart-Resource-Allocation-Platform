"""
Smart Resource Allocation — Configuration
Loads environment variables with sensible defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:password@127.0.0.1:5432/smart_resource")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://127.0.0.1:8000,http://127.0.0.1:3000,http://localhost:8000,http://localhost:3000")
    DEBUG: bool = os.getenv("APP_DEBUG", os.getenv("DEBUG", "true")).lower() in ("true", "1", "yes")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", os.getenv("PORT", "8000")))

    # Auth0
    AUTH0_DOMAIN: str = os.getenv("AUTH0_DOMAIN", "")
    AUTH0_AUDIENCE: str = os.getenv("AUTH0_AUDIENCE", "")
    AUTH0_CLIENT_ID: str = os.getenv("AUTH0_CLIENT_ID", "")


settings = Settings()
