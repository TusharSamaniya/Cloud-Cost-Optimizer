from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_user
from ml.pipeline import run_full_pipeline
from app.db.session import SessionLocal
from app.db.models.resource import Resource
from app.db.models.forecast import Forecast

router = APIRouter()

@router.post("/run")
def trigger_pipeline(current_user=Depends(get_current_user)):
    run_full_pipeline(current_user.id)
    return {"message": "Pipeline completed"}

@router.get("/clusters")
def get_clusters(current_user=Depends(get_current_user)):
    db = SessionLocal()
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    # Simple grouping logic
    clusters = {"idle": [], "healthy": [], "overprovisioned": []}
    for r in resources:
        clusters.setdefault(r.status, []).append({"name": r.name, "cost": r.monthly_cost})
    return clusters

@router.get("/forecast")
def get_forecast(current_user=Depends(get_current_user)):
    db = SessionLocal()
    return db.query(Forecast).filter(Forecast.user_id == current_user.id).all()