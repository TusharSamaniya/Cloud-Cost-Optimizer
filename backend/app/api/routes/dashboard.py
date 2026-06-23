from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.resource import Resource
from app.db.models.recommendation import Recommendation

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Calculates the top-level metrics for the React frontend."""
    
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    recommendations = db.query(Recommendation).filter(Recommendation.user_id == current_user.id).all()

    # Calculate total monthly cost
    total_cost = sum(r.monthly_cost for r in resources if r.monthly_cost is not None)
    
    # We will assume your recommendation model has a column named 'estimated_savings' or similar. 
    # If the column name is different in your database, we will adjust this later!
    total_wasted = sum(getattr(rec, 'estimated_savings', 0) for rec in recommendations if rec.status != "applied")
    
    savings_percent = 0
    if total_cost > 0:
        savings_percent = round((total_wasted / total_cost) * 100, 1)

    return {
        "total_monthly_cost": round(total_cost, 2),
        "total_wasted": round(total_wasted, 2),
        "savings_percent": savings_percent,
        "resource_count": len(resources),
        "recommendation_count": len(recommendations)
    }