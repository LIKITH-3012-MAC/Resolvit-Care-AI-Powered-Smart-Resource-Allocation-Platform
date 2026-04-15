from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.db.session import get_db
from backend.app.models.user import Volunteer, Ngo
from backend.app.schemas.user import UserSchema # Simplified for now

router = APIRouter()

@router.get("/", response_model=List[Any])
async def read_volunteers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all registered volunteers.
    """
    query = select(Volunteer).offset(skip).limit(limit)
    result = await db.execute(query)
    volunteers = result.scalars().all()
    return volunteers

@router.get("/{id}", response_model=Any)
async def read_volunteer_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific volunteer profile.
    """
    query = select(Volunteer).where(Volunteer.id == id)
    result = await db.execute(query)
    volunteer = result.scalar_one_or_none()
    
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer not found")
        
    return volunteer
