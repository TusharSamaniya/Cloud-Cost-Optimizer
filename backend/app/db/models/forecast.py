from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base   # BUG FIXED: this MUST be the same Base as every
                                 # other model (User, Resource, Recommendation,
                                 # Anomaly). The original file tried importing
                                 # Base from 'app.db.session' (doesn't exist
                                 # there) then 'app.db.base_class' (doesn't
                                 # exist at all), and silently fell back to
                                 # creating a BRAND NEW declarative_base().
                                 # That meant the forecasts table was on a
                                 # completely disconnected metadata registry —
                                 # Alembic's autogenerate could never see it,
                                 # so the table was either never created or
                                 # created without being tracked, and any
                                 # joins/relationships with User would break
                                 # the same way the original clustering.py
                                 # foreign key error did.


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False)
    forecast_date = Column(Date, index=True, nullable=False)
    predicted_cost = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
