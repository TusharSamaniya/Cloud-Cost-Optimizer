import pandas as pd
import numpy as np
import sys
import os

# Add the backend directory to the Python path so we can import our database models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from app.db.session import SessionLocal
from app.db.models.resource import Resource
from app.db.models.user import User

class MLDataLoader:
    def get_resources(self, user_id: int) -> pd.DataFrame:
        """Fetches resources and returns them as a Pandas DataFrame."""
        db = SessionLocal()
        try:
            resources = db.query(Resource).filter(Resource.user_id == user_id).all()
            
            data = []
            for r in resources:
                data.append({
                    "resource_id": r.resource_id,
                    "name": r.name,
                    "type": r.type,
                    "monthly_cost": r.monthly_cost or 0.0,
                    "avg_cpu_percent": r.avg_cpu_percent or 0.0,
                    "region": r.region,
                    "hours_active": 730 # Standard hours in a month for our ML baseline
                })
            
            return pd.DataFrame(data)
        finally:
            db.close()

    def get_daily_costs(self, user_id: int, days: int = 90) -> pd.DataFrame:
        """Simulates historical daily cost data based on the current monthly cost."""
        df_resources = self.get_resources(user_id)
        total_monthly = df_resources['monthly_cost'].sum() if not df_resources.empty else 0
        daily_base = total_monthly / 30.0

        # Generate the last 90 days of dates
        dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
        
        # Add realistic random noise to simulate fluctuating daily AWS usage
        noise = np.random.normal(0, daily_base * 0.1, size=days)
        daily_costs = np.maximum(0, daily_base + noise) # Ensure no negative costs

        return pd.DataFrame({
            'date': dates,
            'resource_id': 'aggregate', 
            'daily_cost': daily_costs
        })

    def get_total_daily_cost(self, user_id: int, days: int = 90) -> pd.DataFrame:
        """Formats the daily cost exactly how the Prophet AI model requires it (ds and y)."""
        df = self.get_daily_costs(user_id, days)
        
        # Prophet strictly requires the date column to be named 'ds' and the value to be 'y'
        prophet_df = df[['date', 'daily_cost']].copy()
        prophet_df.columns = ['ds', 'y']
        
        return prophet_df

# --- STEP 9 TEST SCRIPT ---
# This only runs if you run this file directly!
if __name__ == "__main__":
    print("Testing MLDataLoader...")
    loader = MLDataLoader()
    
    # We will test using user_id 1 (your admin account)
    test_user_id = 1 
    
    df_res = loader.get_resources(test_user_id)
    print(f"\nResource DataFrame Shape: {df_res.shape}")
    print(df_res.head(3)) # Print the first 3 rows
    
    df_prophet = loader.get_total_daily_cost(test_user_id)
    print(f"\nProphet Forecast DataFrame Shape: {df_prophet.shape}")
    print(df_prophet.head(3))