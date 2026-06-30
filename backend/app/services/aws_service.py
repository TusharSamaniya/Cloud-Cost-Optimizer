import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
from fastapi import HTTPException
from app.db.models.user import User
from app.utils.encryption import decrypt_value
from datetime import datetime, timedelta


def get_boto3_client(user: User, service_name: str = "ce"):
    """
    Decrypts the user's keys and returns an active boto3 client.
    'ce' stands for Cost Explorer.
    """
    if not user.aws_access_key or not user.aws_secret_key:
        raise HTTPException(status_code=400, detail="AWS credentials not found. Please add them first.")

    try:
        decrypted_access = decrypt_value(user.aws_access_key)
        decrypted_secret = decrypt_value(user.aws_secret_key)

        client = boto3.client(
            service_name,
            aws_access_key_id=decrypted_access,
            aws_secret_access_key=decrypted_secret,
            region_name="us-east-1"
        )
        return client
    except Exception:
        raise HTTPException(status_code=401, detail="Failed to initialize AWS client. Keys might be invalid.")


# ---------------------------------------------------------------------------
# BUG FIXED: fetch_ec2_instances, fetch_cost_explorer and fetch_cloudwatch_metrics
# were all indented INSIDE get_boto3_client() in the original file (notice the
# extra 4-space indent before "def fetch_ec2_instances"). This made them local
# functions trapped inside get_boto3_client that could NEVER be called or
# imported from outside — which is exactly why "from app.services.aws_service
# import fetch_ec2_instances" would fail and real AWS sync always errored out.
#
# They are now top-level functions, properly de-indented, and each one wraps
# its boto3 call in a try/except that raises a CLEAR, SPECIFIC error message
# instead of a generic "Invalid credentials" — so the frontend can show the
# user exactly what went wrong (expired keys vs no permissions vs no internet).
# ---------------------------------------------------------------------------

def fetch_ec2_instances(user: User):
    """Fetches a list of all running EC2 servers and shapes them to match the Resource model."""
    client = get_boto3_client(user, "ec2")

    try:
        response = client.describe_instances()
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("AuthFailure", "UnrecognizedClientException", "InvalidClientTokenId"):
            raise HTTPException(status_code=401, detail="Invalid AWS credentials. Please check your Access Key and Secret Key.")
        elif error_code in ("UnauthorizedOperation", "AccessDenied"):
            raise HTTPException(status_code=403, detail="Insufficient IAM permissions. Your key needs EC2 read-only access.")
        else:
            raise HTTPException(status_code=400, detail=f"AWS error: {error_code}")
    except NoCredentialsError:
        raise HTTPException(status_code=401, detail="No AWS credentials provided.")
    except EndpointConnectionError:
        raise HTTPException(status_code=503, detail="Could not reach AWS. Check your internet connection.")

    instances = []
    for reservation in response.get('Reservations', []):
        for inst in reservation.get('Instances', []):
            # Only include running instances — terminated/stopped ones aren't costing money
            state = inst.get("State", {}).get("Name")
            if state != "running":
                continue

            instances.append({
                "resource_id": inst.get("InstanceId"),
                "name": next(
                    (tag["Value"] for tag in inst.get("Tags", []) if tag["Key"] == "Name"),
                    inst.get("InstanceId")
                ),
                "type": inst.get("InstanceType"),
                "region": inst.get("Placement", {}).get("AvailabilityZone", "us-east-1")[:-1],
                "monthly_cost": 0.0,        # filled in by fetch_cost_explorer pass
                "avg_cpu_percent": 0.0,     # filled in by fetch_cloudwatch_metrics pass
                "status": "healthy",        # default until ML pipeline relabels it
            })
    return instances


def fetch_cost_explorer(user: User):
    """Fetches the daily cost for the last 30 days."""
    client = get_boto3_client(user, "ce")

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)

    try:
        response = client.get_cost_and_usage(
            TimePeriod={'Start': start_date.isoformat(), 'End': end_date.isoformat()},
            Granularity='DAILY',
            Metrics=['UnblendedCost']
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "AccessDeniedException":
            raise HTTPException(status_code=403, detail="Your IAM user needs 'ce:GetCostAndUsage' permission.")
        raise HTTPException(status_code=400, detail=f"Cost Explorer error: {error_code}")

    return response.get('ResultsByTime', [])


def fetch_cloudwatch_metrics(user: User, instance_id: str):
    """Fetches the average CPU usage for a specific server over the last 7 days."""
    client = get_boto3_client(user, "cloudwatch")

    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)

    try:
        response = client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=86400,
            Statistics=['Average']
        )
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        raise HTTPException(status_code=400, detail=f"CloudWatch error: {error_code}")

    datapoints = response.get('Datapoints', [])
    if not datapoints:
        return 0.0

    avg_cpu = sum(d['Average'] for d in datapoints) / len(datapoints)
    return round(avg_cpu, 2)
