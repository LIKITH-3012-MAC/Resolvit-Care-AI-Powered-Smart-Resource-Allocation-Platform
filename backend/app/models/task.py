from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("community_reports.id"))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(50)) # low, medium, high, critical
    status = Column(String(50), default="open") # open, assigned, in_progress, completed, validated, closed
    
    # Timing
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    deadline = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    report = relationship("CommunityReport", back_populates="tasks")
    assignments = relationship("TaskAssignment", back_populates="task")
    resource_movements = relationship("ResourceMovement", back_populates="task")

class TaskAssignment(Base):
    __tablename__ = "task_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    volunteer_id = Column(Integer, ForeignKey("volunteers.id"))
    status = Column(String(50), default="pending") # pending, accepted, declined, completed
    match_score = Column(Float) # AI confidence in this match
    match_reasons = Column(JSON) # Why this volunteer was chosen
    
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    accepted_at = Column(DateTime(timezone=True))
    
    task = relationship("Task", back_populates="assignments")
    volunteer = relationship("Volunteer", back_populates="assignments")
