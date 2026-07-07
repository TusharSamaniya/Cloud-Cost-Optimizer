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
    if settings.USE_MOCK_DATA:
        data = get_mock_resources()
        db.query(Resource).filter(Resource.user_id == current_user.id).delete()
        for item in data:
            db.add(Resource(
                user_id=current_user.id,
                resource_id=item["resource_id"],
                name=item["service_name"],
                type=item["resource_type"],
                region=item["region"],
                monthly_cost=item["cost_amount"],
                avg_cpu_percent=item["cpu_utilization"],
                status="healthy",
            ))
        db.commit()

        try:
            from backend.ml.pipeline import run_full_pipeline
            run_full_pipeline(current_user.id)
        except Exception as e:
            print(f"Warning: ML pipeline failed during sync: {e}")

        return {"message": "Mock data synced successfully!", "resources_added": len(data)}

    else:
        # Real AWS path
        if not current_user.aws_access_key or not current_user.aws_secret_key:
            raise HTTPException(
                status_code=400,
                detail="No AWS credentials found. Please connect your AWS account in Settings first."
            )

        try:
            from app.services.aws_service import (
                fetch_ec2_instances,
                fetch_cost_explorer,
                fetch_cloudwatch_metrics
            )

            # Step 1: Get list of running EC2 instances
            instances = fetch_ec2_instances(current_user)

            # FIXED: Step 2 — fetch real costs from Cost Explorer
            # Build a per-service cost map from the last 30 days of billing data
            cost_data = fetch_cost_explorer(current_user)
            total_cost = 0.0
            for day in cost_data:
                for group in day.get('Total', {}).values():
                    try:
                        total_cost += float(group.get('Amount', 0))
                    except (ValueError, TypeError):
                        pass

            # Distribute total cost evenly across instances as an approximation
            # (A production system would use resource-level tagging for exact costs)
            per_instance_cost = round(total_cost / len(instances), 2) if instances else 0.0

            # FIXED: Step 3 — fetch real CPU from CloudWatch for each instance
            for inst in instances:
                inst["monthly_cost"] = per_instance_cost
                try:
                    inst["avg_cpu_percent"] = fetch_cloudwatch_metrics(
                        current_user, inst["resource_id"]
                    )
                except Exception:
                    inst["avg_cpu_percent"] = 0.0  # fallback if CloudWatch fails

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"AWS connection failed: {str(e)}")

        db.query(Resource).filter(Resource.user_id == current_user.id).delete()
        for inst in instances:
            db.add(Resource(
                user_id=current_user.id,
                resource_id=inst["resource_id"],
                name=inst["name"],
                type=inst["type"],
                region=inst["region"],
                monthly_cost=inst["monthly_cost"],
                avg_cpu_percent=inst["avg_cpu_percent"],
                status=inst["status"],
            ))
        db.commit()

        try:
            from backend.ml.pipeline import run_full_pipeline
            run_full_pipeline(current_user.id)
        except Exception as e:
            print(f"Warning: ML pipeline failed during sync: {e}")

        return {"message": "AWS data synced successfully!", "resources_added": len(instances)}


@router.get("/resources")
def get_user_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    return resources
