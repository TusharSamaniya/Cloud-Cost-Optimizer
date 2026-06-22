from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(String)
    expected_cost = Column(Float)
    actual_cost = Column(Float)
    severity = Column(String) # low, medium, high
    detected_at = Column(DateTime(timezone=True), server_default=func.now())