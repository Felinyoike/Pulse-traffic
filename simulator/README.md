# Pulse Traffic Simulator

Run the simulator from the repository root:

```bash
python -m simulator.main --scenario normal
```

To test backend validation with malformed payloads:

```bash
python -m simulator.main --scenario faulty_data --fault-injection --allow-invalid-payloads
```
