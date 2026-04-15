from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List
from datetime import datetime
from backend.app.models.user import UserRole

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    role: Optional[UserRole] = UserRole.REPORTER

# Properties to receive on user creation
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = None

# Properties to return to client
class UserSchema(UserBase):
    id: int
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Authentication schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# NGO Schemas
class NgoBase(BaseModel):
    name: str
    description: Optional[str] = None
    website: Optional[str] = None

class NgoCreate(NgoBase):
    admin_id: int

class NgoSchema(NgoBase):
    id: int
    admin_id: int
    verification_status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
