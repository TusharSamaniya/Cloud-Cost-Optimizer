from sqlalchemy import Column, Integer, Float, Date, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

# Try to import the existing Base from your project, or fallback to a new one
try:
    from app.db.session import Base
except ImportError:
    try:
        from app.db.base_class import Base
    except ImportError:
        Base = declarative_base()

class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    forecast_date = Column(Date, index=True, nullable=False)
    predicted_cost = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())