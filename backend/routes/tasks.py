"""
Tasks API — Lifecycle management + assignment
Flask Blueprint version.
"""

from uuid import UUID
from flask import Blueprint, request, jsonify, abort
from backend.database import fetch_all, fetch_one, execute_returning, execute

tasks_bp = Blueprint('tasks_bp', __name__)

@tasks_bp.route("", methods=["GET"])
async def list_tasks():
    """List tasks with filtering."""
    status = request.args.get("status")
    priority = request.args.get("priority")
    volunteer_id = request.args.get("volunteer_id")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

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
    return jsonify({"data": rows, "total": len(rows)})


@tasks_bp.route("/<task_id>", methods=["GET"])
async def get_task(task_id):
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
        return jsonify({"error": "Task not found"}), 404
        
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
    return jsonify(row)


@tasks_bp.route("", methods=["POST"])
async def create_task():
    """Create a new task from a report."""
    data = request.json
    if not data or "report_id" not in data:
        return jsonify({"error": "report_id required"}), 400
        
    report = await fetch_one(
        "SELECT urgency_score, priority_level FROM community_reports WHERE id = $1",
        str(data["report_id"])
    )
    
    priority_score = report["urgency_score"] if report else 0
    priority_level = data.get("priority_level") or (report["priority_level"] if report else "medium")

    row = await execute_returning(
        """INSERT INTO tasks
           (report_id, task_type, title, description, priority_level,
            priority_score, deadline, resources_needed)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8::jsonb)
           RETURNING *""",
        str(data["report_id"]), data.get("task_type", "Resolution"), data.get("title", "New Task"),
        data.get("description", ""), priority_level, priority_score,
        data.get("deadline"), data.get("resources_needed", "[]")
    )
    return jsonify({"data": row, "message": "Task created"})


@tasks_bp.route("/<task_id>/assign/<volunteer_id>", methods=["POST"])
async def assign_task(task_id, volunteer_id):
    """Assign a volunteer to a task."""
    vol = await fetch_one("SELECT * FROM volunteers WHERE id = $1", volunteer_id)
    if not vol:
        return jsonify({"error": "Volunteer not found"}), 404

    row = await execute_returning(
        """UPDATE tasks
           SET assigned_volunteer_id = $1, status = 'assigned'
           WHERE id = $2
           RETURNING *""",
        volunteer_id, task_id
    )

    if not row:
        return jsonify({"error": "Task not found"}), 404

    await execute(
        "UPDATE volunteers SET current_workload = current_workload + 1 WHERE id = $1",
        volunteer_id
    )

    return jsonify({"data": row, "message": "Volunteer assigned to task"})
