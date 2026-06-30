from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.resource import Resource
from app.core.config import settings
from app.services.mock_data_service import get_mock_resources

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

router = APIRouter()

@router.post("/")
def sync_cloud_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    The master sync route. Checks the feature flag to decide where to get data,
    then automatically runs the ML pipeline so cluster labels, recommendations,
    anomalies and forecasts are generated right away.
    """

    if settings.USE_MOCK_DATA:
        data = get_mock_resources()

        db.query(Resource).filter(Resource.user_id == current_user.id).delete()

        for item in data:
            new_resource = Resource(
                user_id=current_user.id,
                resource_id=item["resource_id"],
                name=item["service_name"],
                type=item["resource_type"],
                region=item["region"],
                monthly_cost=item["cost_amount"],
                avg_cpu_percent=item["cpu_utilization"],
                status="healthy",  # default until ML pipeline runs and relabels it
            )
            db.add(new_resource)

        db.commit()

        # BUG FIXED: sync used to only insert raw resources and stop there.
        # Without running the pipeline immediately, the dashboard stayed at
        # $0 / 0% forever because clustering, recommendations and forecasts
        # never got generated until the user manually hit "Run Scan".
        # Now sync ALSO runs the full ML pipeline right after inserting data.
        try:
            from ml.pipeline import run_full_pipeline
            run_full_pipeline(current_user.id)
        except Exception as e:
            # Don't fail the whole sync if ML pipeline has an issue —
            # resources are still saved, user can hit "Run Scan" to retry ML
            print(f"Warning: ML pipeline failed during sync: {e}")

        return {"message": "Mock data synced successfully!", "resources_added": len(data)}

    else:
        # Real AWS path
        try:
            from app.services.aws_service import fetch_ec2_instances, fetch_cost_explorer, fetch_cloudwatch_metrics
        except ImportError:
            raise HTTPException(
                status_code=501,
                detail="Real AWS sync is not implemented yet. Enable USE_MOCK_DATA=true in .env to test with sample data."
            )

        if not current_user.aws_access_key or not current_user.aws_secret_key:
            raise HTTPException(
                status_code=400,
                detail="No AWS credentials found. Please connect your AWS account in Settings first."
            )

        try:
            instances = fetch_ec2_instances(current_user)
        except Exception as e:
            # BUG FIXED: previously any AWS failure (bad keys, no permissions,
            # network issue) was silently swallowed and the user just saw
            # "Real AWS sync triggered (Logic pending)" with no real data.
            # Now we raise a proper error so the frontend shows what's wrong.
            raise HTTPException(status_code=400, detail=f"AWS connection failed: {str(e)}")

        db.query(Resource).filter(Resource.user_id == current_user.id).delete()
        for inst in instances:
            db.add(Resource(user_id=current_user.id, **inst))
        db.commit()

        try:
            from ml.pipeline import run_full_pipeline
            run_full_pipeline(current_user.id)
        except Exception as e:
            print(f"Warning: ML pipeline failed during sync: {e}")

        return {"message": "AWS data synced successfully!", "resources_added": len(instances)}


@router.get("/resources")
def get_user_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns all resources currently saved in the database for the logged-in user."""
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    return resources
