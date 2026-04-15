from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class ResourceInventoryBase(BaseModel):
    name: str
    category: Optional[str] = None
    quantity: float = 0.0
    unit: str
    location_name: Optional[str] = None

class ResourceInventoryCreate(ResourceInventoryBase):
    ngo_id: int

class ResourceInventoryUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    location_name: Optional[str] = None

class ResourceDispatchSchema(BaseModel):
    id: int
    resource_id: int
    task_id: int
    quantity: float
    status: str
    dispatched_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ResourceInventorySchema(ResourceInventoryBase):
    id: int
    ngo_id: int
    updated_at: Optional[datetime] = None
    dispatches: List[ResourceDispatchSchema] = []
    
    model_config = ConfigDict(from_attributes=True)
