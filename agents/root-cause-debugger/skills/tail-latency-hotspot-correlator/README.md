# Tail Latency Hotspot Correlator

An autonomous engineering skill for the **Root-Cause Debugger** agent designed to isolate production tail latency anomalies.

## Quick Start
Run the built-in test suite and workflow validation:
```bash
python3 workflow.py
```

## Architecture
- **Input**: Array of telemetry sample dictionaries.
- **Analysis Engine**: Computes variance ratios between p50 and p99, aggregates thread saturation, and isolates bottlenecks.
- **Output**: Structured JSON report with root-cause identification and confidence scoring.
