from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace

import requests

from simulator.config import SimulatorConfig
from simulator.generator import TrafficGenerator
from simulator.models import TrafficReading
from simulator.sender import TrafficSender


def test_normal_generation_ranges():
    generator = TrafficGenerator(SimulatorConfig(seed=7, scenario="normal"))
    reading = generator.next_validated()

    assert 0 <= reading.vehicle_count <= 200
    assert 0 <= reading.speed <= 120
    assert 0 <= reading.density <= 1
    assert reading.node_id == "simulator"
    assert reading.timestamp.tzinfo is not None


def test_peak_hour_is_more_congested_than_low_traffic():
    peak_generator = TrafficGenerator(SimulatorConfig(seed=11, scenario="peak_hour"))
    low_generator = TrafficGenerator(SimulatorConfig(seed=11, scenario="low_traffic"))

    peak_samples = [peak_generator.next_validated() for _ in range(8)]
    low_samples = [low_generator.next_validated() for _ in range(8)]

    peak_avg_speed = sum(sample.speed for sample in peak_samples) / len(peak_samples)
    low_avg_speed = sum(sample.speed for sample in low_samples) / len(low_samples)
    peak_avg_density = sum(sample.density for sample in peak_samples) / len(peak_samples)
    low_avg_density = sum(sample.density for sample in low_samples) / len(low_samples)

    assert peak_avg_speed < low_avg_speed
    assert peak_avg_density > low_avg_density


def test_faulty_payload_can_be_invalid():
    generator = TrafficGenerator(SimulatorConfig(seed=3, scenario="faulty_data", fault_injection=True))
    payload = generator.next_raw_payload()

    assert set(payload).issubset({"vehicle_count", "speed", "density", "timestamp", "node_id"})
    assert any(key not in payload for key in ["vehicle_count", "speed", "density", "timestamp"]) or any(
        isinstance(payload.get(key), str) for key in ["vehicle_count", "speed", "density", "timestamp"]
    )


def test_sender_retries_until_success(monkeypatch):
    config = SimulatorConfig(retries=2)
    sender = TrafficSender(config)
    payload = TrafficReading(vehicle_count=10, speed=45.0, density=0.2, timestamp=datetime.now()).as_payload()

    calls = {"count": 0}

    def fake_post(url, json, timeout):
        calls["count"] += 1
        if calls["count"] < 3:
            raise requests.ConnectionError("temporary connection issue")
        response = SimpleNamespace(status_code=201, text="ok")
        response.raise_for_status = lambda: None
        return response

    monkeypatch.setattr(sender.session, "post", fake_post)

    result = sender.send(payload)

    assert result.success is True
    assert calls["count"] == 3


def test_timestamp_is_serialized_as_iso_string():
    reading = TrafficReading(vehicle_count=10, speed=50.0, density=0.3, timestamp=datetime.now())
    payload = reading.as_payload()

    assert isinstance(payload["timestamp"], str)
    normalized = payload["timestamp"].replace("Z", "+00:00")
    assert datetime.fromisoformat(normalized)
