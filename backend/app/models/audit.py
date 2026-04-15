from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(100), nullable=False) # e.g., create_report, update_user_role, delete_resource
    target_type = Column(String(50)) # table name: users, cases, reports
    target_id = Column(Integer)
    
    changes = Column(JSON) # { "field": [old, new] }
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="audit_logs")

class SecurityLog(Base):
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100)) # failed_login, password_change, brute_force_detected
    severity = Column(String(20), default="info") # info, warning, critical
    details = Column(JSON)
    ip_address = Column(String(50))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
