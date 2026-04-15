from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.api import deps
from backend.app.models.user import User, UserRole
from backend.app.models.report import CommunityReport
from backend.app.models.user import Ngo
from backend.app.schemas.user import NgoSchema, NgoCreate
from sqlalchemy import select

router = APIRouter()

@router.post("/", response_model=NgoSchema)
async def create_ngo(
    *,
    db: AsyncSession = Depends(deps.get_db),
    ngo_in: NgoCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Register a new NGO.
    """
    if current_user.role not in [UserRole.ADMIN, UserRole.NGO_ADMIN]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    db_obj = Ngo(
        name=ngo_in.name,
        description=ngo_in.description,
        website=ngo_in.website,
        admin_id=current_user.id
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

@router.get("/", response_model=List[NgoSchema])
async def read_ngos(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve NGOs.
    """
    result = await db.execute(select(Ngo).offset(skip).limit(limit))
    return result.scalars().all()
