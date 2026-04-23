# Pulse Traffic Integration Guide

## Overview

This project implements a complete traffic simulation pipeline: **Simulator → Backend → Prediction Module**.

The simulator generates realistic traffic data conforming to a strict schema, sends it to a FastAPI backend, which stores it and generates congestion predictions.

---

## Backend API Contract

### Payload Schema

```json
{
  "vehicle_count": 25,
  "speed": 45.5,
  "density": 0.62,
  "timestamp": "2026-04-22T10:30:00Z"
}
```

### Constraints

- `vehicle_count`: 0–200 (integer)
- `speed`: 0–120 km/h (float)
- `density`: 0–1 ratio (float)
- `timestamp`: ISO 8601 UTC format (required timezone)
- `node_id`: optional, defaults to `"simulator"`

### Endpoint

```
POST /traffic-data
```

---

## Quick Start

### Start the Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000/docs`

### Run the Simulator

In a separate terminal, from the project root:

```bash
python -m simulator.main --scenario normal
```

The simulator will send one data point every 2 seconds. By default, it connects to `http://127.0.0.1:8000/traffic-data`.

---

## Simulator Modes

### 1. Normal Traffic

```bash
python -m simulator.main --scenario normal
```

Generates realistic mixed-flow conditions: 20–80 vehicles, 35–75 km/h, density 0.18–0.55.

### 2. Peak Hour

```bash
python -m simulator.main --scenario peak_hour
```

Heavy congestion: 90–180 vehicles, 10–45 km/h, density 0.6–0.95.

### 3. Low Traffic

```bash
python -m simulator.main --scenario low_traffic
```

Free flow: 0–30 vehicles, 60–110 km/h, density 0.02–0.2.

### 4. Sudden Spike

```bash
python -m simulator.main --scenario sudden_spike
```

Alternates normal conditions with sudden congestion spikes.

### 5. Faulty Data (for backend validation testing)

```bash
python -m simulator.main --scenario faulty_data --fault-injection --allow-invalid-payloads
```

Injects faults (missing fields, type errors, out-of-range values, corrupted timestamps) to test backend robustness.

---

## Configuration Options

All options can be passed via command-line arguments:

```bash
python -m simulator.main \
  --backend-url http://custom-backend:8000/traffic-data \
  --scenario peak_hour \
  --interval 1.5 \
  --node-id sensor-1 \
  --retries 3 \
  --timeout 10 \
  --seed 42
```

| Option | Default | Description |
|--------|---------|-------------|
| `--backend-url` | `http://127.0.0.1:8000/traffic-data` | Backend API endpoint |
| `--interval` | `2.0` | Seconds between data points |
| `--scenario` | `normal` | Traffic scenario to simulate |
| `--node-id` | `simulator` | Node identifier for the payload |
| `--retries` | `2` | Number of API retry attempts |
| `--timeout` | `5.0` | API request timeout in seconds |
| `--fault-injection` | False | Enable malformed payload generation (requires `--scenario faulty_data`) |
| `--allow-invalid-payloads` | False | Send payloads that fail local validation (for testing backend rejection) |
| `--seed` | None | Random seed for reproducible scenarios |

---

## Example: Load Testing

Simulate 3 minutes of peak-hour traffic with faster intervals:

```bash
python -m simulator.main --scenario peak_hour --interval 0.5 --timeout 10
```

You can query the backend after:

```bash
curl "http://127.0.0.1:8000/traffic-data?limit=50"
```

---

## Integration Testing

### Run Simulator Tests

```bash
python -m pytest simulator/tests/test_simulator.py -v
```

All tests verify:
- ✓ Generated data stays in valid ranges
- ✓ Scenario behavior (peak > low traffic)
- ✓ Timestamp serialization (UTC ISO 8601)
- ✓ Retry logic under connection failures
- ✓ Faults are correctly injected

### Backend Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## Payload Examples

### Normal Traffic

```json
{
  "vehicle_count": 54,
  "speed": 62.3,
  "density": 0.38,
  "timestamp": "2026-04-23T14:22:45Z"
}
```

### Peak Hour

```json
{
  "vehicle_count": 156,
  "speed": 18.5,
  "density": 0.82,
  "timestamp": "2026-04-23T14:22:47Z"
}
```

### Faulty Payload (if `--allow-invalid-payloads` is set)

```json
{
  "vehicle_count": "not_a_number",
  "speed": 45.0,
  "density": 0.5,
  "timestamp": "2026-04-23T14:22:49Z"
}
```

Backend will reject with a validation error.

---

## Logging

The simulator logs all operations:

```
2026-04-23 14:22:45 - INFO - Sent payload {'vehicle_count': 54, 'speed': 62.3, 'density': 0.38, 'timestamp': '2026-04-23T14:22:45Z'} with status 201
2026-04-23 14:22:47 - INFO - Sent payload {'vehicle_count': 156, 'speed': 18.5, 'density': 0.82, 'timestamp': '2026-04-23T14:22:47Z'} with status 201
```

Connection errors and retries:

```
2026-04-23 14:22:49 - WARNING - Send attempt 1 failed: Connection refused
2026-04-23 14:22:49 - WARNING - Send attempt 2 failed: Connection refused
2026-04-23 14:22:50 - WARNING - Send attempt 3 failed: Connection refused
2026-04-23 14:22:50 - ERROR - Delivery failed after retries: Connection refused
```

---

## Architecture

```
Simulator (Python)
  ├── Config: database, interval, scenario
  ├── Generator: realistic traffic data by scenario
  ├── Models: Pydantic schema validation
  ├── Sender: HTTP + retry logic
  └── Logger: all API interactions

Backend (FastAPI)
  ├── Schemas: strict input validation
  ├── Models: database tables (SQLAlchemy)
  ├── Routes: /traffic-data (POST, GET)
  ├── Prediction: congestion prediction (1h forecast)
  └── Database: SQLite (traffic_data.db)
```

---

## Troubleshooting

### Backend not responding

If you get `Connection refused`, ensure the backend is running:

```bash
cd backend && uvicorn main:app --reload
```

### Timeout errors

Increase the timeout:

```bash
python -m simulator.main --timeout 15
```

### Module not found errors

Ensure dependencies are installed:

```bash
pip install -r simulator/requirements.txt
pip install -r backend/requirements.txt
```

### Validation errors in logs

If the backend rejects data, check the endpoint URL:

```bash
python -m simulator.main --backend-url http://127.0.0.1:8000/traffic-data
```

Or enable fault testing to confirm backend validation works:

```bash
python -m simulator.main --scenario faulty_data --fault-injection --allow-invalid-payloads
```
