from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.db.models.resource import Resource
from app.core.config import settings
from app.services.mock_data_service import get_mock_resources

router = APIRouter()

@router.post("/")
def sync_cloud_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """The master sync route. Checks the feature flag to decide where to get data."""
    
    if settings.USE_MOCK_DATA:
        # 1. Get the fake data
        data = get_mock_resources()
        
        # 2. Delete any old resources for this user so we don't get duplicates
        db.query(Resource).filter(Resource.user_id == current_user.id).delete()
        
        # 3. Save the new generated resources to PostgreSQL
        for item in data:
            new_resource = Resource(
                user_id=current_user.id,
                resource_id=item["resource_id"],
                service_name=item["service_name"],
                resource_type=item["resource_type"],
                region=item["region"]
                # Note: We aren't saving cost/cpu here yet, we will do that in the recommendations step!
            )
            db.add(new_resource)
            
        db.commit()
        return {"message": "Mock data synced successfully!", "resources_added": len(data)}
        
    else:
        # This is where the real AWS logic goes later when we have a real account
        return {"message": "Real AWS sync triggered (Logic pending)"}

@router.get("/resources")
def get_user_resources(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Returns all resources currently saved in the database for the logged-in user."""
    resources = db.query(Resource).filter(Resource.user_id == current_user.id).all()
    return resources