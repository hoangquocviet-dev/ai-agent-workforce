---
name: Tail Latency Hotspot Correlator
description: Isolate production tail latency (p99/p99.9) spikes by correlating thread pool exhaustion, garbage collection pause patterns, and downstream I/O timeout anomalies from telemetry logs.
agent: root-cause-debugger
version: 1.0.0
---

# Tail Latency Hotspot Correlator

## Overview
The `tail-latency-hotspot-correlator` skill analyzes structured application performance logs and metrics telemetry to isolate root causes of p99/p99.9 latency spikes in distributed microservices. It cross-correlates thread pool saturation metrics, GC pause durations, and downstream service call durations.

## Capabilities
- **Metric Anomaly Detection**: Parses time-series samples to identify sudden divergence between median (p50) and tail (p99) latency.
- **Resource Bottleneck Triangulation**: Determines whether latency is bound by CPU throttling, event-loop starvation, thread pool exhaustion, or external network latency.
- **Actionable Remediation**: Generates precise tuning recommendations for thread pool capacities, connection timeouts, and garbage collection ergonomics.

## Usage
Execute the workflow analyzer with a JSON payload containing time-series telemetry logs:
```bash
python3 workflow.py
```
