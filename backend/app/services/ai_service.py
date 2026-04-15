from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.report import CommunityReport, PriorityScore
from backend.app.models.user import Volunteer
from ai.priority import calculate_priority
from ai.matcher import find_best_matches

class AIService:
    @staticmethod
    async def prioritize_report(db: AsyncSession, report: CommunityReport) -> PriorityScore:
        """
        Run the AI priority scoring engine on a report.
        """
        # Convert SQLAlchemy model to dict for the legacy AI logic
        report_data = {
            "id": report.id,
            "severity": 7, # Placeholder for AI-extracted severity
            "people_affected": report.affected_count,
            "vulnerable_group": report.structured_data.get("vulnerabilities", "") if report.structured_data else "",
            "category": report.category.name if report.category else "general",
            "verification_status": report.status,
            "created_at": report.created_at,
        }
        
        priority_result = calculate_priority(report_data)
        
        # Update report urgency scores
        report.urgency_score = priority_result["score"]
        report.status = "prioritized"
        
        # Create/Update PriorityScore entry
        priority_entry = PriorityScore(
            report_id=report.id,
            severity_weight=priority_result["breakdown"]["severity"],
            affected_weight=priority_result["breakdown"]["people_affected"],
            vulnerability_weight=priority_result["breakdown"]["vulnerability"],
            time_sensitivity_weight=priority_result["breakdown"]["time_criticality"],
            resource_gap_weight=priority_result["breakdown"]["resource_gap"],
            explanation=priority_result["explanation"]
        )
        
        return priority_entry

    @staticmethod
    async def match_volunteers(db: AsyncSession, task_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find best matching volunteers for a task.
        """
        # Get all relevant volunteers from DB
        query = select(Volunteer).where(Volunteer.current_status == "available")
        result = await db.execute(query)
        volunteers = result.scalars().all()
        
        # Convert to list of dicts for matcher
        vol_list = []
        for v in volunteers:
            vol_list.append({
                "user_id": v.user_id,
                "name": v.user.full_name,
                "skill_tags": v.skill_tags.split(",") if v.skill_tags else [],
                "latitude": 12.9716, # Placeholder
                "longitude": 77.5946,
                "availability": v.current_status,
                "reliability_score": v.trust_score,
            })
            
        matches = find_best_matches(vol_list, task_data)
        return matches

ai_service = AIService()
