import os
import sys
from sqlalchemy import and_

# Bridge to backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
from app.db.session import SessionLocal
from app.db.models.resource import Resource
from app.db.models.anomaly import Anomaly
from app.db.models.recommendation import Recommendation
from backend.ml.base_model import CloudMLModel

class RecommendationEngine(CloudMLModel):
    def run(self, user_id: int):
        db = SessionLocal()
        try:
            resources = db.query(Resource).filter(Resource.user_id == user_id).all()
            recommendations = []

            for r in resources:
                # Rule 1: Idle resource
                if r.status == 'idle' and (r.monthly_cost or 0) > 50:
                    recommendations.append({
                        "resource_id": str(r.resource_id),
                        "title": "Terminate Idle Resource",
                        "desc": "Resource is idle and incurring cost.",
                        "saving": r.monthly_cost * 0.90
                    })
                
                # Rule 2: Overprovisioned
                if r.status == 'overprovisioned' and (r.avg_cpu_percent or 0) < 20:
                    recommendations.append({
                        "resource_id": str(r.resource_id),
                        "title": "Downsize Instance",
                        "desc": "CPU utilization is low. Consider downsizing.",
                        "saving": r.monthly_cost * 0.50
                    })

                # Rule 3: Staging/Dev Always-on
                if r.status == 'idle' and any(x in r.name.lower() for x in ['staging', 'dev']):
                    recommendations.append({
                        "resource_id": str(r.resource_id),
                        "title": "Schedule Off-Hours",
                        "desc": "This dev resource can be scheduled off.",
                        "saving": r.monthly_cost * 0.65
                    })

                # Rule 4: Runaway processes (Anomaly Check)
                high_anomalies = db.query(Anomaly).filter(and_(
                    Anomaly.resource_id == r.resource_id,
                    Anomaly.severity == 'high'
                )).count()
                
                if high_anomalies > 2:
                    recommendations.append({
                        "resource_id": str(r.resource_id),
                        "title": "Investigate Anomaly",
                        "desc": "Multiple high-severity anomalies detected.",
                        "saving": r.monthly_cost * 0.20
                    })

            self.save_results(user_id, recommendations, db)
        finally:
            db.close()

    def save_results(self, user_id, recommendations, db):
        for rec in recommendations:
            # Upsert logic - checks if a recommendation for this resource/title exists
            existing = db.query(Recommendation).filter(and_(
                Recommendation.resource_id == rec['resource_id'],
                Recommendation.title == rec['title']
            )).first()
            
            priority = "Low"
            if rec['saving'] > 300: priority = "High"
            elif rec['saving'] > 100: priority = "Medium"

            if existing:
                existing.saving_amount = rec['saving']
                existing.priority = priority
            else:
                db.add(Recommendation(
                    user_id=user_id, 
                    resource_id=rec['resource_id'],
                    title=rec['title'],
                    description=rec['desc'],
                    saving_amount=rec['saving'], 
                    priority=priority,
                    status="pending"
                ))
        db.commit()