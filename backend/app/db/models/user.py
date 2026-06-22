from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    aws_access_key = Column(String) # We will encrypt this later!
    aws_secret_key = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())