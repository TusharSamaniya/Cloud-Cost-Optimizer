from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.anomaly import Anomaly

router = APIRouter()

@router.get("/")
def get_anomalies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all anomalies sorted by the newest first."""
    # .desc() orders them so the most recent anomaly is at the top of the list
    return db.query(Anomaly).filter(Anomaly.user_id == current_user.id).order_by(Anomaly.detected_at.desc()).all()