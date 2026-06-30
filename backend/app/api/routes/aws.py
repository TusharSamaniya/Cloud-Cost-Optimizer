from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.db.models.user import User
from app.schemas.aws import AWSCredentialsInput
from app.utils.encryption import encrypt_value
from app.services.aws_service import get_boto3_client
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError

router = APIRouter()


@router.post("/credentials")
def save_credentials(
    creds: AWSCredentialsInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validates the AWS keys BEFORE saving them, then encrypts and stores them.

    BUG FIXED: the original version saved whatever keys the user typed
    immediately, with zero validation. This is why your screenshot shows
    "Connection failed: Invalid credentials" AFTER save succeeded — bad keys
    were already written to the database, then the next call (sync) failed
    against AWS. Now we test the keys against AWS STS first; if they're
    wrong, we reject immediately and nothing bad gets saved.
    """

    # Step 1 — temporarily build a client with the SUBMITTED (not yet saved) keys
    # to validate them before writing anything to the database
    import boto3
    try:
        sts_client = boto3.client(
            "sts",
            aws_access_key_id=creds.access_key,
            aws_secret_access_key=creds.secret_key,
            region_name="us-east-1",
        )
        identity = sts_client.get_caller_identity()
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("InvalidClientTokenId", "AuthFailure", "SignatureDoesNotMatch"):
            raise HTTPException(status_code=401, detail="Invalid Access Key ID or Secret Access Key.")
        raise HTTPException(status_code=400, detail=f"AWS rejected the credentials: {error_code}")
    except NoCredentialsError:
        raise HTTPException(status_code=400, detail="Access Key and Secret Key are required.")
    except EndpointConnectionError:
        raise HTTPException(status_code=503, detail="Could not reach AWS. Check your internet connection.")

    # Step 2 — keys are valid, NOW encrypt and save them
    current_user.aws_access_key = encrypt_value(creds.access_key)
    current_user.aws_secret_key = encrypt_value(creds.secret_key)
    db.commit()

    return {
        "message": "AWS credentials validated and saved securely.",
        "account_id": identity.get("Account"),
    }


@router.get("/credentials/status")
def check_credentials_status(current_user: User = Depends(get_current_user)):
    has_keys = bool(current_user.aws_access_key and current_user.aws_secret_key)
    return {"has_credentials": has_keys}


@router.delete("/credentials")
def delete_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.aws_access_key = None
    current_user.aws_secret_key = None
    db.commit()
    return {"message": "AWS credentials removed successfully."}
