"""
Volunteers API — CRUD + matching
"""

from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from backend.database import fetch_all, fetch_one, execute_returning, execute
from backend.models import VolunteerCreate, VolunteerUpdate
from ai.matcher import find_best_matches

router = APIRouter()


@router.get("")
async def list_volunteers(
    availability: str = Query(None),
    skill: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
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
    return row


@router.post("")
async def create_volunteer(vol: VolunteerCreate):
    """Register a new volunteer."""
    row = await execute_returning(
        """INSERT INTO volunteers
           (user_id, skill_tags, languages, latitude, longitude,
            travel_radius_km, transport_access, gender, preferred_causes)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
           RETURNING *""",
        str(vol.user_id), vol.skill_tags, vol.languages,
        vol.latitude, vol.longitude, vol.travel_radius_km,
        vol.transport_access, vol.gender, vol.preferred_causes
    )
    return {"data": row, "message": "Volunteer registered"}


@router.patch("/{volunteer_id}")
async def update_volunteer(volunteer_id: str, update: VolunteerUpdate):
    """Update volunteer profile."""
    fields = []
    params = []
    idx = 1

    update_dict = update.model_dump(exclude_none=True)
    for key, val in update_dict.items():
        fields.append(f"{key} = ${idx}")
        params.append(val)
        idx += 1

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(volunteer_id)
    query = f"UPDATE volunteers SET {', '.join(fields)} WHERE id = ${idx} RETURNING *"
    row = await execute_returning(query, *params)

    if not row:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    return {"data": row, "message": "Volunteer updated"}


@router.post("/match")
async def match_volunteers(
    task_type: str,
    latitude: float,
    longitude: float,
    required_language: str = "",
    top_n: int = 5,
):
    """Find best volunteer matches for a task using AI matching engine."""
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
        "required_language": required_language,
    }

    # Convert DB rows to match format
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

    matches = find_best_matches(vol_dicts, task_info, top_n=top_n)
    return {"matches": matches, "task": task_info}
