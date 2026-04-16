"""
Maps API — Geospatial data for map visualization
Flask Blueprint version.
"""

from uuid import UUID
from flask import Blueprint, request, jsonify
from backend.database import fetch_all
from ai.clustering import kmeans_cluster, dbscan_cluster, generate_heatmap_data

maps_bp = Blueprint('maps_bp', __name__)

@maps_bp.route("/reports", methods=["GET"])
async def map_reports():
    """Get all reports with coordinates for map display."""
    priority = request.args.get("priority")
    category = request.args.get("category")

    conditions = ["cr.latitude IS NOT NULL", "cr.longitude IS NOT NULL"]
    params = []
    idx = 1

    if priority:
        conditions.append(f"cr.priority_level = ${idx}")
        params.append(priority)
        idx += 1
    if category:
        conditions.append(f"cr.category = ${idx}")
        params.append(category)
        idx += 1

    where = f"WHERE {' AND '.join(conditions)}"

    rows = await fetch_all(f"""
        SELECT cr.id, cr.title, cr.category, cr.severity, cr.urgency_score,
               cr.priority_level, cr.people_affected, cr.latitude, cr.longitude,
               cr.verification_status, cr.created_at,
               l.name as location_name, l.district
        FROM community_reports cr
        LEFT JOIN locations l ON cr.location_id = l.id
        {where}
        ORDER BY cr.urgency_score DESC
    """, *params)

    # Convert UUIDs
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)

    return jsonify({"data": rows, "total": len(rows)})


@maps_bp.route("/volunteers", methods=["GET"])
async def map_volunteers():
    """Get volunteer locations for map display."""
    rows = await fetch_all("""
        SELECT v.id, u.name, v.availability, v.reliability_score,
               v.latitude, v.longitude, v.current_workload,
               array_to_string(v.skill_tags, ', ') as skills
        FROM volunteers v
        JOIN users u ON v.user_id = u.id
        WHERE v.latitude IS NOT NULL AND v.longitude IS NOT NULL
    """)
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
    return jsonify({"data": rows})


@maps_bp.route("/hotspots", methods=["GET"])
async def detect_hotspots():
    """Detect need hotspots using clustering."""
    k = int(request.args.get("k", 4))
    method = request.args.get("method", "kmeans")
    
    rows = await fetch_all("""
        SELECT id, title, category, severity, urgency_score,
               priority_level, people_affected, latitude, longitude
        FROM community_reports
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)

    if not rows:
        return jsonify({"clusters": [], "method": method})

    points = [dict(r) for r in rows]
    # Handle UUIDs in points
    for p in points:
        for key, val in p.items():
            if isinstance(val, UUID):
                p[key] = str(val)

    if method == "dbscan":
        result = dbscan_cluster(points)
        return jsonify({"clusters": result["clusters"], "method": "dbscan", "noise_count": result["noise_count"]})
    else:
        clusters = kmeans_cluster(points, k=min(k, len(points)))
        return jsonify({"clusters": clusters, "method": "kmeans"})


@maps_bp.route("/heatmap", methods=["GET"])
async def heatmap_data():
    """Get heatmap-ready data for urgency visualization."""
    rows = await fetch_all("""
        SELECT id, title, category, severity, urgency_score,
               priority_level, people_affected, latitude, longitude
        FROM community_reports
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """)

    points = [dict(r) for r in rows]
    for p in points:
        for key, val in p.items():
            if isinstance(val, UUID):
                p[key] = str(val)
                
    heatmap = generate_heatmap_data(points)
    return jsonify({"data": heatmap, "total": len(heatmap)})


@maps_bp.route("/resources", methods=["GET"])
async def map_resources():
    """Get resource warehouse locations for map display."""
    rows = await fetch_all("""
        SELECT id, name, type, quantity, unit, warehouse_location,
               warehouse_latitude as latitude, warehouse_longitude as longitude,
               availability_status
        FROM resource_inventory
        WHERE warehouse_latitude IS NOT NULL AND warehouse_longitude IS NOT NULL
    """)
    for row in rows:
        for key, val in row.items():
            if isinstance(val, UUID):
                row[key] = str(val)
    return jsonify({"data": rows})
