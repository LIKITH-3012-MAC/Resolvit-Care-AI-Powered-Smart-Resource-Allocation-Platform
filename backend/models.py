"""
Smart Resource Allocation — Pydantic Models
Request/Response schemas for all API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ============ Reports ============

class ReportCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    description: str = Field(..., min_length=10)
    category: Optional[str] = None
    severity: int = Field(default=5, ge=1, le=10)
    people_affected: int = Field(default=1, ge=1)
    vulnerable_group: Optional[str] = None
    source_type: str = Field(default="web_form")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address_text: Optional[str] = None
    images: Optional[List[str]] = []


class ReportResponse(BaseModel):
    id: UUID
    title: str
    description: str
    category: Optional[str]
    subcategory: Optional[str]
    severity: int
    urgency_score: float
    priority_level: str
    people_affected: int
    vulnerable_group: Optional[str]
    source_type: str
    reporter_id: Optional[UUID]
    latitude: Optional[float]
    longitude: Optional[float]
    address_text: Optional[str]
    verification_status: str
    ai_classification: Optional[dict]
    ai_priority_explanation: Optional[str]
    created_at: datetime
    updated_at: datetime


class ReportUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    severity: Optional[int] = Field(default=None, ge=1, le=10)
    verification_status: Optional[str] = None
    people_affected: Optional[int] = None
    vulnerable_group: Optional[str] = None


# ============ Volunteers ============

class VolunteerCreate(BaseModel):
    user_id: UUID
    skill_tags: List[str] = []
    languages: List[str] = []
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    travel_radius_km: float = 10
    transport_access: str = "none"
    gender: Optional[str] = None
    preferred_causes: List[str] = []


class VolunteerResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: Optional[str] = None
    email: Optional[str] = None
    skill_tags: List[str]
    languages: List[str]
    availability: str
    latitude: Optional[float]
    longitude: Optional[float]
    reliability_score: float
    total_tasks_completed: int
    current_workload: int
    preferred_causes: List[str]
    travel_radius_km: float
    transport_access: str


class VolunteerUpdate(BaseModel):
    skill_tags: Optional[List[str]] = None
    languages: Optional[List[str]] = None
    availability: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    travel_radius_km: Optional[float] = None


# ============ Tasks ============

class TaskCreate(BaseModel):
    report_id: UUID
    task_type: str
    title: str
    description: Optional[str] = None
    priority_level: str = "medium"
    deadline: Optional[datetime] = None
    resources_needed: Optional[list] = []


class TaskResponse(BaseModel):
    id: UUID
    report_id: UUID
    assigned_volunteer_id: Optional[UUID]
    assigned_by: Optional[UUID]
    task_type: str
    title: str
    description: Optional[str]
    status: str
    priority_level: str
    priority_score: float
    deadline: Optional[datetime]
    ai_match_explanation: Optional[str]
    ai_match_score: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime


class TaskUpdate(BaseModel):
    status: Optional[str] = None
    assigned_volunteer_id: Optional[UUID] = None
    notes: Optional[str] = None
    proof_urls: Optional[List[str]] = None


# ============ Resources ============

class ResourceCreate(BaseModel):
    name: str
    type: str
    quantity: int = 0
    unit: str = "units"
    warehouse_location: Optional[str] = None
    warehouse_latitude: Optional[float] = None
    warehouse_longitude: Optional[float] = None
    expiry_date: Optional[str] = None


class ResourceResponse(BaseModel):
    id: UUID
    name: str
    type: str
    quantity: int
    unit: str
    warehouse_location: Optional[str]
    availability_status: str
    created_at: datetime


# ============ Analytics ============

class DashboardStats(BaseModel):
    total_reports: int
    critical_reports: int
    active_tasks: int
    completed_tasks: int
    total_volunteers: int
    available_volunteers: int
    total_beneficiaries: int
    avg_response_hours: float
    completion_rate: float

class CategoryStat(BaseModel):
    category: str
    count: int
    percentage: float

class TimelineStat(BaseModel):
    date: str
    reports: int
    tasks_completed: int
    beneficiaries: int
