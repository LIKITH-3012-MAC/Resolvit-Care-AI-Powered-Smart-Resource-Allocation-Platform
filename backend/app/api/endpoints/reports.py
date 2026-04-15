from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from sqlalchemy.orm import selectinload
from backend.app.db.session import get_db
from backend.app.models.report import CommunityReport, NeedCategory, PriorityScore
from backend.app.schemas.report import CommunityReportCreate, CommunityReportSchema, CommunityReportUpdate
from backend.app.models.user import User

router = APIRouter()

@router.post("/", response_model=CommunityReportSchema)
async def create_report(
    *,
    db: AsyncSession = Depends(get_db),
    report_in: CommunityReportCreate
) -> Any:
    """
    Create a new community report with AI-driven prioritization.
    """
    # 1. Initialize the report using standard lat/long (PostGIS fallback)
    report = CommunityReport(
        title=report_in.title,
        raw_text=report_in.raw_text,
        structured_data=report_in.structured_data,
        category_id=report_in.category_id,
        severity_level=report_in.severity_level,
        urgency_score=report_in.urgency_score,
        affected_count=report_in.affected_count,
        reporter_id=report_in.reporter_id,
        latitude=report_in.latitude,
        longitude=report_in.longitude,
        location_name=report_in.location_name,
        report_source=report_in.report_source,
        status="reported",
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    # 2. Trigger AI Prioritization Simulation
    priority = PriorityScore(
        report_id=report.id,
        score=report_in.urgency_score or 0.75,
        severity_weight=0.8,
        affected_weight=0.6,
        vulnerability_weight=0.9,
        time_sensitivity_weight=0.7,
        resource_gap_weight=0.5,
        explanation="AI prioritized this based on keyword extraction and affected population density."
    )
    db.add(priority)
    await db.commit()
    
    await db.refresh(report)
    return report

@router.get("/", response_model=List[CommunityReportSchema])
async def read_reports(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None
) -> Any:
    """
    Retrieve reports with optional status filtering.
    """
    query = select(CommunityReport).options(selectinload(CommunityReport.evidence)).offset(skip).limit(limit)
    if status:
        query = query.where(CommunityReport.status == status)
    
    result = await db.execute(query)
    reports = result.scalars().all()
    return reports

@router.get("/{id}", response_model=CommunityReportSchema)
async def read_report_by_id(
    id: int,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get a specific report by ID.
    """
    query = select(CommunityReport).options(selectinload(CommunityReport.evidence)).where(CommunityReport.id == id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return report
