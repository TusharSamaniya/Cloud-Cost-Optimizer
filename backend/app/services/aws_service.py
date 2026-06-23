import boto3
from fastapi import HTTPException
from app.db.models.user import User
from app.utils.encryption import decrypt_value

def get_boto3_client(user: User, service_name: str = "ce"):
    """
    Decrypts the user's keys and returns an active boto3 client.
    'ce' stands for Cost Explorer (which we will use later).
    """
    # 1. Ensure the user actually saved their keys
    if not user.aws_access_key or not user.aws_secret_key:
        raise HTTPException(status_code=400, detail="AWS credentials not found. Please add them first.")

    try:
        # 2. Unscramble the keys using our Master Key
        decrypted_access = decrypt_value(user.aws_access_key)
        decrypted_secret = decrypt_value(user.aws_secret_key)

        # 3. Create a unique AWS connection just for this user
        client = boto3.client(
            service_name,
            aws_access_key_id=decrypted_access,
            aws_secret_access_key=decrypted_secret,
            region_name="us-east-1" 
        )
        return client
    except Exception as e:
        raise HTTPException(status_code=401, detail="Failed to initialize AWS client. Keys might be invalid.")