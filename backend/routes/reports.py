"""
Reports API — CRUD + AI classification + priority scoring
FastAPI Router version.
"""

import json
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body, Request
from backend.database import fetch_all, fetch_one, execute_returning, execute
from ai import classify_report
from ai.priority import calculate_priority

router = APIRouter()

@router.get("")
async def list_reports(
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at"),
    order: str = Query("desc")
):
    """List all community reports with filtering."""
    conditions = []
    params = []
    idx = 1

    if category:
        conditions.append(f"cr.category = ${idx}")
        params.append(category)
        idx += 1
    if priority:
        conditions.append(f"cr.priority_level = ${idx}")
        params.append(priority)
        idx += 1
    if status:
        conditions.append(f"cr.verification_status = ${idx}")
        params.append(status)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    allowed_sorts = {"created_at", "urgency_score", "severity", "people_affected", "priority_level"}
    sort_col = sort if sort in allowed_sorts else "created_at"
    sort_order = "ASC" if order.lower() == "asc" else "DESC"

    query = f"""
        SELECT cr.*, u.name as reporter_name,
               l.name as location_name, l.district, l.ward
        FROM community_reports cr
        LEFT JOIN users u ON cr.reporter_id = u.id
        LEFT JOIN locations l ON cr.location_id = l.id
        {where}
        ORDER BY cr.{sort_col} {sort_order}
        LIMIT ${idx} OFFSET ${idx + 1}
    """
    params.extend([limit, offset])

    rows = await fetch_all(query, *params)

    count_query = f"SELECT COUNT(*) as total FROM community_reports cr {where}"
    count_row = await fetch_one(count_query, *params[:-2]) if params[:-2] else await fetch_one(count_query)
    total = count_row["total"] if count_row else 0

    # Convert UUID and datetime to string/serializable for JSON
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)

    return {"data": rows, "total": total, "limit": limit, "offset": offset}


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Get a single report."""
    row = await fetch_one(
        """SELECT cr.*, u.name as reporter_name, u.email as reporter_email,
                  l.name as location_name, l.district, l.ward, l.latitude as loc_lat, l.longitude as loc_lon
           FROM community_reports cr
           LEFT JOIN users u ON cr.reporter_id = u.id
           LEFT JOIN locations l ON cr.location_id = l.id
           WHERE cr.id = $1""",
        report_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Convert types
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
            
    return row


@router.post("")
async def create_report(payload: dict = Body(...)):
    """Submit a new report."""
    title = payload.get("title")
    description = payload.get("description")
    
    if not title or not description:
        raise HTTPException(status_code=400, detail="Title and Description required")

    # AI classification
    classification = classify_report(description, title)
    category = classification.get("primary", payload.get("category", "General"))

    # AI priority scoring
    priority_input = {
        "severity": payload.get("severity", 5),
        "people_affected": payload.get("people_affected", 1),
        "vulnerable_group": payload.get("vulnerable_group", ""),
        "category": category,
        "verification_status": "pending",
    }
    priority = calculate_priority(priority_input)

    row = await execute_returning(
        """INSERT INTO community_reports
           (title, description, category, severity, urgency_score, priority_level,
            people_affected, vulnerable_group, source_type, latitude, longitude,
            address_text, images, ai_classification, ai_priority_explanation)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14::jsonb, $15)
           RETURNING *""",
        title, description, category,
        payload.get("severity", 5), priority["score"], priority["level"],
        payload.get("people_affected", 1), payload.get("vulnerable_group", ""),
        payload.get("source_type", "web_form"), payload.get("latitude"), payload.get("longitude"),
        payload.get("address_text", ""), payload.get("images", []),
        json.dumps(classification), priority["explanation"]
    )

    # Convert UUID
    if row and "id" in row:
        row["id"] = str(row["id"])

    return {
        "data": row,
        "ai_classification": classification,
        "ai_priority": priority,
        "message": "Report created successfully"
    }
