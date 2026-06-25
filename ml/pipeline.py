import logging
from ml.clustering import ResourceClusterer
from ml.anomaly_detection import AnomalyDetector
from ml.forecasting import CostForecaster
from ml.recommendations import RecommendationEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_full_pipeline(user_id: int):
    """Runs all ML models in the correct logical sequence."""
    steps = [
        ("Clustering", ResourceClusterer()),
        ("Anomaly Detection", AnomalyDetector()),
        ("Forecasting", CostForecaster()),
        ("Recommendations", RecommendationEngine())
    ]

    for name, model in steps:
        try:
            logger.info(f"Starting {name} for user {user_id}...")
            model.run(user_id)
            logger.info(f"Successfully completed {name}.")
        except Exception as e:
            logger.error(f"Error in {name}: {str(e)}")
            # Continue to next step even if this one fails
            continue