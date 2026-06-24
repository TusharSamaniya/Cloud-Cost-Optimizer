import pandas as pd
from sklearn.ensemble import IsolationForest
import os
import sys

# Bridge to the backend database
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "backend")
    )
)
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from app.db.session import SessionLocal
from app.db.models.anomaly import Anomaly

from ml.base_model import CloudMLModel
from ml.data_loader import MLDataLoader


class AnomalyDetector(CloudMLModel):

    def __init__(self):
        self.loader = MLDataLoader()

    def run(self, user_id: int):
        """Executes the anomaly detection algorithm."""

        # Load data
        df = self.loader.get_daily_costs(user_id)

        if df.empty:
            print("No daily cost data found.")
            return []

        # Validate required columns
        required_cols = ["date", "resource_id", "daily_cost"]

        missing_cols = [
            col for col in required_cols if col not in df.columns
        ]

        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}"
            )

        # Convert date column
        df["date"] = pd.to_datetime(df["date"])

        # Feature Engineering
        df["day_of_week"] = df["date"].dt.dayofweek

        # Saturday = 5, Sunday = 6
        df["is_weekend"] = (
            df["day_of_week"]
            .isin([5, 6])
            .astype(int)
        )

        all_anomalies = []

        # Run model separately for each resource
        for res_id in df["resource_id"].unique():

            res_df = (
                df[df["resource_id"] == res_id]
                .copy()
                .sort_values("date")
                .reset_index(drop=True)
            )

            # Need enough history
            if len(res_df) < 7:
                continue

            features = [
                "daily_cost",
                "day_of_week",
                "is_weekend"
            ]

            X = res_df[features].fillna(0)

            # Isolation Forest
            model = IsolationForest(
                contamination=0.05,
                random_state=42
            )

            res_df["anomaly_label"] = model.fit_predict(X)

            res_df["anomaly_score"] = (
                model.decision_function(X)
            )

            # Historical normal costs only
            normal_costs = res_df["daily_cost"].where(
                res_df["anomaly_label"] == 1
            )

            res_df["expected_cost"] = (
                normal_costs
                .ffill()
                .rolling(window=7, min_periods=1)
                .mean()
                .shift(1)
            )

            res_df["expected_cost"] = (
                res_df["expected_cost"]
                .bfill()
                .fillna(0)
            )

            anomaly_days = res_df[
                res_df["anomaly_label"] == -1
            ]

            for _, row in anomaly_days.iterrows():

                actual = float(row["daily_cost"])
                expected = float(row["expected_cost"])

                # Ignore drops and invalid expected values
                if expected <= 0:
                    continue

                if actual <= expected:
                    continue

                percent_diff = (
                    actual - expected
                ) / expected

                if percent_diff > 1.0:
                    severity = "high"
                elif percent_diff >= 0.3:
                    severity = "medium"
                else:
                    severity = "low"

                all_anomalies.append(
                    {
                        "resource_id": res_id,
                        "detected_at": row["date"].date(),
                        "actual_cost": round(actual, 2),
                        "expected_cost": round(expected, 2),
                        "severity": severity,
                    }
                )

        if all_anomalies:
            self.save_results(
                user_id=user_id,
                anomalies=all_anomalies
            )

        return all_anomalies

    def save_results(
        self,
        user_id: int,
        anomalies: list
    ):
        """Save anomalies to database."""

        db = SessionLocal()

        try:
            for anomaly in anomalies:

                existing = (
                    db.query(Anomaly)
                    .filter(
                        Anomaly.user_id == user_id,
                        Anomaly.resource_id
                        == anomaly["resource_id"],
                        Anomaly.detected_at
                        == anomaly["detected_at"],
                    )
                    .first()
                )

                if existing:

                    existing.actual_cost = (
                        anomaly["actual_cost"]
                    )

                    existing.expected_cost = (
                        anomaly["expected_cost"]
                    )

                    existing.severity = (
                        anomaly["severity"]
                    )

                else:

                    db.add(
                        Anomaly(
                            user_id=user_id,
                            resource_id=anomaly["resource_id"],
                            detected_at=anomaly["detected_at"],
                            actual_cost=anomaly["actual_cost"],
                            expected_cost=anomaly["expected_cost"],
                            severity=anomaly["severity"],
                        )
                    )

            db.commit()

        except Exception as e:
            db.rollback()
            print(f"Error saving to DB: {e}")
            raise

        finally:
            db.close()


if __name__ == "__main__":

    print("Initializing Isolation Forest AI...")

    detector = AnomalyDetector()

    print("\n--- Running Anomaly Detection ---")

    results = detector.run(user_id=1)

    print(
        f"\nSuccessfully detected "
        f"{len(results)} spending spikes."
    )

    if results:

        print(
            f"\n{'Date':<15}"
            f"{'Resource':<15}"
            f"{'Severity':<10}"
            f"{'Expected':<12}"
            f"{'Actual'}"
        )

        print("-" * 70)

        for r in results[:10]:

            print(
                f"{str(r['detected_at']):<15}"
                f"{str(r['resource_id']):<15}"
                f"{r['severity']:<10}"
                f"${r['expected_cost']:<11.2f}"
                f"${r['actual_cost']:.2f}"
            )