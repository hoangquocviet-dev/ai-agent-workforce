# Memory Heap Profiler

Autonomous memory profiling and heap leak diagnosis tool maintained by the **Root-Cause Debugger** agent.

## Quick Start

```python
from workflow import MemoryHeapProfiler

profiler = MemoryHeapProfiler()
profiler.start()

# Execute target logic
run_my_service()

# Capture and compare
report = profiler.compare("baseline")
print("Memory Diagnostic Report:", report)
```

## Running the Self-Test

```bash
python workflow.py
```
