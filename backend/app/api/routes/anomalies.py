from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.anomaly import Anomaly
from app.db.models.resource import Resource

router = APIRouter()


@router.get("/")
def get_anomalies(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Returns all anomalies sorted newest first, shaped to match exactly
    what AnomalyItem.jsx expects on the frontend.

    BUG FIXED: previously this returned raw SQLAlchemy Anomaly rows, which
    only have resource_id (not a name), detected_at (not date_detected),
    and no spike_percentage field at all — but the frontend component reads
    resource_name, date_detected, and spike_percentage. Those were always
    undefined, which is why anomalies likely rendered with blank/NaN values.
    """
    anomalies = (
        db.query(Anomaly)
        .filter(Anomaly.user_id == current_user.id)
        .order_by(Anomaly.detected_at.desc())
        .all()
    )

    # Build a resource_id -> name lookup so we can show a human-readable name
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    name_lookup = {r.resource_id: r.name for r in resources}

    result = []
    for a in anomalies:
        spike_percent = 0
        if a.expected_cost and a.expected_cost > 0:
            spike_percent = round(((a.actual_cost - a.expected_cost) / a.expected_cost) * 100, 1)

        result.append({
            "id": a.id,
            "resource_name": name_lookup.get(a.resource_id, a.resource_id),
            "date_detected": a.detected_at.isoformat() if a.detected_at else None,
            "expected_cost": round(a.expected_cost or 0, 2),
            "actual_cost": round(a.actual_cost or 0, 2),
            "spike_percentage": spike_percent,
            # BUG FIXED: severity was stored lowercase ("high"/"medium"/"low")
            # but the frontend FilterBar compares against capitalized
            # ("High"/"Medium"/"Low"). Capitalizing here means the filter
            # buttons actually work instead of always showing zero results.
            "severity": (a.severity or "low").capitalize(),
        })

    return result
