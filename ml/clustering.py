import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# Bridge to the backend database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.db.session import SessionLocal
from app.db.models.resource import Resource

from ml.base_model import CloudMLModel
from ml.data_loader import MLDataLoader

class ResourceClusterer(CloudMLModel):
    def __init__(self):
        self.loader = MLDataLoader()
        self.scaler = StandardScaler()
        # K-Means configured for 3 clusters (Idle, Healthy, Overprovisioned)
        self.model = KMeans(n_clusters=3, random_state=42, n_init=10)
        
        # Ensure the directory for saving our fitted models exists
        self.models_dir = os.path.join(os.path.dirname(__file__), 'saved_models')
        os.makedirs(self.models_dir, exist_ok=True)

    def run(self, user_id: int):
        """Executes the clustering algorithm."""
        
        # Step 2: Get the DataFrame
        df = self.loader.get_resources(user_id)
        if df.empty:
            return []

        # Step 3: Feature Engineering
        features = ['monthly_cost', 'avg_cpu_percent', 'hours_active']
        X = df[features]

        # Step 4: Normalize data so Cost and CPU are weighted equally
        X_scaled = self.scaler.fit_transform(X)

        # Step 5: Fit the model and assign clusters to each server
        clusters = self.model.fit_predict(X_scaled)
        df['cluster'] = clusters

        # Step 6: Label clusters dynamically by looking at their Centroids
        # Inverse transform brings our pins back to human-readable numbers (like 15% CPU instead of -1.2)
        centroids = self.scaler.inverse_transform(self.model.cluster_centers_)
        
        # 'avg_cpu_percent' is at index 1 of our features list
        # Let's map out which cluster index (0, 1, or 2) has which CPU usage
        centroid_cpus = [(idx, centroid) for idx, centroid in enumerate(centroids)]
        
        # Sort them from lowest CPU to highest CPU
        centroid_cpus.sort(key=lambda x: x)
        
        idle_idx = centroid_cpus          # Lowest CPU -> Idle
        overprov_idx = centroid_cpus      # Middle CPU -> Overprovisioned
        healthy_idx = centroid_cpus       # Highest CPU -> Healthy

        # Create a dictionary to instantly map the math output to our database status strings
        label_map = {
            idle_idx: 'idle',
            healthy_idx: 'healthy',
            overprov_idx: 'overprovisioned'
        }
        
        # Apply the labels to the DataFrame
        df['cluster_label'] = df['cluster'].map(label_map)

        # Step 8: Save the fitted scaler and model so we don't have to retrain on every API call
        joblib.dump(self.scaler, os.path.join(self.models_dir, 'scaler.pkl'))
        joblib.dump(self.model, os.path.join(self.models_dir, 'kmeans.pkl'))

        # Prepare results
        results = df.to_dict('records')
        
        # Step 7: Save labels back into PostgreSQL
        self.save_results(user_id, results)
        
        # Step 10: Expose clean results for the API
        final_results = []
        for r in results:
            final_results.append({
                "resource_id": r['resource_id'],
                "name": r['name'],
                "cluster_label": r['cluster_label'],
                "monthly_cost": r['monthly_cost'],
                "avg_cpu_percent": r['avg_cpu_percent']
            })
        return final_results

    def save_results(self, user_id: int, results):
        """Step 7: Updates the Resource.status column in the database."""
        db = SessionLocal()
        try:
            for r in results:
                db_resource = db.query(Resource).filter(
                    Resource.user_id == user_id, 
                    Resource.resource_id == r['resource_id']
                ).first()
                if db_resource:
                    db_resource.status = r['cluster_label'] # Save 'idle', 'healthy', or 'overprovisioned'
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error saving to DB: {e}")
        finally:
            db.close()
            
    def get_cluster_summary(self, user_id: int):
        """Step 9: Returns the count and total cost of each cluster for the dashboard."""
        db = SessionLocal()
        try:
            resources = db.query(Resource).filter(Resource.user_id == user_id).all()
            
            summary = {
                "idle": {"count": 0, "total_cost": 0.0},
                "healthy": {"count": 0, "total_cost": 0.0},
                "overprovisioned": {"count": 0, "total_cost": 0.0}
            }
            
            for r in resources:
                if r.status in summary:
                    summary[r.status]["count"] += 1
                    summary[r.status]["total_cost"] += r.monthly_cost
                    
            # Round costs for clean UI
            for key in summary.keys():
                summary[key]["total_cost"] = round(summary[key]["total_cost"], 2)
                
            return summary
        finally:
            db.close()

# --- TEST SCRIPT ---
if __name__ == "__main__":
    print("Initializing AI Clustering Model...")
    clusterer = ResourceClusterer()
    
    # 1. Run the Elbow Method to prove K=3 is the best mathematical choice
    print("\n--- Running Elbow Method (Inertia) ---")
    df = clusterer.loader.get_resources(user_id=1)
    X_scaled = clusterer.scaler.fit_transform(df[['monthly_cost', 'avg_cpu_percent', 'hours_active']])
    
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        print(f"k={k} Clusters: Inertia Score = {round(km.inertia_, 2)}")
        
    # 2. Run the actual model
    print("\n--- Running K-Means Predictions ---")
    results = clusterer.run(user_id=1)
    
    print(f"Successfully clustered {len(results)} servers.")
    for res in results[:3]: # Print first 3 to verify
        print(f"Server {res['resource_id']} assigned to: {res['cluster_label'].upper()} (CPU: {res['avg_cpu_percent']}%)")
        
    # 3. Check the summary
    print("\n--- Final Dashboard Summary ---")
    print(clusterer.get_cluster_summary(user_id=1))