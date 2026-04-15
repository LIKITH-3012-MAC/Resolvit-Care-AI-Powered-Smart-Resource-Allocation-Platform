from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from backend.app.db.session import Base

class ResourceCategory(Base):
    __tablename__ = "resource_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False) # e.g., Medical, Food, Shelter
    description = Column(Text)
    
    inventories = relationship("ResourceInventory", back_populates="category")

class ResourceInventory(Base):
    __tablename__ = "resource_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    ngo_id = Column(Integer, ForeignKey("ngos.id"))
    category_id = Column(Integer, ForeignKey("resource_categories.id"))
    
    item_name = Column(String(255), nullable=False)
    total_quantity = Column(Float, default=0.0)
    available_quantity = Column(Float, default=0.0)
    unit = Column(String(20)) # kits, kg, units, beds
    
    threshold_alert = Column(Float, default=10.0) # Alert when below this
    location_details = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("ResourceCategory", back_populates="inventories")
    movements = relationship("ResourceMovement", back_populates="inventory")

class ResourceMovement(Base):
    __tablename__ = "resource_movements"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("resource_inventory.id"))
    task_id = Column(Integer, ForeignKey("tasks.id")) # Linked to a mission
    
    movement_type = Column(String(50)) # inward, outward, transfer, adjustment
    quantity = Column(Float, nullable=False)
    
    source_location = Column(String(255))
    destination_location = Column(String(255))
    
    moved_by_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
    
    inventory = relationship("ResourceInventory", back_populates="movements")
    task = relationship("Task", back_populates="resource_movements")
