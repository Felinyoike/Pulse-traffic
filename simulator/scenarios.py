from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import random


SCENARIOS = {"normal", "peak_hour", "low_traffic", "sudden_spike", "faulty_data"}


@dataclass(slots=True)
class ScenarioSample:
    vehicle_count: int
    speed: float
    density: float
    timestamp: str
    node_id: str

    def as_dict(self) -> dict:
        return {
            "vehicle_count": self.vehicle_count,
            "speed": self.speed,
            "density": self.density,
            "timestamp": self.timestamp,
            "node_id": self.node_id,
        }


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _base_sample(
    rng: random.Random,
    node_id: str,
    vehicle_count: tuple[int, int],
    speed: tuple[float, float],
    density: tuple[float, float],
) -> ScenarioSample:
    vehicles = rng.randint(*vehicle_count)
    congestion = round(rng.uniform(*density), 3)
    lower_speed, upper_speed = speed
    speed_floor = max(lower_speed, upper_speed - (congestion * (upper_speed - lower_speed) * 0.8))
    speed_value = round(rng.uniform(lower_speed, speed_floor), 1) if speed_floor > lower_speed else round(lower_speed, 1)
    return ScenarioSample(
        vehicle_count=vehicles,
        speed=speed_value,
        density=congestion,
        timestamp=_utc_now(),
        node_id=node_id,
    )


def build_sample(scenario: str, rng: random.Random, node_id: str, step: int) -> ScenarioSample:
    if scenario == "normal":
        return _base_sample(rng, node_id, (20, 80), (35.0, 75.0), (0.18, 0.55))
    if scenario == "peak_hour":
        return _base_sample(rng, node_id, (90, 180), (10.0, 45.0), (0.6, 0.95))
    if scenario == "low_traffic":
        return _base_sample(rng, node_id, (0, 30), (60.0, 110.0), (0.02, 0.2))
    if scenario == "sudden_spike":
        if step % 4 == 3:
            return _base_sample(rng, node_id, (140, 200), (5.0, 30.0), (0.75, 1.0))
        return _base_sample(rng, node_id, (15, 60), (40.0, 85.0), (0.15, 0.45))
    if scenario == "faulty_data":
        return _base_sample(rng, node_id, (20, 80), (35.0, 75.0), (0.18, 0.55))
    raise ValueError(f"Unknown scenario: {scenario}")


def inject_fault(sample: ScenarioSample, rng: random.Random, node_id: str) -> dict:
    payload = sample.as_dict()
    fault_type = rng.choice(["missing_field", "invalid_type", "out_of_range", "corrupted_timestamp"])

    if fault_type == "missing_field":
        payload.pop(rng.choice(["vehicle_count", "speed", "density", "timestamp"]), None)
    elif fault_type == "invalid_type":
        payload[rng.choice(["vehicle_count", "speed", "density"])] = "invalid"
    elif fault_type == "out_of_range":
        payload[rng.choice(["vehicle_count", "speed", "density"])] = 9999
    else:
        payload["timestamp"] = "not-a-timestamp"

    payload["node_id"] = node_id
    return payload
