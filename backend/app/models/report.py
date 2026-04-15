from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base

class NeedCategory(Base):
    __tablename__ = "need_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    icon_name = Column(String(50))
    
    reports = relationship("CommunityReport", back_populates="category")

class CommunityReport(Base):
    __tablename__ = "community_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    raw_text = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("need_categories.id"))
    
    # Impact & Priority
    severity_level = Column(Integer, default=5) # 1-10
    urgency_score = Column(Float, default=0.0)
    affected_count = Column(Integer, default=1)
    
    # Location (No PostGIS Fallback)
    latitude = Column(Float)
    longitude = Column(Float)
    location_name = Column(String(255))
    
    # Media & Data
    structured_data = Column(JSON) # Extracted fields
    report_source = Column(String(50), default="citizen_portal") # portal, whatsapp, officer
    
    # Security/AI Flags
    is_duplicate = Column(Boolean, default=False)
    fraud_flag = Column(Boolean, default=False)
    anomaly_details = Column(JSON)
    
    # Auth & Status
    reporter_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50), default="reported") # reported, prioritized, case_opened, matching, assigned, resolving, resolved, closed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    category = relationship("NeedCategory", back_populates="reports")
    priority_scores = relationship("PriorityScore", back_populates="report")
    tasks = relationship("Task", back_populates="report")
    evidence = relationship("Evidence", back_populates="report")
    case = relationship("Case", back_populates="report", uselist=False)

class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("community_reports.id"))
    file_type = Column(String(50)) # image, video, voice, document
    file_url = Column(String(500))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    report = relationship("CommunityReport", back_populates="evidence")

class PriorityScore(Base):
    __tablename__ = "priority_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("community_reports.id"))
    
    score = Column(Float)
    severity_weight = Column(Float)
    affected_weight = Column(Float)
    vulnerability_weight = Column(Float)
    time_sensitivity_weight = Column(Float)
    resource_gap_weight = Column(Float)
    explanation = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    report = relationship("CommunityReport", back_populates="priority_scores")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("community_reports.id"), unique=True)
    case_number = Column(String(50), unique=True)
    
    owner_id = Column(Integer, ForeignKey("users.id")) # NGO Admin or Field Coordinator
    assigned_responder_id = Column(Integer, ForeignKey("users.id")) # Field Officer or Lead Volunteer
    
    status = Column(String(50), default="open")
    priority = Column(String(50))
    sla_deadline = Column(DateTime(timezone=True))
    
    notes = Column(Text)
    outcome_summary = Column(Text)
    beneficiary_confirmation = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    report = relationship("CommunityReport", back_populates="case")
    escalations = relationship("CaseEscalation", back_populates="case")

class CaseEscalation(Base):
    __tablename__ = "case_escalations"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"))
    reason = Column(Text)
    previous_status = Column(String(50))
    new_status = Column(String(50))
    escalated_by_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    case = relationship("Case", back_populates="escalations")
