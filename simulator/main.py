from __future__ import annotations

import argparse
import signal
import time

from simulator.config import SimulatorConfig
from simulator.generator import TrafficGenerator
from simulator.logger import get_logger
from simulator.sender import TrafficSender


def run_simulation(config: SimulatorConfig) -> None:
    logger = get_logger()
    generator = TrafficGenerator(config)
    sender = TrafficSender(config)
    running = True

    def stop_handler(signum, frame):
        nonlocal running
        running = False
        logger.info("Stopping simulator after signal %s", signum)

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    while running:
        generated = generator.next()
        if generated.validated is not None:
            result = sender.send(generated.validated)
        elif config.allow_invalid_payloads:
            result = sender.send(generated.raw_payload)
        else:
            logger.error("Rejected invalid payload locally: %s", generated.raw_payload)
            result = None

        if result is not None and not result.success:
            logger.error("Delivery failed after retries: %s", result.error)

        time.sleep(max(0.0, config.interval_seconds))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pulse Traffic simulator")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000/traffic-data")
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--scenario", default="normal", choices=["normal", "peak_hour", "low_traffic", "sudden_spike", "faulty_data"])
    parser.add_argument("--fault-injection", action="store_true")
    parser.add_argument("--allow-invalid-payloads", action="store_true")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--retries", type=int, default=2)
    parser.add_argument("--node-id", default="simulator")
    parser.add_argument("--seed", type=int, default=None)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = SimulatorConfig(
        backend_url=args.backend_url,
        interval_seconds=args.interval,
        scenario=args.scenario,
        fault_injection=args.fault_injection,
        allow_invalid_payloads=args.allow_invalid_payloads,
        timeout_seconds=args.timeout,
        retries=args.retries,
        node_id=args.node_id,
        seed=args.seed,
    )
    run_simulation(config)


if __name__ == "__main__":
    main()
