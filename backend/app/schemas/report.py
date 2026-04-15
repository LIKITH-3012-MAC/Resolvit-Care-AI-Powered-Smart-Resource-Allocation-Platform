from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class NeedCategoryBase(BaseModel):
    name: str
    icon_name: Optional[str] = None
    description: Optional[str] = None

class NeedCategoryCreate(NeedCategoryBase):
    pass

class NeedCategorySchema(NeedCategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class CommunityReportBase(BaseModel):
    title: Optional[str] = None
    raw_text: str
    category_id: Optional[int] = None
    severity_level: Optional[int] = 5
    urgency_score: float = 0.0
    affected_count: int = 1
    location_name: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    report_source: str = "citizen_portal"

class CommunityReportCreate(CommunityReportBase):
    latitude: float
    longitude: float
    reporter_id: Optional[int] = None

class CommunityReportUpdate(BaseModel):
    title: Optional[str] = None
    category_id: Optional[int] = None
    severity_level: Optional[int] = None
    urgency_score: Optional[float] = None
    status: Optional[str] = None

class EvidenceSchema(BaseModel):
    id: int
    file_type: str
    file_url: str
    uploaded_at: datetime
    model_config = ConfigDict(from_attributes=True)

class CommunityReportSchema(CommunityReportBase):
    id: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    evidence: List[EvidenceSchema] = []
    
    model_config = ConfigDict(from_attributes=True)

class PriorityScoreSchema(BaseModel):
    score: float
    severity_weight: float
    affected_weight: float
    vulnerability_weight: float
    time_sensitivity_weight: float
    resource_gap_weight: float
    explanation: str
    
    model_config = ConfigDict(from_attributes=True)
