import boto3
from fastapi import HTTPException
from app.db.models.user import User
from app.utils.encryption import decrypt_value
from datetime import datetime, timedelta

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
    
    def fetch_ec2_instances(user: User):
    """Fetches a list of all running EC2 servers."""
    client = get_boto3_client(user, "ec2")
    response = client.describe_instances()
    
    instances = []
    # AWS returns data in a deeply nested dictionary, so we loop through to extract what we need
    for reservation in response.get('Reservations', []):
        for inst in reservation.get('Instances', []):
            instances.append({
                "resource_id": inst.get("InstanceId"),
                "resource_type": inst.get("InstanceType"),
                "state": inst.get("State", {}).get("Name"),
            })
    return instances

def fetch_cost_explorer(user: User):
    """Fetches the daily cost for the last 30 days."""
    client = get_boto3_client(user, "ce")
    
    # Calculate dates for the last 30 days
    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=30)
    
    response = client.get_cost_and_usage(
        TimePeriod={'Start': start_date.isoformat(), 'End': end_date.isoformat()},
        Granularity='DAILY',
        Metrics=['UnblendedCost']
    )
    return response.get('ResultsByTime', [])

def fetch_cloudwatch_metrics(user: User, instance_id: str):
    """Fetches the average CPU usage for a specific server over the last 7 days."""
    client = get_boto3_client(user, "cloudwatch")
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    
    response = client.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=start_time,
        EndTime=end_time,
        Period=86400, # 86400 seconds = 1 Day
        Statistics=['Average']
    )
    return response.get('Datapoints', [])