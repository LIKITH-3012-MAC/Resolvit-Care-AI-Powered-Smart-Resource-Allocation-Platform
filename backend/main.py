"""
Smart Resource Allocation — FastAPI Backend
Main application entry point with middleware, CORS, and static file serving.
"""

import os
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.config import settings
from backend.database import init_db, close_db, ensure_schema
from backend.routes import auth, auth0, reports, volunteers, tasks, resources, analytics, maps, ai_chat, ai_ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    await init_db()
    print("✅ Database connected")
    await ensure_schema()
    print("✅ Schema verified")
    yield
    await close_db()
    print("🔌 Database disconnected")


app = FastAPI(
    title="Smart Resource Allocation API",
    description="AI-powered volunteer coordination and social impact platform",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS middleware — allow frontend origins
origins = [o.strip().strip('"').strip("'") for o in settings.CORS_ORIGINS.replace("[", "").replace("]", "").split(",")]
origins = [o for o in origins if o]  # Remove empty strings

from backend.auth_decorator import auth_middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins + ["*"],  # Allow all during development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_auth_middleware(request: Request, call_next):
    return await auth_middleware(request, call_next)

# API routes
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(auth0.router, prefix="/auth", tags=["Auth0"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(volunteers.router, prefix="/api/volunteers", tags=["Volunteers"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["Tasks"])
app.include_router(resources.router, prefix="/api/resources", tags=["Resources"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(maps.router, prefix="/api/maps", tags=["Maps"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["AI Engine"])
app.include_router(ai_ingest.router, prefix="/api/ai", tags=["AI Ingestion"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "Smart Resource Allocation", "version": "2.0.0"}


# Serve frontend static files
root_dir = os.path.dirname(os.path.dirname(__file__))
frontend_dir = os.path.join(root_dir, "frontend")

if os.path.exists(frontend_dir):
    static_dir = os.path.join(frontend_dir, "static")
    assets_dir = os.path.join(frontend_dir, "assets")
    
    if os.path.exists(static_dir):
        # Mount subdirectories of static correctly
        for item in os.listdir(static_dir):
            item_path = os.path.join(static_dir, item)
            if os.path.isdir(item_path):
                app.mount(f"/{item}", StaticFiles(directory=item_path), name=item)
    
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")


# Catch-all route for HTML pages
@app.get("/{page}.html")
async def serve_page(page: str):
    templates_dir = os.path.join(frontend_dir, "templates")
    filepath = os.path.join(templates_dir, f"{page}.html")
    if os.path.exists(filepath):
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/")
async def serve_index():
    templates_dir = os.path.join(frontend_dir, "templates")
    filepath = os.path.join(templates_dir, "index.html")
    if os.path.exists(filepath):
        return FileResponse(filepath)
    return {"message": "Smart Resource Allocation API", "docs": "/docs"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc) if settings.DEBUG else "An error occurred"},
    )
