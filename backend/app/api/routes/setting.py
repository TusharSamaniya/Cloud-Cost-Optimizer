from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.core.config import settings

router = APIRouter()


class DemoModeUpdate(BaseModel):
    enabled: bool


@router.get("/demo-mode")
def get_demo_mode(current_user: User = Depends(get_current_user)):
    """
    Returns the current state of USE_MOCK_DATA so the frontend toggle
    reflects the REAL backend state instead of resetting to off on every reload.
    """
    return {"enabled": settings.USE_MOCK_DATA}


@router.post("/demo-mode")
def set_demo_mode(payload: DemoModeUpdate, current_user: User = Depends(get_current_user)):
    """
    Flips USE_MOCK_DATA for the current server process.

    NOTE: this changes the setting in memory for as long as the server runs.
    For a permanent change across restarts, update USE_MOCK_DATA in your .env file.
    This is intentional for a student/demo project — a full production system
    would make this a per-user database column instead of a global server flag.
    """
    settings.USE_MOCK_DATA = payload.enabled
    return {"enabled": settings.USE_MOCK_DATA}
