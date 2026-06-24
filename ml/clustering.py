import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import joblib
import os
import sys

# Bridge to the backend database
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
# Bridge to the root folder so Python finds the 'ml' module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import SessionLocal
from app.db.models.resource import Resource
from app.db.models.user import User

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

        # Step 1: Get the DataFrame from the database via our data loader
        df = self.loader.get_resources(user_id)
        if df.empty:
            print(f"No resources found for user_id={user_id}. Skipping clustering.")
            return []

        # Step 2: Feature Engineering
        # These 3 features are what the model uses to decide which cluster a resource belongs to
        features = ['monthly_cost', 'avg_cpu_percent', 'hours_active']
        X = df[features].copy()

        # Step 3: Normalize features with StandardScaler
        # Without this, monthly_cost (e.g. 1500) would dominate avg_cpu_percent (e.g. 4)
        # After scaling, all 3 features contribute equally to the clustering decision
        X_scaled = self.scaler.fit_transform(X)

        # Step 4: Fit K-Means and assign each resource to a cluster (0, 1, or 2)
        # fit_predict trains the model AND returns the cluster label for each row in one step
        clusters = self.model.fit_predict(X_scaled)
        df = df.copy()  # avoid SettingWithCopyWarning
        df['cluster'] = clusters

        # -----------------------------------------------------------------------
        # Step 5: Label clusters by their centroid CPU value
        #
        # The cluster numbers (0, 1, 2) from K-Means are arbitrary — the model
        # doesn't know what "idle" means. We figure out which number means which
        # label by looking at each cluster's average (centroid) CPU usage:
        #   lowest  CPU centroid → idle
        #   middle  CPU centroid → overprovisioned
        #   highest CPU centroid → healthy
        # -----------------------------------------------------------------------

        # inverse_transform converts the scaled centroid coordinates back to
        # real-world numbers (dollars and percentages) so we can read them
        centroids = self.scaler.inverse_transform(self.model.cluster_centers_)

        # Build a list of (cluster_index, cpu_value) tuples
        # centroids has shape (3, 3) → 3 clusters × 3 features [cost, cpu, hours]
        # We pick index 1 to grab the CPU column specifically
        centroid_cpus = []
        for cluster_idx, centroid in enumerate(centroids):
            cpu_value = centroid[1]  # FIX 1: index [1] = avg_cpu_percent column
            centroid_cpus.append((cluster_idx, cpu_value))

        # Sort the list by cpu_value (ascending) so position 0 = lowest CPU
        centroid_cpus.sort(key=lambda x: x[1])  # FIX 2: sort by x[1] (the cpu value), not the whole tuple

        # Now extract the actual cluster index integer from each sorted position
        # centroid_cpus[0] = (cluster_idx, cpu_value) for lowest  CPU → idle
        # centroid_cpus[1] = (cluster_idx, cpu_value) for middle  CPU → overprovisioned
        # centroid_cpus[2] = (cluster_idx, cpu_value) for highest CPU → healthy
        idle_idx     = int(centroid_cpus[0][0])  # FIX 3: [position][0] gets the cluster index integer
        overprov_idx = int(centroid_cpus[1][0])
        healthy_idx  = int(centroid_cpus[2][0])

        # Map each cluster number → its human-readable label string
        label_map = {
            idle_idx:     'idle',
            overprov_idx: 'overprovisioned',
            healthy_idx:  'healthy',
        }

        # Apply the label map to the cluster column to create cluster_label
        df['cluster_label'] = df['cluster'].map(label_map)

        # -----------------------------------------------------------------------
        # Step 6: Save the fitted scaler and model to disk
        # We save them so that when a new resource arrives we can classify it
        # instantly using predict() without retraining the whole model
        # -----------------------------------------------------------------------
        joblib.dump(self.scaler, os.path.join(self.models_dir, 'scaler.pkl'))
        joblib.dump(self.model,  os.path.join(self.models_dir, 'kmeans.pkl'))
        print("Models saved to ml/saved_models/")

        # Step 7: Save the cluster labels back to PostgreSQL
        results = df.to_dict('records')
        self.save_results(user_id, results)

        # Step 8: Return a clean list of dicts for the API route to return as JSON
        final_results = []
        for r in results:
            final_results.append({
                "resource_id":     r['resource_id'],
                "name":            r['name'],
                "cluster_label":   r['cluster_label'],
                "monthly_cost":    round(r['monthly_cost'], 2),
                "avg_cpu_percent": round(r['avg_cpu_percent'], 2),
            })
        return final_results

    def save_results(self, user_id: int, results: list):
        """Updates the Resource.status column in PostgreSQL for every resource."""
        db = SessionLocal()
        try:
            for r in results:
                db_resource = db.query(Resource).filter(
                    Resource.user_id == user_id,
                    Resource.resource_id == r['resource_id']
                ).first()
                if db_resource:
                    db_resource.status = r['cluster_label']  # 'idle' / 'healthy' / 'overprovisioned'
            db.commit()
            print(f"Saved cluster labels for {len(results)} resources to database.")
        except Exception as e:
            db.rollback()
            print(f"Database error in save_results: {e}")
            raise
        finally:
            db.close()

    def get_cluster_summary(self, user_id: int) -> dict:
        """Returns count + total_cost per cluster — used by the dashboard summary API."""
        db = SessionLocal()
        try:
            resources = db.query(Resource).filter(Resource.user_id == user_id).all()

            summary = {
                "idle":            {"count": 0, "total_cost": 0.0},
                "healthy":         {"count": 0, "total_cost": 0.0},
                "overprovisioned": {"count": 0, "total_cost": 0.0},
            }

            for r in resources:
                if r.status in summary:
                    summary[r.status]["count"]      += 1
                    summary[r.status]["total_cost"] += r.monthly_cost or 0.0

            # Round costs for clean JSON output
            for key in summary:
                summary[key]["total_cost"] = round(summary[key]["total_cost"], 2)

            return summary
        finally:
            db.close()


# ---------------------------------------------------------------------------
# TEST SCRIPT — only runs when you execute this file directly:
#   cd backend
#   python ../ml/clustering.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("Initializing ResourceClusterer...")
    clusterer = ResourceClusterer()

    # 1. Elbow method — proves K=3 is a good choice
    print("\n--- Elbow Method (lower inertia = tighter clusters) ---")
    df = clusterer.loader.get_resources(user_id=1)
    if df.empty:
        print("No resources in database. Run your sync endpoint first.")
        sys.exit(1)

    X_scaled = clusterer.scaler.fit_transform(df[['monthly_cost', 'avg_cpu_percent', 'hours_active']])
    for k in range(2, 7):
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(X_scaled)
        print(f"  k={k} → inertia = {round(km.inertia_, 2)}")

    # 2. Run the actual clustering
    print("\n--- Running K-Means Clustering ---")
    results = clusterer.run(user_id=1)
    print(f"\nClustered {len(results)} resources successfully.\n")

    print(f"{'Resource':<30} {'Label':<18} {'CPU %':>6}  {'Cost':>8}")
    print("-" * 68)
    for r in results:
        print(f"{r['name']:<30} {r['cluster_label']:<18} {r['avg_cpu_percent']:>6.1f}%  ${r['monthly_cost']:>7.2f}")

    # 3. Dashboard summary
    print("\n--- Cluster Summary ---")
    summary = clusterer.get_cluster_summary(user_id=1)
    for label, data in summary.items():
        print(f"  {label:<18} count={data['count']}  total_cost=${data['total_cost']}")
    print("=" * 50)