import asyncio
import random
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import AsyncSessionLocal, Base, engine
from backend.app.models.user import User, UserRole
from backend.app.models.report import CommunityReport, NeedCategory, PriorityScore
from backend.app.models.user import Ngo

async def seed_data():
    async with AsyncSessionLocal() as db:
        # 1. Create Need Categories
        categories = [
            {"name": "Medical", "description": "Urgent health requirements", "icon_name": "Activity"},
            {"name": "Food", "description": "Emergency food supplies", "icon_name": "Utensils"},
            {"name": "Water", "description": "Clean drinking water", "icon_name": "Droplets"},
            {"name": "Shelter", "description": "Emergency housing", "icon_name": "Home"},
            {"name": "Infrastructure", "description": "Electricity and roads", "icon_name": "Settings"},
        ]
        
        db_categories = []
        for cat in categories:
            db_cat = NeedCategory(**cat)
            db.add(db_cat)
            db_categories.append(db_cat)
        
        await db.commit()
        
        # 2. Create Admin & NGO
        admin = User(
            email="admin@resolvit.ai",
            full_name="Likith Naidu",
            hashed_password="hashed_password_placeholder", # In real app, use pwd_context.hash
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin)
        await db.commit()
        await db.refresh(admin)
        
        ngo = Ngo(
            name="Resolvit Global Relief",
            description="Elite humanitarian deployment network.",
            admin_id=admin.id,
            verification_status="verified"
        )
        db.add(ngo)
        await db.commit()
        
        # 3. Create Sample Reports
        report_data = [
            {
                "title": "Medical Facility Flooded",
                "raw_text": "The local clinic in South Sector is flooded. Patients need evacuation and dry storage for medicines.",
                "latitude": 12.9716,
                "longitude": 77.5946,
                "location_name": "South Sector, Block 4",
                "severity_level": 9,
                "urgency_score": 0.94,
                "affected_count": 45,
                "status": "prioritized"
            },
            {
                "title": "Food Supply Chain Cut Off",
                "raw_text": "Bridge collapse has isolated the Red Zone Colony. 12 families without food for 2 days.",
                "latitude": 12.9800,
                "longitude": 77.6000,
                "location_name": "Red Zone Colony",
                "severity_level": 8,
                "urgency_score": 0.87,
                "affected_count": 60,
                "status": "matching"
            },
            {
                "title": "Hospital B Power Surge",
                "raw_text": "Unstable power grid causing medical equipment failures at Hospital B.",
                "latitude": 12.9600,
                "longitude": 77.5800,
                "location_name": "Central Block",
                "severity_level": 7,
                "urgency_score": 0.82,
                "affected_count": 200,
                "status": "dispatched"
            }
        ]
        
        for r in report_data:
            report = CommunityReport(
                **r,
                category_id=db_categories[0].id if "Medical" in r["title"] else db_categories[1].id,
                report_source="citizen_portal"
            )
            db.add(report)
            await db.commit()
            await db.refresh(report)
            
            # Add priority entries
            priority = PriorityScore(
                report_id=report.id,
                score=r["urgency_score"],
                severity_weight=0.8,
                affected_weight=0.6,
                vulnerability_weight=0.9,
                time_sensitivity_weight=0.7,
                resource_gap_weight=0.5,
                explanation="AI Intelligence detected critical infrastructure impact."
            )
            db.add(priority)
            await db.commit()

        print("Seed data injected successfully.")

if __name__ == "__main__":
    asyncio.run(seed_data())
