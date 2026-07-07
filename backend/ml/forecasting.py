import pandas as pd
import numpy as np
from prophet import Prophet
import joblib
import os
import sys
from datetime import datetime

# Bridge to the backend database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.forecast import Forecast
from app.db.models.resource import Resource

from backend.ml.base_model import CloudMLModel
from backend.ml.data_loader import MLDataLoader

class CostForecaster(CloudMLModel):
    def __init__(self):
        self.loader = MLDataLoader()
        self.models_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(self.models_dir, exist_ok=True)

    def run(self, user_id: int):
        """Executes the Prophet forecasting algorithm."""
        
        # Step 4: Get historical cost data
        df = self.loader.get_total_daily_cost(user_id)
        
        # Prophet needs at least 30 rows to establish a reliable baseline
        if df.empty or len(df) < 30:
            print("Not enough history for forecasting. Need at least 30 days of data.")
            return []

        # Step 5: Initialize Prophet Model
        # We tell Prophet to expect weekly patterns, but ignore daily/yearly patterns for now
        model = Prophet(
            weekly_seasonality=True, 
            yearly_seasonality=False, 
            daily_seasonality=False
        )
        
        # Step 6: Add custom seasonality to catch monthly billing cycles
        model.add_seasonality(name='monthly', period=30.5, fourier_order=5)
        
        # Step 7: Fit the AI on our historical DataFrame
        model.fit(df)
        
        # Step 8: Forecast 30 days into the future
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        
        # Step 9: Extract ONLY the future rows (where dates are greater than our latest historical date)
        last_historical_date = df['ds'].max()
        future_forecast = forecast[forecast['ds'] > last_historical_date].copy()
        
        # Select and clean the specific columns we want for the database
        results = []
        for _, row in future_forecast.iterrows():
            results.append({
                "forecast_date": row['ds'].date(),               # 'ds' is the datestamp
                "predicted_cost": round(float(row['yhat']), 2),  # 'yhat' is Prophet's prediction
                "lower_bound": round(float(row['yhat_lower']), 2),
                "upper_bound": round(float(row['yhat_upper']), 2)
            })
            
        # Save the trained model to disk for fast API re-use later
        joblib.dump(model, os.path.join(self.models_dir, 'prophet_model.pkl'))
        
        # Step 10: Save to database
        if results:
            self.save_results(user_id, results)
        
        return results

    def save_results(self, user_id: int, results: list):
        """Step 10: Delete old forecasts and insert the fresh 30-day forecast."""
        db = SessionLocal()
        try:
            # Delete old forecasts for this user so we don't have overlapping data
            db.query(Forecast).filter(Forecast.user_id == user_id).delete()
            
            # Insert the fresh predictions
            new_forecasts = []
            for r in results:
                new_forecasts.append(
                    Forecast(
                        user_id=user_id,
                        forecast_date=r['forecast_date'],
                        predicted_cost=r['predicted_cost'],
                        lower_bound=r['lower_bound'],
                        upper_bound=r['upper_bound']
                    )
                )
            
            db.add_all(new_forecasts)
            db.commit()
            print(f"Saved {len(new_forecasts)} days of forecasted costs to the database.")
            
        except Exception as e:
            db.rollback()
            print(f"Error saving forecasts to DB: {e}")
            raise
        finally:
            db.close()

    def get_forecast_summary(self, user_id: int) -> dict:
        """Step 11: Returns total predicted cost and projected savings based on AI clusters."""
        db = SessionLocal()
        try:
            # 1. Sum up the entire 30-day predicted cost
            forecasts = db.query(Forecast).filter(Forecast.user_id == user_id).all()
            total_predicted = sum(f.predicted_cost for f in forecasts)
            
            # 2. Calculate potential savings by looking at the K-Means cluster results
            resources = db.query(Resource).filter(Resource.user_id == user_id).all()
            projected_savings = 0.0
            
            for r in resources:
                if r.status == 'idle':
                    # If we terminate idle servers, we save 100% of their cost
                    projected_savings += (r.monthly_cost or 0.0)
                elif r.status == 'overprovisioned':
                    # If we downsize overprovisioned servers, we assume we save 50%
                    projected_savings += (r.monthly_cost or 0.0) * 0.5
                    
            return {
                "total_predicted_30d_cost": round(total_predicted, 2),
                "projected_30d_savings": round(projected_savings, 2)
            }
        finally:
            db.close()

# --- TEST SCRIPT ---
if __name__ == "__main__":
    print("=" * 60)
    print("Initializing Meta Prophet Forecasting AI...")
    forecaster = CostForecaster()
    
    print("\n--- Training Model & Predicting Next 30 Days ---")
    results = forecaster.run(user_id=1)
    
    if results:
        print("\n--- 30-Day Cost Forecast (First 7 Days) ---")
        print(f"{'Date':<15} {'Predicted':<12} {'Lower Bound':<15} {'Upper Bound'}")
        print("-" * 60)
        
        for r in results[:7]: 
            print(f"{str(r['forecast_date']):<15} ${r['predicted_cost']:<11.2f} ${r['lower_bound']:<14.2f} ${r['upper_bound']:.2f}")
        print("... (forecast continues for 30 days)\n")
        
        summary = forecaster.get_forecast_summary(user_id=1)
        print("--- Financial Summary ---")
        print(f"Total Predicted Spend (Next 30 Days): ${summary['total_predicted_30d_cost']}")
        print(f"Potential Savings (If Optimized):     ${summary['projected_30d_savings']}")
    print("=" * 60)