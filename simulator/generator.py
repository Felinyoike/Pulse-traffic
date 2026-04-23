from __future__ import annotations

from dataclasses import dataclass
import random

from simulator.config import SimulatorConfig
from simulator.models import TrafficReading
from simulator.scenarios import SCENARIOS, build_sample, inject_fault


@dataclass(slots=True)
class GeneratedTraffic:
    validated: TrafficReading | None
    raw_payload: dict


class TrafficGenerator:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self._rng = random.Random(config.seed)
        self._step = 0

    def next_raw_payload(self) -> dict:
        if self.config.scenario not in SCENARIOS:
            raise ValueError(f"Unsupported scenario: {self.config.scenario}")

        sample = build_sample(self.config.scenario, self._rng, self.config.node_id, self._step)
        self._step += 1

        if self.config.scenario == "faulty_data" and self.config.fault_injection:
            return inject_fault(sample, self._rng, self.config.node_id)

        return sample.as_dict()

    def next_validated(self) -> TrafficReading:
        payload = self.next_raw_payload()
        return TrafficReading.model_validate(payload)

    def next(self) -> GeneratedTraffic:
        payload = self.next_raw_payload()
        validated = None
        if not (self.config.scenario == "faulty_data" and self.config.fault_injection):
            validated = TrafficReading.model_validate(payload)
        return GeneratedTraffic(validated=validated, raw_payload=payload)
