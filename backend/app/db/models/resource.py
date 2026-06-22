from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Resource(Base):
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(String, index=True) # This is the AWS unique ID
    name = Column(String)
    type = Column(String)
    region = Column(String)
    monthly_cost = Column(Float)
    avg_cpu_percent = Column(Float)
    status = Column(String) # healthy, idle, or overprovisioned
    last_synced = Column(DateTime(timezone=True), server_default=func.now())