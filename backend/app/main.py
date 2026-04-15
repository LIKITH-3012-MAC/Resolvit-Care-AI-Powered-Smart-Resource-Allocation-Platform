from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.api import api_router

def get_application() -> FastAPI:
    _app = FastAPI(
        title=settings.APP_NAME,
        description="Elite System for Humanitarian Intelligence & Resource Orchestration",
        version="2.0.0",
        debug=settings.APP_DEBUG,
    )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    _app.include_router(api_router, prefix="/api")

    @_app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}

    return _app

app = get_application()
