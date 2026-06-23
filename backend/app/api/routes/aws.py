from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.schemas.aws import AWSCredentialsInput
from app.utils.encryption import encrypt_value

router = APIRouter()

# 5. POST route to save and encrypt keys
@router.post("/credentials")
def save_credentials(
    creds: AWSCredentialsInput, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Scramble the keys before they ever touch the database
    encrypted_access = encrypt_value(creds.access_key)
    encrypted_secret = encrypt_value(creds.secret_key)
    
    # Save them to the user's row
    current_user.aws_access_key = encrypted_access
    current_user.aws_secret_key = encrypted_secret
    db.commit()
    
    return {"message": "AWS credentials encrypted and saved securely."}

# 6. GET route to check status WITHOUT revealing the keys
@router.get("/credentials/status")
def check_credentials_status(current_user: User = Depends(get_current_user)):
    # Returns True if both columns have data, False if they are empty
    has_keys = bool(current_user.aws_access_key and current_user.aws_secret_key)
    return {"has_credentials": has_keys}

# 7. DELETE route to wipe the keys
@router.delete("/credentials")
def delete_credentials(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    current_user.aws_access_key = None
    current_user.aws_secret_key = None
    db.commit()
    
    return {"message": "AWS credentials removed successfully."}