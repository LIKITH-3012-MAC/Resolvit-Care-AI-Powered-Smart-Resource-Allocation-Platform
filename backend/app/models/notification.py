from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    title = Column(String(255))
    message = Column(Text, nullable=False)
    type = Column(String(50)) # email, sms, push, in_app
    priority = Column(String(20), default="normal") # normal, urgent, emergency
    
    # Metadata
    reference_type = Column(String(50)) # case, report, task
    reference_id = Column(Integer)
    
    # Status
    is_sent = Column(Boolean, default=False)
    is_read = Column(Boolean, default=False)
    sent_at = Column(DateTime(timezone=True))
    read_at = Column(DateTime(timezone=True))
    
    # Error Handling
    error_log = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="notifications")

class CommunicationLog(Base):
    __tablename__ = "communication_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50)) # SMS, Email
    recipient = Column(String(255))
    content = Column(Text)
    provider_id = Column(String(100)) # Resend ID, Twilio SID etc.
    status = Column(String(50))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
