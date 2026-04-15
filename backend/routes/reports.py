"""
Reports API — CRUD + AI classification + priority scoring
"""

import json
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query
from backend.database import fetch_all, fetch_one, execute_returning, execute
from backend.models import ReportCreate, ReportUpdate
from ai import classify_report
from ai.priority import calculate_priority

router = APIRouter()


@router.get("")
async def list_reports(
    category: str = Query(None),
    priority: str = Query(None),
    status: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort: str = Query("created_at"),
    order: str = Query("desc"),
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

    # Convert UUID and datetime to string for JSON
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)

    return {"data": rows, "total": total, "limit": limit, "offset": offset}


@router.get("/{report_id}")
async def get_report(report_id: str):
    """Get a single report with full details."""
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
    return row


@router.post("")
async def create_report(report: ReportCreate):
    """Submit a new community report with AI classification and scoring."""
    # AI classification
    classification = classify_report(report.description, report.title)
    category = classification.get("primary", report.category)

    # AI priority scoring
    priority_input = {
        "severity": report.severity,
        "people_affected": report.people_affected,
        "vulnerable_group": report.vulnerable_group or "",
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
        report.title, report.description, category,
        report.severity, priority["score"], priority["level"],
        report.people_affected, report.vulnerable_group,
        report.source_type, report.latitude, report.longitude,
        report.address_text, report.images or [],
        json.dumps(classification), priority["explanation"]
    )

    return {
        "data": row,
        "ai_classification": classification,
        "ai_priority": priority,
        "message": "Report created successfully"
    }


@router.patch("/{report_id}")
async def update_report(report_id: str, update: ReportUpdate):
    """Update a report. Recalculates priority if severity/category changes."""
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

    params.append(report_id)
    query = f"UPDATE community_reports SET {', '.join(fields)} WHERE id = ${idx} RETURNING *"
    row = await execute_returning(query, *params)

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"data": row, "message": "Report updated"}


@router.post("/{report_id}/classify")
async def reclassify_report(report_id: str):
    """Re-run AI classification on a report."""
    row = await fetch_one("SELECT * FROM community_reports WHERE id = $1", report_id)
    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    classification = classify_report(row["description"], row["title"])
    priority_input = {
        "severity": row["severity"],
        "people_affected": row["people_affected"],
        "vulnerable_group": row.get("vulnerable_group", ""),
        "category": classification["primary"],
        "verification_status": row["verification_status"],
        "created_at": str(row["created_at"]),
    }
    priority = calculate_priority(priority_input)

    await execute(
        """UPDATE community_reports
           SET category = $1, urgency_score = $2, priority_level = $3,
               ai_classification = $4::jsonb, ai_priority_explanation = $5
           WHERE id = $6""",
        classification["primary"], priority["score"], priority["level"],
        json.dumps(classification), priority["explanation"], report_id
    )

    return {
        "classification": classification,
        "priority": priority,
        "message": "Report reclassified successfully"
    }


@router.delete("/{report_id}")
async def delete_report(report_id: str):
    """Delete a report."""
    result = await execute("DELETE FROM community_reports WHERE id = $1", report_id)
    return {"message": "Report deleted"}
