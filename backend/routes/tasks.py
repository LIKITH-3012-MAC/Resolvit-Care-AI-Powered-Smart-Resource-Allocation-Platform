"""
Tasks API — Lifecycle management + assignment
"""

from fastapi import APIRouter, HTTPException, Query
from backend.database import fetch_all, fetch_one, execute_returning, execute
from backend.models import TaskCreate, TaskUpdate

router = APIRouter()


@router.get("")
async def list_tasks(
    status: str = Query(None),
    priority: str = Query(None),
    volunteer_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
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
    return row


@router.post("")
async def create_task(task: TaskCreate):
    """Create a new task from a report."""
    # Get report priority for task
    report = await fetch_one(
        "SELECT urgency_score, priority_level FROM community_reports WHERE id = $1",
        str(task.report_id)
    )
    
    priority_score = report["urgency_score"] if report else 0
    priority_level = task.priority_level or (report["priority_level"] if report else "medium")

    row = await execute_returning(
        """INSERT INTO tasks
           (report_id, task_type, title, description, priority_level,
            priority_score, deadline, resources_needed)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
           RETURNING *""",
        str(task.report_id), task.task_type, task.title,
        task.description, priority_level, priority_score,
        task.deadline, "[]"
    )
    return {"data": row, "message": "Task created"}


@router.patch("/{task_id}")
async def update_task(task_id: str, update: TaskUpdate):
    """Update task status, assignment, or notes."""
    fields = []
    params = []
    idx = 1

    update_dict = update.model_dump(exclude_none=True)
    
    for key, val in update_dict.items():
        if key == "assigned_volunteer_id":
            val = str(val)
        fields.append(f"{key} = ${idx}")
        params.append(val)
        idx += 1

    # Auto-set timestamps based on status
    if "status" in update_dict:
        status = update_dict["status"]
        if status == "in_progress":
            fields.append(f"started_at = NOW()")
        elif status == "completed":
            fields.append(f"completed_at = NOW()")
        elif status == "validated":
            fields.append(f"validated_at = NOW()")

    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")

    params.append(task_id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ${idx} RETURNING *"
    row = await execute_returning(query, *params)

    if not row:
        raise HTTPException(status_code=404, detail="Task not found")

    return {"data": row, "message": "Task updated"}


@router.post("/{task_id}/assign/{volunteer_id}")
async def assign_task(task_id: str, volunteer_id: str):
    """Assign a volunteer to a task."""
    # Verify volunteer exists
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

    # Update volunteer workload
    await execute(
        "UPDATE volunteers SET current_workload = current_workload + 1 WHERE id = $1",
        volunteer_id
    )

    return {"data": row, "message": "Volunteer assigned to task"}
