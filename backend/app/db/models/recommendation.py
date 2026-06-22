from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(String)
    title = Column(String)
    description = Column(String)
    saving_amount = Column(Float)
    priority = Column(String)
    status = Column(String, default="pending") # pending, applied, or dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now())