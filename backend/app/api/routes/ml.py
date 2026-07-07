from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# ✅ FIX 1: get_current_user lives in app.core.dependencies, NOT app.api.deps
from app.core.dependencies import get_current_user
from app.db.session import SessionLocal
from app.db.models.resource import Resource
from app.db.models.user import User          # noqa: F401 — SQLAlchemy needs this
from app.db.models.forecast import Forecast

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from backend.ml.pipeline import run_full_pipeline

router = APIRouter()


# ---------------------------------------------------------------------------
# POST /api/ml/run  — manually trigger the full ML pipeline
# ---------------------------------------------------------------------------
@router.post("/run")
def trigger_pipeline(current_user: User = Depends(get_current_user)):
    """
    Triggers clustering → anomaly detection → forecasting → recommendations
    for the currently logged-in user.
    """
    try:
        run_full_pipeline(current_user.id)
        return {"message": "ML pipeline completed successfully", "user_id": current_user.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


# ---------------------------------------------------------------------------
# GET /api/ml/clusters  — return resources grouped by cluster label
# ---------------------------------------------------------------------------
@router.get("/clusters")
def get_clusters(current_user: User = Depends(get_current_user)):
    """
    Returns all resources for this user grouped by their ML cluster label:
    idle / healthy / overprovisioned
    """
    db = SessionLocal()
    try:                                          # ✅ FIX 2: always close the session
        resources = db.query(Resource).filter(
            Resource.user_id == current_user.id
        ).all()

        # Build grouped response
        clusters = {
            "idle":            {"count": 0, "total_cost": 0.0, "resources": []},
            "healthy":         {"count": 0, "total_cost": 0.0, "resources": []},
            "overprovisioned": {"count": 0, "total_cost": 0.0, "resources": []},
        }

        for r in resources:
            label = r.status if r.status in clusters else "healthy"
            clusters[label]["count"]       += 1
            clusters[label]["total_cost"]  += r.monthly_cost or 0.0
            clusters[label]["resources"].append({
                "resource_id":     r.resource_id,
                "name":            r.name,
                "type":            r.type,
                "region":          r.region,
                "monthly_cost":    round(r.monthly_cost or 0.0, 2),
                "avg_cpu_percent": round(r.avg_cpu_percent or 0.0, 2),
                "status":          r.status,
            })

        # Round totals
        for label in clusters:
            clusters[label]["total_cost"] = round(clusters[label]["total_cost"], 2)

        return clusters

    finally:
        db.close()


# ---------------------------------------------------------------------------
# GET /api/ml/forecast  — return the 30-day cost forecast
# ---------------------------------------------------------------------------
@router.get("/forecast")
def get_forecast(current_user: User = Depends(get_current_user)):
    """
    Returns the 30-day Prophet forecast for the logged-in user.
    """
    db = SessionLocal()
    try:                                          # ✅ FIX 2: always close the session
        forecasts = db.query(Forecast).filter(
            Forecast.user_id == current_user.id
        ).order_by(Forecast.forecast_date).all()

        if not forecasts:
            return {"message": "No forecast data yet. Run POST /api/ml/run first.", "data": []}

        return {
            "data": [
                {
                    "date":            f.forecast_date.strftime("%Y-%m-%d"),
                    "predicted_cost":  round(f.predicted_cost, 2),
                    "lower_bound":     round(f.lower_bound, 2),
                    "upper_bound":     round(f.upper_bound, 2),
                }
                for f in forecasts
            ]
        }
    finally:
        db.close()