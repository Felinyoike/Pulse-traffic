from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class TrafficReading(Base):
    __tablename__ = "traffic_readings"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    timestamp = Column(DateTime)
    vehicle_count = Column(Integer)
    speed = Column(Float)
    density = Column(Float)

class CongestionPrediction(Base):
    __tablename__ = "congestion_predictions"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, index=True)
    target_time = Column(DateTime)
    predicted_level = Column(String)
    confidence_score = Column(Float)