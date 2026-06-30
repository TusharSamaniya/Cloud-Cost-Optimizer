from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.resource import Resource
from app.db.models.recommendation import Recommendation

router = APIRouter()

@router.get("/summary")
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    recommendations = db.query(Recommendation).filter(
        Recommendation.user_id == current_user.id,
        Recommendation.status == "pending"
    ).all()

    total_cost = sum(r.monthly_cost or 0 for r in resources)

    # BUG FIXED: was using 'estimated_savings' which doesn't exist in the model
    # Correct column name is 'saving_amount' (defined in Recommendation model)
    total_wasted = sum(rec.saving_amount or 0 for rec in recommendations)

    savings_percent = round((total_wasted / total_cost) * 100, 1) if total_cost > 0 else 0

    # BUG FIXED: frontend reads 'total_spend', 'wasted_spend', 'resources_scanned'
    # but backend was returning 'total_monthly_cost', 'total_wasted', 'resource_count'
    # All keys now match exactly what DashboardPage.jsx expects
    return {
        "total_spend": round(total_cost, 2),
        "wasted_spend": round(total_wasted, 2),
        "savings_percent": savings_percent,
        "resources_scanned": len(resources),
        "recommendation_count": len(recommendations),
    }
