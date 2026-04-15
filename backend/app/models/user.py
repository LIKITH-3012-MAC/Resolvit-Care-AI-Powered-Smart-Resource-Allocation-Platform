from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    NGO_ADMIN = "ngo_admin"
    FIELD_COORDINATOR = "field_coordinator"
    FIELD_OFFICER = "field_officer"
    VOLUNTEER = "volunteer"
    CITIZEN = "citizen"
    REPORTER = "reporter"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255))
    phone_number = Column(String(20))
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.CITIZEN)
    
    # Profile Details
    profile_photo_url = Column(String(500))
    address = Column(Text)
    district = Column(String(100))
    state = Column(String(100))
    pincode = Column(String(10))
    preferred_language = Column(String(50), default="English")
    emergency_contact = Column(JSON) # {name, relationship, phone}
    
    # Status & Verification
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_status = Column(String(50), default="unverified") # unverified, pending, verified
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Relationships
    ngo = relationship("Ngo", back_populates="admin", uselist=False)
    volunteer_profile = relationship("Volunteer", back_populates="user", uselist=False)
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    session_logs = relationship("SessionLog", back_populates="user")

class SessionLog(Base):
    __tablename__ = "session_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_info = Column(String(255))
    ip_address = Column(String(50))
    login_at = Column(DateTime(timezone=True), server_default=func.now())
    logout_at = Column(DateTime(timezone=True))
    
    user = relationship("User", back_populates="session_logs")

class Ngo(Base):
    __tablename__ = "ngos"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    website = Column(String(255))
    admin_id = Column(Integer, ForeignKey("users.id"))
    verification_status = Column(String(50), default="pending")
    operational_zones = Column(JSON) # List of districts/areas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    admin = relationship("User", back_populates="ngo")
    volunteers = relationship("Volunteer", back_populates="ngo")

class Volunteer(Base):
    __tablename__ = "volunteers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    ngo_id = Column(Integer, ForeignKey("ngos.id"))
    
    # Domain specific
    skill_tags = Column(String(500)) 
    certifications = Column(JSON) # List of docs/certs
    languages = Column(JSON) # List of languages
    availability_status = Column(String(50), default="available") # available, busy, on_leave, offline
    service_area = Column(String(255))
    
    # Metrics
    trust_score = Column(Integer, default=50)
    completed_assignments = Column(Integer, default=0)
    current_task_status = Column(String(100))
    
    user = relationship("User", back_populates="volunteer_profile")
    ngo = relationship("Ngo", back_populates="volunteers")
    assignments = relationship("TaskAssignment", back_populates="volunteer")
