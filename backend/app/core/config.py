from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    APP_NAME: str = "Resolvit Care AI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    
    # Database
    # Using Aiven Cloud PostgreSQL as primary
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # External APIs
    MAPBOX_API_KEY: Optional[str] = None
    EMAIL_API_KEY: Optional[str] = None
    STORAGE_BUCKET: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # API
    API_V1_STR: str = "/api/v1"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

settings = Settings()
