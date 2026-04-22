from datetime import timedelta
from sqlalchemy.orm import Session
import models

def generate_prediction(node_id: str, db: Session):
    """
    Fetches the latest readings for a node and calculates a basic prediction.
    """
    # Fetch the 5 most recent readings for this specific node
    recent_readings = db.query(models.TrafficReading)\
        .filter(models.TrafficReading.node_id == node_id)\
        .order_by(models.TrafficReading.timestamp.desc())\
        .limit(5).all()

    if not recent_readings:
        return None

    # Calculate moving average of speed
    avg_speed = sum(r.speed for r in recent_readings) / len(recent_readings)
    
    # Target time is 1 hour in the future
    latest_time = recent_readings[0].timestamp
    future_time = latest_time + timedelta(hours=1)

    if avg_speed < 20.0:
        level = "High"
        confidence = 85.0
    elif avg_speed < 40.0:
        level = "Medium"
        confidence = 75.0
    else:
        level = "Low"
        confidence = 90.0

    # Create the database record
    prediction = models.CongestionPrediction(
        node_id=node_id,
        target_time=future_time,
        predicted_level=level,
        confidence_score=confidence
    )
    
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    
    return prediction