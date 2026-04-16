"""
Volunteers API — CRUD + matching
FastAPI Router version.
"""

from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body, Request
from backend.database import fetch_all, fetch_one, execute_returning, execute
from ai.matcher import find_best_matches

router = APIRouter()

@router.get("")
async def list_volunteers(
    availability: Optional[str] = Query(None),
    skill: Optional[str] = Query(None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    """List volunteers with filtering."""
    conditions = []
    params = []
    idx = 1

    if availability:
        conditions.append(f"v.availability = ${idx}")
        params.append(availability)
        idx += 1
    if skill:
        conditions.append(f"${idx} = ANY(v.skill_tags)")
        params.append(skill)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT v.*, u.name, u.email, u.phone
        FROM volunteers v
        JOIN users u ON v.user_id = u.id
        {where}
        ORDER BY v.reliability_score DESC
        LIMIT ${idx} OFFSET ${idx + 1}
    """
    params.extend([limit, offset])

    rows = await fetch_all(query, *params)
    
    # Convert UUIDs
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
                
    return {"data": rows, "total": len(rows)}


@router.get("/{volunteer_id}")
async def get_volunteer(volunteer_id: str):
    """Get volunteer details."""
    row = await fetch_one(
        """SELECT v.*, u.name, u.email, u.phone
           FROM volunteers v
           JOIN users u ON v.user_id = u.id
           WHERE v.id = $1""",
        volunteer_id
    )
    if not row:
         raise HTTPException(status_code=404, detail="Volunteer not found")
        
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
    return row


@router.post("")
async def create_volunteer(payload: dict = Body(...)):
    """Register a new volunteer."""
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id required")
        
    row = await execute_returning(
        """INSERT INTO volunteers
           (user_id, skill_tags, languages, latitude, longitude,
            travel_radius_km, transport_access, gender, preferred_causes)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
           RETURNING *""",
        str(user_id), payload.get("skill_tags", []), payload.get("languages", []),
        payload.get("latitude"), payload.get("longitude"), payload.get("travel_radius_km", 10),
        payload.get("transport_access", "none"), payload.get("gender"), payload.get("preferred_causes", [])
    )
    return {"data": row, "message": "Volunteer registered"}


@router.post("/match")
async def match_volunteers(payload: dict = Body(...)):
    """Find best volunteer matches for a task using AI matching engine."""
    task_type = payload.get("task_type")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    
    volunteers = await fetch_all(
        """SELECT v.*, u.name
           FROM volunteers v
           JOIN users u ON v.user_id = u.id
           WHERE v.availability != 'offline'"""
    )

    task_info = {
        "task_type": task_type,
        "latitude": latitude,
        "longitude": longitude,
        "required_language": payload.get("required_language", ""),
    }

    vol_dicts = []
    for v in volunteers:
        vol_dicts.append({
            "user_id": str(v["user_id"]),
            "name": v.get("name", "Unknown"),
            "skill_tags": v.get("skill_tags", []),
            "languages": v.get("languages", []),
            "availability": v.get("availability", "offline"),
            "latitude": v.get("latitude"),
            "longitude": v.get("longitude"),
            "reliability_score": v.get("reliability_score", 50),
            "current_workload": v.get("current_workload", 0),
            "travel_radius_km": v.get("travel_radius_km", 10),
            "gender": v.get("gender"),
            "total_tasks_completed": v.get("total_tasks_completed", 0),
        })

    matches = find_best_matches(vol_dicts, task_info, top_n=payload.get("top_n", 5))
    return {"matches": matches, "task": task_info}
