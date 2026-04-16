"""
Resources API — Inventory management
Flask Blueprint version.
"""

from uuid import UUID
from flask import Blueprint, request, jsonify, abort
from backend.database import fetch_all, fetch_one, execute_returning, execute

resources_bp = Blueprint('resources_bp', __name__)

@resources_bp.route("", methods=["GET"])
async def list_resources():
    """List resource inventory."""
    res_type = request.args.get("type")
    status = request.args.get("status")
    limit = int(request.args.get("limit", 50))

    conditions = []
    params = []
    idx = 1

    if res_type:
        conditions.append(f"type = ${idx}")
        params.append(res_type)
        idx += 1
    if status:
        conditions.append(f"availability_status = ${idx}")
        params.append(status)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    query = f"""
        SELECT * FROM resource_inventory
        {where}
        ORDER BY type, name
        LIMIT ${idx}
    """
    params.append(limit)

    rows = await fetch_all(query, *params)
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
    return jsonify({"data": rows, "total": len(rows)})


@resources_bp.route("", methods=["POST"])
async def create_resource():
    """Add a resource to inventory."""
    data = request.json
    if not data or "name" not in data or "type" not in data:
        return jsonify({"error": "name and type required"}), 400
        
    row = await execute_returning(
        """INSERT INTO resource_inventory
           (name, type, quantity, unit, warehouse_location,
            warehouse_latitude, warehouse_longitude)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           RETURNING *""",
        data["name"], data["type"], data.get("quantity", 0),
        data.get("unit", "units"), data.get("warehouse_location", ""),
        data.get("warehouse_latitude"), data.get("warehouse_longitude")
    )
    return jsonify({"data": row, "message": "Resource added"})


@resources_bp.route("/<resource_id>", methods=["PATCH"])
async def update_resource(resource_id):
    """Update resource quantity or status."""
    data = request.json
    quantity = data.get("quantity")
    status = data.get("status")

    fields = []
    params = []
    idx = 1

    if quantity is not None:
        fields.append(f"quantity = ${idx}")
        params.append(quantity)
        idx += 1
    if status:
        fields.append(f"availability_status = ${idx}")
        params.append(status)
        idx += 1

    if not fields:
        return jsonify({"error": "No fields to update"}), 400

    params.append(resource_id)
    query = f"UPDATE resource_inventory SET {', '.join(fields)} WHERE id = ${idx} RETURNING *"
    row = await execute_returning(query, *params)
    
    if not row:
        return jsonify({"error": "Resource not found"}), 404

    return jsonify({"data": row, "message": "Resource updated"})


@resources_bp.route("/summary", methods=["GET"])
async def resource_summary():
    """Get resource inventory summary by type."""
    rows = await fetch_all(
        """SELECT type,
                   COUNT(*) as item_count,
                   SUM(quantity) as total_quantity,
                   SUM(CASE WHEN availability_status = 'available' THEN quantity ELSE 0 END) as available_qty
            FROM resource_inventory
            GROUP BY type
            ORDER BY type"""
    )
    return jsonify({"data": rows})
