from fastapi import APIRouter
from backend.app.api.endpoints import reports, volunteers, tasks, auth, users, ngos

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ngos.router, prefix="/ngos", tags=["ngos"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(volunteers.router, prefix="/volunteers", tags=["volunteers"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
