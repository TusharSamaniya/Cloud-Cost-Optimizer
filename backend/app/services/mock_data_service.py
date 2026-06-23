import random

def get_mock_resources():
    """Generates 10 highly realistic fake EC2 instances with randomized costs and CPU usage."""
    resources = []
    
    for i in range(1, 11):
        # Alternate between cheap micro servers and expensive large servers
        res_type = "t3.micro" if i % 2 == 0 else "m5.large"
        
        resources.append({
            "resource_id": f"i-0abcd1234fake{i:02d}",
            "service_name": "EC2",
            "resource_type": res_type,
            "region": "us-east-1",
            # Randomize cost between $5 and $100
            "cost_amount": round(random.uniform(5.0, 100.0), 2),
            # Randomize CPU usage between 5% and 98%
            "cpu_utilization": round(random.uniform(5.0, 98.0), 2)
        })
        
    return resources