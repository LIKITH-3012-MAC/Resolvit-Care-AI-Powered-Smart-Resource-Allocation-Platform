"""
Analytics API — Dashboard KPIs, trends, category stats
Flask Blueprint version.
"""

from flask import Blueprint, request, jsonify
from backend.database import fetch_all, fetch_one

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route("/dashboard", methods=["GET"])
async def dashboard_stats():
    """Get main dashboard statistics."""
    stats = await fetch_one("""
        SELECT
            (SELECT COUNT(*) FROM community_reports) as total_reports,
            (SELECT COUNT(*) FROM community_reports WHERE priority_level = 'critical') as critical_reports,
            (SELECT COUNT(*) FROM community_reports WHERE priority_level = 'high') as high_reports,
            (SELECT COUNT(*) FROM tasks WHERE status NOT IN ('completed', 'closed', 'validated')) as active_tasks,
            (SELECT COUNT(*) FROM tasks WHERE status IN ('completed', 'validated', 'closed')) as completed_tasks,
            (SELECT COUNT(*) FROM tasks) as total_tasks,
            (SELECT COUNT(*) FROM volunteers) as total_volunteers,
            (SELECT COUNT(*) FROM volunteers WHERE availability = 'available') as available_volunteers,
            (SELECT COALESCE(SUM(beneficiaries_served), 0) FROM impact_records) as total_beneficiaries,
            (SELECT COALESCE(AVG(time_to_resolve_hours), 0) FROM impact_records) as avg_response_hours
    """)

    total_tasks = stats["total_tasks"] or 1
    completion_rate = round((stats["completed_tasks"] / total_tasks) * 100, 1)

    return jsonify({
        "total_reports": stats["total_reports"],
        "critical_reports": stats["critical_reports"],
        "high_reports": stats["high_reports"],
        "active_tasks": stats["active_tasks"],
        "completed_tasks": stats["completed_tasks"],
        "total_volunteers": stats["total_volunteers"],
        "available_volunteers": stats["available_volunteers"],
        "total_beneficiaries": stats["total_beneficiaries"],
        "avg_response_hours": round(float(stats["avg_response_hours"]), 1),
        "completion_rate": completion_rate,
    })


@analytics_bp.route("/categories", methods=["GET"])
async def category_breakdown():
    """Get reports breakdown by category."""
    rows = await fetch_all("""
        SELECT category, COUNT(*) as count,
               ROUND(COUNT(*) * 100.0 / NULLIF((SELECT COUNT(*) FROM community_reports), 0), 1) as percentage,
               AVG(urgency_score) as avg_urgency,
               SUM(people_affected) as total_people
        FROM community_reports
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC
    """)
    return jsonify({"data": rows})


@analytics_bp.route("/priorities", methods=["GET"])
async def priority_breakdown():
    """Get reports breakdown by priority level."""
    rows = await fetch_all("""
        SELECT priority_level, COUNT(*) as count,
               AVG(urgency_score) as avg_score,
               SUM(people_affected) as total_people
        FROM community_reports
        GROUP BY priority_level
        ORDER BY CASE priority_level
            WHEN 'critical' THEN 1
            WHEN 'high' THEN 2
            WHEN 'medium' THEN 3
            WHEN 'low' THEN 4
        END
    """)
    return jsonify({"data": rows})


@analytics_bp.route("/timeline", methods=["GET"])
async def timeline_stats():
    """Get daily report/task activity timeline."""
    days = int(request.args.get("days", 30))
    # Flask query params via request.args
    rows = await fetch_all(f"""
        SELECT
            d.date::text as date,
            COALESCE(r.report_count, 0) as reports,
            COALESCE(t.task_completed, 0) as tasks_completed,
            COALESCE(i.beneficiaries, 0) as beneficiaries
        FROM generate_series(
            CURRENT_DATE - INTERVAL '{days} days',
            CURRENT_DATE,
            '1 day'
        ) AS d(date)
        LEFT JOIN (
            SELECT DATE(created_at) as dt, COUNT(*) as report_count
            FROM community_reports
            GROUP BY DATE(created_at)
        ) r ON d.date = r.dt
        LEFT JOIN (
            SELECT DATE(completed_at) as dt, COUNT(*) as task_completed
            FROM tasks WHERE completed_at IS NOT NULL
            GROUP BY DATE(completed_at)
        ) t ON d.date = t.dt
        LEFT JOIN (
            SELECT DATE(created_at) as dt, SUM(beneficiaries_served) as beneficiaries
            FROM impact_records
            GROUP BY DATE(created_at)
        ) i ON d.date = i.dt
        ORDER BY d.date
    """)
    return jsonify({"data": rows})


@analytics_bp.route("/volunteers/stats", methods=["GET"])
async def volunteer_stats():
    """Get volunteer performance statistics."""
    rows = await fetch_all("""
        SELECT
            u.name,
            v.reliability_score,
            v.total_tasks_completed,
            v.current_workload,
            v.availability,
            array_to_string(v.skill_tags, ', ') as skills,
            COALESCE(SUM(ir.beneficiaries_served), 0) as total_beneficiaries
        FROM volunteers v
        JOIN users u ON v.user_id = u.id
        LEFT JOIN impact_records ir ON v.id = ir.volunteer_id
        GROUP BY u.name, v.reliability_score, v.total_tasks_completed,
                 v.current_workload, v.availability, v.skill_tags
        ORDER BY v.reliability_score DESC
    """)
    return jsonify({"data": rows})


@analytics_bp.route("/impact", methods=["GET"])
async def impact_summary():
    """Get overall impact metrics."""
    stats = await fetch_one("""
        SELECT
            COUNT(*) as total_actions,
            SUM(beneficiaries_served) as total_beneficiaries,
            AVG(time_to_resolve_hours) as avg_resolve_time,
            SUM(resource_cost) as total_resource_cost,
            COUNT(CASE WHEN follow_up_required THEN 1 END) as pending_followups,
            AVG(satisfaction_score) as avg_satisfaction
        FROM impact_records
    """)
    return jsonify({
        "total_actions": stats["total_actions"],
        "total_beneficiaries": int(stats["total_beneficiaries"] or 0),
        "avg_resolve_time_hours": round(float(stats["avg_resolve_time"] or 0), 1),
        "total_resource_cost": float(stats["total_resource_cost"] or 0),
        "pending_followups": stats["pending_followups"],
        "avg_satisfaction": round(float(stats["avg_satisfaction"] or 0), 1) if stats["avg_satisfaction"] else None,
    })
