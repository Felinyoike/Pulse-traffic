from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
import json


@dataclass(slots=True)
class SimulatorConfig:
    backend_url: str = "http://127.0.0.1:8000/traffic-data"
    interval_seconds: float = 2.0
    scenario: str = "normal"
    fault_injection: bool = False
    allow_invalid_payloads: bool = False
    timeout_seconds: float = 5.0
    retries: int = 2
    node_id: str = "simulator"
    seed: int | None = None

    @classmethod
    def load(cls, path: str | Path) -> "SimulatorConfig":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
