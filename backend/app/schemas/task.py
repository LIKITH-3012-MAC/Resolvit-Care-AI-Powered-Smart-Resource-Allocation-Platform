from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    report_id: int

class TaskCreate(TaskBase):
    deadline: Optional[datetime] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskAssignmentSchema(BaseModel):
    id: int
    volunteer_id: int
    status: str
    match_score: float
    match_reasons: Optional[Dict[str, Any]] = None
    assigned_at: datetime
    accepted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class TaskSchema(TaskBase):
    id: int
    status: str
    created_at: datetime
    deadline: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    assignments: List[TaskAssignmentSchema] = []
    
    model_config = ConfigDict(from_attributes=True)
