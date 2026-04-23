from __future__ import annotations

from dataclasses import dataclass
import time

import requests

from simulator.config import SimulatorConfig
from simulator.logger import get_logger
from simulator.models import TrafficReading


@dataclass(slots=True)
class SendResult:
    success: bool
    status_code: int | None
    response_text: str | None
    error: str | None = None


class TrafficSender:
    def __init__(self, config: SimulatorConfig):
        self.config = config
        self.logger = get_logger()
        self.session = requests.Session()

    def _serialize(self, payload: TrafficReading | dict) -> dict:
        if isinstance(payload, TrafficReading):
            return payload.as_payload()
        if isinstance(payload, dict):
            return payload
        raise TypeError("Unsupported payload type")

    def send(self, payload: TrafficReading | dict) -> SendResult:
        body = self._serialize(payload)
        last_error: str | None = None

        for attempt in range(self.config.retries + 1):
            try:
                response = self.session.post(
                    self.config.backend_url,
                    json=body,
                    timeout=self.config.timeout_seconds,
                )
                response.raise_for_status()
                self.logger.info("Sent payload %s with status %s", body, response.status_code)
                return SendResult(True, response.status_code, response.text)
            except (requests.ConnectionError, requests.Timeout, requests.HTTPError, requests.RequestException) as exc:
                last_error = str(exc)
                self.logger.warning("Send attempt %s failed: %s", attempt + 1, last_error)
                if attempt < self.config.retries:
                    time.sleep(min(1.0, 0.25 * (attempt + 1)))

        return SendResult(False, None, None, last_error)
