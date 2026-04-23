from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.orm import Session
import logging
from typing import List, Optional

from schemas import TrafficPayload, TrafficResponse, PredictionResponse
import models
import prediction_logic
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

#Initializing fastAPI app
app = FastAPI(
    title="Pulse Traffic API",
    description="Backend for simulated traffic data ingestion",
    version="1.0.0",
    # openapi_tags=[
    #     {"name": "ingestion", "description": "Endpoints for ingesting traffic data"}
    # ]
)

# Dependency to get the database session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# POST Endpoint to receive traffic data from the simulator
@app.post("/traffic-data", status_code=status.HTTP_201_CREATED)
async def ingest_traffic_data(payload: TrafficPayload, db: Session = Depends(get_db)):
    try:
        new_reading = models.TrafficReading(
            node_id=payload.node_id or "simulator",
            timestamp=payload.timestamp,
            vehicle_count=payload.vehicle_count,
            speed=payload.speed,
            density=payload.density
        )
        db.add(new_reading)
        db.commit()
        db.refresh(new_reading)

        logger.info(f"Received traffic data: {payload.node_id}: {payload.vehicle_count} vehicles, {payload.speed} km/h")

        return {
            "status": "success",
            "message": "Traffic data saved to database",
            "data_received": payload.model_dump()
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"System failure during ingestion: {str(e)} [cite: 10]")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
    
@app.get("/traffic-data", response_model=List[TrafficResponse])
async def get_traffic_data(
    skip: int = 0,
    limit: int = 100,
    node_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.TrafficReading)

    if node_id:
        query = query.filter(models.TrafficReading.node_id == node_id)

    records = query.order_by(models.TrafficReading.timestamp.desc()).offset(skip).limit(limit).all()

    return records

@app.post("/predict/{node_id}", response_model=PredictionResponse)
async def create_prection(node_id: str, db: Session = Depends(get_db)):
    try:
        prediction = prediction_logic.generate_prediction(node_id, db)

        if not prediction:
            raise HTTPException(status_code=404, detail="Not enough data to generate prediction")
        
        logger.info(f"Generated {prediction.predicted_level} congestion prediction for {node_id}")
        return prediction
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error during prediction")