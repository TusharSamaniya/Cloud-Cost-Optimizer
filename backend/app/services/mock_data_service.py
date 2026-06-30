import random

def get_mock_resources():
    """
    Generates 10 realistic AWS resources with varied costs and CPU usage
    so the ML clustering has meaningful data to work with.
    The spread is intentional:
      - Some resources with high cost + low CPU  → will cluster as 'idle'
      - Some with balanced cost + CPU            → will cluster as 'healthy'  
      - Some with high cost + medium CPU         → will cluster as 'overprovisioned'
    """
    resources = [
        # Idle servers — high cost, very low CPU (waste money)
        {"resource_id": "i-0abc001fake", "service_name": "ml-training-node",    "resource_type": "p3.2xlarge",  "region": "us-east-1", "cost_amount": 1420.00, "cpu_utilization": 4.0},
        {"resource_id": "i-0abc002fake", "service_name": "batch-job-server",    "resource_type": "m5.2xlarge",  "region": "us-east-1", "cost_amount": 620.00,  "cpu_utilization": 3.0},
        {"resource_id": "i-0abc003fake", "service_name": "staging-env-02",      "resource_type": "t3.large",    "region": "us-west-2", "cost_amount": 180.00,  "cpu_utilization": 1.0},
        {"resource_id": "i-0abc004fake", "service_name": "analytics-worker",    "resource_type": "c5.4xlarge",  "region": "us-east-1", "cost_amount": 540.00,  "cpu_utilization": 8.0},

        # Healthy servers — reasonable cost and CPU
        {"resource_id": "i-0abc005fake", "service_name": "web-server-prod-01",  "resource_type": "t3.xlarge",   "region": "us-east-1", "cost_amount": 210.00,  "cpu_utilization": 78.0},
        {"resource_id": "i-0abc006fake", "service_name": "api-gateway-prod",    "resource_type": "t3.medium",   "region": "us-east-1", "cost_amount": 95.00,   "cpu_utilization": 45.0},
        {"resource_id": "i-0abc007fake", "service_name": "redis-cache-01",      "resource_type": "r6g.medium",  "region": "us-west-2", "cost_amount": 310.00,  "cpu_utilization": 22.0},

        # Overprovisioned — decent cost, medium CPU (could use smaller instance)
        {"resource_id": "i-0abc008fake", "service_name": "db-master-01",        "resource_type": "db.m5.2xlarge","region": "us-east-1", "cost_amount": 890.00,  "cpu_utilization": 18.0},
        {"resource_id": "i-0abc009fake", "service_name": "log-archive-server",  "resource_type": "m5.xlarge",   "region": "eu-west-1", "cost_amount": 450.00,  "cpu_utilization": 12.0},
        {"resource_id": "i-0abc010fake", "service_name": "backup-server-prod",  "resource_type": "t3.large",    "region": "us-east-1", "cost_amount": 125.00,  "cpu_utilization": 10.0},
    ]
    return resources
