---
name: async-deadlock-detector
description: Detects async coroutine starvation, task inter-lock cycles, and await-chain deadlocks in concurrent event loop traces.
agent: root-cause-debugger
version: 1.0.0
---

# Async Deadlock and Coroutine Starvation Detector

## Overview
The `async-deadlock-detector` skill analyzes concurrency dumps, event loop execution logs, and coroutine state traces to isolate circular await dependencies, abandoned futures, and thread-pool starvation leading to application hangs.

## Capabilities
- **Cycle Detection**: Builds directed graphs of active coroutines and resolves circular await dependencies.
- **Future Abandonment Analysis**: Flags Futures and Tasks created without active consumers or awaiting targets.
- **Event Loop Latency Correlation**: Correlates long-running synchronous callbacks with delayed async dispatch queues.

## Usage
Execute the workflow validator with a target trace log to verify concurrency integrity.
