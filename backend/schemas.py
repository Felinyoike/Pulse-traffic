from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator

class TrafficPayload(BaseModel):
    node_id: str = Field(
        default="simulator",
        description="Unique identifier for the simulated sensor node",
    )
    timestamp: datetime = Field(..., description="Time the reading was taken (ISO 8601 format)")
    vehicle_count: int = Field(..., ge=0, le=200, description="Number of vehicles detected")
    speed: float = Field(..., ge=0, le=120, description="Average speed in km/h")
    density: float = Field(..., ge=0, le=1, description="Traffic density ratio")

    @field_validator('timestamp')
    @classmethod
    def ensure_timestamp_is_timezone_aware(cls, value):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value

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
        if val < 0 or val > 1:
            raise ValueError("Density must be between 0 and 1")
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