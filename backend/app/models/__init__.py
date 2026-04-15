from backend.app.db.session import Base
from backend.app.models.user import User, SessionLog, Ngo, Volunteer
from backend.app.models.report import CommunityReport, NeedCategory, Evidence, PriorityScore, Case, CaseEscalation
from backend.app.models.task import Task, TaskAssignment
from backend.app.models.resource import ResourceCategory, ResourceInventory, ResourceMovement
from backend.app.models.audit import AuditLog, SecurityLog
from backend.app.models.notification import Notification, CommunicationLog

# Ensure all models are imported here so Base.metadata is fully populated
__all__ = [
    "Base",
    "User",
    "SessionLog",
    "Ngo",
    "Volunteer",
    "CommunityReport",
    "NeedCategory",
    "Evidence",
    "PriorityScore",
    "Case",
    "CaseEscalation",
    "Task",
    "TaskAssignment",
    "ResourceCategory",
    "ResourceInventory",
    "ResourceMovement",
    "AuditLog",
    "SecurityLog",
    "Notification",
    "CommunicationLog",
]
