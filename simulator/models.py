from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TrafficReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    vehicle_count: int = Field(ge=0, le=200)
    speed: float = Field(ge=0, le=120)
    density: float = Field(ge=0, le=1)
    timestamp: datetime
    node_id: str = Field(default="simulator")

    @field_validator("timestamp")
    @classmethod
    def normalize_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def as_payload(self) -> dict:
        return self.model_dump(mode="json", exclude={"node_id"})
