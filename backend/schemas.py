from pydantic import BaseModel, Field, field_validator
from datetime import datetime

class TrafficPayload(BaseModel):
    node_id: str = Field(..., description="Unique identifier for the simulated sensor node")
    timestamp: datetime = Field(..., description="Time the reading was taken (ISO 8601 format)")
    vehicle_count: int = Field(..., description="Number of vehicles detected")
    speed: float = Field(..., description="Average speed in km/h")
    density: float = Field(..., description="Traffic density percentage")

    # QA Validation: Ensure no negative values are ingested from the simulator
    @field_validator('vehicle_count', 'speed', 'density')
    @classmethod
    def check_non_negative(cls, val, infor):
        if val < 0:
            raise ValueError(f"{infor.field_name} cannot be negative")
        return val
    
    @field_validator('density')
    @classmethod
    def check_density_range(cls, val):
        if val < 0 or val > 100:
            raise ValueError("Density cannot exceed 100%")
        return val
    
class TrafficResponse(TrafficPayload):
    id: int

    class Config:
        from_attributes = True

class PredictionResponse(BaseModel):
    id: int
    node_id: str
    target_time: datetime
    predicted_level: str
    confidence_score: float

    class Config:
        from_attributes = True