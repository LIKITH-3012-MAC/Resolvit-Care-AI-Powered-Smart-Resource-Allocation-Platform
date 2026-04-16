"""
Reports API — CRUD + AI classification + priority scoring
Flask Blueprint version.
"""

import json
from uuid import UUID
from flask import Blueprint, request, jsonify, abort
from backend.database import fetch_all, fetch_one, execute_returning, execute
from ai import classify_report
from ai.priority import calculate_priority

reports_bp = Blueprint('reports_bp', __name__)

@reports_bp.route("", methods=["GET"])
async def list_reports():
    """List all community reports with filtering."""
    # Using request.args for Query parameters
    category = request.args.get("category")
    priority = request.args.get("priority")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 50))
    offset = int(request.args.get("offset", 0))
    sort = request.args.get("sort", "created_at")
    order = request.args.get("order", "desc")

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

    return jsonify({"data": rows, "total": total, "limit": limit, "offset": offset})


@reports_bp.route("/<report_id>", methods=["GET"])
async def get_report(report_id):
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
        return jsonify({"error": "Report not found"}), 404
    
    # Convert types
    for key, val in row.items():
        if isinstance(val, UUID):
            row[key] = str(val)
            
    return jsonify(row)


@reports_bp.route("", methods=["POST"])
async def create_report():
    """Submit a new report."""
    data = request.json
    if not data or "title" not in data or "description" not in data:
        return jsonify({"error": "Title and Description required"}), 400

    # AI classification
    classification = classify_report(data["description"], data["title"])
    category = classification.get("primary", data.get("category", "General"))

    # AI priority scoring
    priority_input = {
        "severity": data.get("severity", 5),
        "people_affected": data.get("people_affected", 1),
        "vulnerable_group": data.get("vulnerable_group", ""),
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
        data["title"], data["description"], category,
        data.get("severity", 5), priority["score"], priority["level"],
        data.get("people_affected", 1), data.get("vulnerable_group", ""),
        data.get("source_type", "web_form"), data.get("latitude"), data.get("longitude"),
        data.get("address_text", ""), data.get("images", []),
        json.dumps(classification), priority["explanation"]
    )

    return jsonify({
        "data": row,
        "ai_classification": classification,
        "ai_priority": priority,
        "message": "Report created successfully"
    })
