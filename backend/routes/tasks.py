"""
Tasks API — Lifecycle management + assignment
FastAPI Router version.
"""

from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query, Body, Request
from backend.database import fetch_all, fetch_one, execute_returning, execute

router = APIRouter()

@router.get("")
async def list_tasks(
    status: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    volunteer_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0)
):
    """List tasks with filtering."""
    conditions = []
    params = []
    idx = 1

    if status:
        conditions.append(f"t.status = ${idx}")
        params.append(status)
        idx += 1
    if priority:
        conditions.append(f"t.priority_level = ${idx}")
        params.append(priority)
        idx += 1
    if volunteer_id:
        conditions.append(f"t.assigned_volunteer_id = ${idx}")
        params.append(volunteer_id)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT t.*, cr.title as report_title, cr.category as report_category,
               u.name as volunteer_name
        FROM tasks t
        LEFT JOIN community_reports cr ON t.report_id = cr.id
        LEFT JOIN volunteers v ON t.assigned_volunteer_id = v.id
        LEFT JOIN users u ON v.user_id = u.id
        {where}
        ORDER BY t.priority_score DESC, t.created_at DESC
        LIMIT ${idx} OFFSET ${idx + 1}
    """
    params.extend([limit, offset])

    rows = await fetch_all(query, *params)
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
    return {"data": rows, "total": len(rows)}


@router.get("/{task_id}")
async def get_task(task_id: str):
    """Get task details."""
    row = await fetch_one(
        """SELECT t.*, cr.title as report_title, cr.description as report_description,
                  cr.category, cr.severity, cr.people_affected,
                  u.name as volunteer_name, u.email as volunteer_email
           FROM tasks t
           LEFT JOIN community_reports cr ON t.report_id = cr.id
           LEFT JOIN volunteers v ON t.assigned_volunteer_id = v.id
           LEFT JOIN users u ON v.user_id = u.id
           WHERE t.id = $1""",
        task_id
    )
    if not row:
        raise HTTPException(status_code=404, detail="Task not found")
        
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
    return row


@router.post("")
async def create_task(payload: dict = Body(...)):
    """Create a new task from a report."""
    report_id = payload.get("report_id")
    if not report_id:
        raise HTTPException(status_code=400, detail="report_id required")
        
    report = await fetch_one(
        "SELECT urgency_score, priority_level FROM community_reports WHERE id = $1",
        str(report_id)
    )
    
    priority_score = report["urgency_score"] if report else 0
    priority_level = payload.get("priority_level") or (report["priority_level"] if report else "medium")

    row = await execute_returning(
        """INSERT INTO tasks
           (report_id, task_type, title, description, priority_level,
            priority_score, deadline, resources_needed)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
           RETURNING *""",
        str(report_id), payload.get("task_type", "Resolution"), payload.get("title", "New Task"),
        payload.get("description", ""), priority_level, priority_score,
        payload.get("deadline"), payload.get("resources_needed", "[]")
    )
    return {"data": row, "message": "Task created"}


@router.post("/{task_id}/assign/{volunteer_id}")
async def assign_task(task_id: str, volunteer_id: str):
    """Assign a volunteer to a task."""
    vol = await fetch_one("SELECT * FROM volunteers WHERE id = $1", volunteer_id)
    if not vol:
        raise HTTPException(status_code=404, detail="Volunteer not found")

    row = await execute_returning(
        """UPDATE tasks
           SET assigned_volunteer_id = $1, status = 'assigned'
           WHERE id = $2
           RETURNING *""",
        volunteer_id, task_id
    )

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    await execute(
        "UPDATE volunteers SET current_workload = current_workload + 1 WHERE id = $1",
        volunteer_id
    )

    return {"data": row, "message": "Volunteer assigned to task"}
