import logging
import os
import sys

# Make the ml package importable when this is called from the backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_full_pipeline(user_id: int) -> dict:
    """
    Runs all 4 ML models in the correct order for one user.

    Order matters:
      1. Clustering  — labels every resource as idle/healthy/overprovisioned
      2. Anomaly     — detects cost spikes (independent of clustering)
      3. Forecasting — predicts next 30 days of spend (independent)
      4. Recommendations — reads cluster labels written in step 1, generates actions

    Each step is wrapped in its own try/except so one failure
    does not prevent the remaining models from running.
    """
    from backend.ml.clustering        import ResourceClusterer
    from backend.ml.anomaly_detection import AnomalyDetector
    from backend.ml.forecasting       import CostForecaster
    from backend.ml.recommendations   import RecommendationEngine

    # Define pipeline steps in execution order
    steps = [
        ("Clustering",       ResourceClusterer()),
        ("Anomaly Detection", AnomalyDetector()),
        ("Forecasting",      CostForecaster()),
        ("Recommendations",  RecommendationEngine()),
    ]

    results = {}   # track which steps passed/failed — useful for the API response

    for step_name, model in steps:
        logger.info(f"[Pipeline] user_id={user_id} — starting {step_name}...")
        try:
            model.run(user_id)
            logger.info(f"[Pipeline] user_id={user_id} — {step_name} ✓")
            results[step_name] = "success"
        except Exception as e:
            logger.error(f"[Pipeline] user_id={user_id} — {step_name} FAILED: {e}")
            results[step_name] = f"failed: {str(e)}"
            continue   # always move to the next step

    logger.info(f"[Pipeline] user_id={user_id} — all steps done. Results: {results}")
    return results   # returned to the API route so the response is informative


# ---------------------------------------------------------------------------
# Quick test — run directly to verify pipeline works end to end
# cd backend && python ../ml/pipeline.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Running full ML pipeline for user_id=1...")
    outcome = run_full_pipeline(user_id=1)
    print("\nPipeline outcome:")
    for step, status in outcome.items():
        icon = "✓" if status == "success" else "✗"
        print(f"  {icon}  {step}: {status}")