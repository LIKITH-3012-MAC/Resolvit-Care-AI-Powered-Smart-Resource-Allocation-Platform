"""
Volunteers API — CRUD + matching
Flask Blueprint version.
"""

from uuid import UUID
from flask import Blueprint, request, jsonify, abort
from backend.database import fetch_all, fetch_one, execute_returning, execute
from ai.matcher import find_best_matches

volunteers_bp = Blueprint('volunteers_bp', __name__)

@volunteers_bp.route("", methods=["GET"])
async def list_volunteers():
    """List volunteers with filtering."""
    availability = request.args.get("availability")
    skill = request.args.get("skill")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))

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
                
    return jsonify({"data": rows, "total": len(rows)})


@volunteers_bp.route("/<volunteer_id>", methods=["GET"])
async def get_volunteer(volunteer_id):
    """Get volunteer details."""
    row = await fetch_one(
        """SELECT v.*, u.name, u.email, u.phone
           FROM volunteers v
           JOIN users u ON v.user_id = u.id
           WHERE v.id = $1""",
        volunteer_id
    )
    if not row:
        return jsonify({"error": "Volunteer not found"}), 404
        
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
    return jsonify(row)


@volunteers_bp.route("", methods=["POST"])
async def create_volunteer():
    """Register a new volunteer."""
    data = request.json
    if not data or "user_id" not in data:
        return jsonify({"error": "user_id required"}), 400
        
    row = await execute_returning(
        """INSERT INTO volunteers
           (user_id, skill_tags, languages, latitude, longitude,
            travel_radius_km, transport_access, gender, preferred_causes)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
           RETURNING *""",
        str(data["user_id"]), data.get("skill_tags", []), data.get("languages", []),
        data.get("latitude"), data.get("longitude"), data.get("travel_radius_km", 10),
        data.get("transport_access", "none"), data.get("gender"), data.get("preferred_causes", [])
    )
    return jsonify({"data": row, "message": "Volunteer registered"})


@volunteers_bp.route("/match", methods=["POST"])
async def match_volunteers():
    """Find best volunteer matches for a task using AI matching engine."""
    data = request.json
    if not data:
        return jsonify({"error": "Data required"}), 400
        
    task_type = data.get("task_type")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    
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
        "required_language": data.get("required_language", ""),
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

    matches = find_best_matches(vol_dicts, task_info, top_n=data.get("top_n", 5))
    return jsonify({"matches": matches, "task": task_info})
