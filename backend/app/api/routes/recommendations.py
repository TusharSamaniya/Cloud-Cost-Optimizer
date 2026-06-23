from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.recommendation import Recommendation

router = APIRouter()

class StatusUpdate(BaseModel):
    status: str

@router.get("/")
def get_recommendations(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns recommendations, optionally filtered by priority or status."""
    query = db.query(Recommendation).filter(Recommendation.user_id == current_user.id)
    
    if priority:
        query = query.filter(Recommendation.priority == priority)
    if status:
        query = query.filter(Recommendation.status == status)
        
    return query.all()

@router.patch("/{rec_id}")
def update_recommendation_status(
    rec_id: int,
    update_data: StatusUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates a recommendation to 'applied' or 'dismissed'."""
    rec = db.query(Recommendation).filter(Recommendation.id == rec_id, Recommendation.user_id == current_user.id).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
        
    rec.status = update_data.status
    db.commit()
    return {"message": f"Recommendation status updated to {update_data.status}"}