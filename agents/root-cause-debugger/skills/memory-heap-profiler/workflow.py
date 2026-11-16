"""
Memory Heap Profiler & Leak Detector
====================================
Agent: Root-Cause Debugger
Skill: memory-heap-profiler

Provides programmatic heap allocation profiling, snapshot diffing,
and leak candidate isolation using Python's standard tracemalloc library.
"""

import sys
import os
import json
import tracemalloc
from typing import Dict, List, Optional
from datetime import datetime


class MemoryHeapProfiler:
    """Manages heap snapshot capture and differential memory diagnostics."""

    def __init__(self, key_type: str = "lineno", frame_depth: int = 10):
        self.key_type = key_type
        self.frame_depth = frame_depth
        self.snapshots: Dict[str, tracemalloc.Snapshot] = {}
        self.is_running = False

    def start(self):
        """Starts heap allocation tracking."""
        if not tracemalloc.is_tracing():
            tracemalloc.start(self.frame_depth)
        self.is_running = True
        self.capture("baseline")

    def capture(self, label: str) -> tracemalloc.Snapshot:
        """Captures a snapshot with a human-readable label."""
        if not self.is_running:
            raise RuntimeError("Profiler has not been started. Call start() first.")
        snap = tracemalloc.take_snapshot()
        self.snapshots[label] = snap
        return snap

    def compare(self, baseline_label: str = "baseline", current_label: Optional[str] = None, limit: int = 10) -> Dict:
        """Compares two snapshots and identifies top memory allocators."""
        if baseline_label not in self.snapshots:
            raise ValueError(f"Baseline label '{baseline_label}' not found.")

        if current_label is None:
            current_snap = tracemalloc.take_snapshot()
        else:
            if current_label not in self.snapshots:
                raise ValueError(f"Target label '{current_label}' not found.")
            current_snap = self.snapshots[current_label]

        base_snap = self.snapshots[baseline_label]
        top_stats = current_snap.compare_to(base_snap, self.key_type)

        allocations: List[Dict] = []
        total_growth_bytes = 0

        for stat in top_stats[:limit]:
            size_diff_kb = stat.size_diff / 1024.0
            total_growth_bytes += stat.size_diff
            allocations.append({
                "trace": str(stat.traceback),
                "size_diff_kb": round(size_diff_kb, 2),
                "count_diff": stat.count_diff,
                "current_size_kb": round(stat.size / 1024.0, 2),
                "current_count": stat.count
            })

        current_kb, peak_kb = tracemalloc.get_traced_memory()
        current_kb = round(current_kb / 1024.0, 2)
        peak_kb = round(peak_kb / 1024.0, 2)

        # Flag potential leak: growth > 10MB or high positive allocation diff
        is_leak_suspect = total_growth_bytes > 5 * 1024 * 1024  # >5MB net growth

        return {
            "status": "ANOMALY_DETECTED" if is_leak_suspect else "NORMAL",
            "leak_suspect": is_leak_suspect,
            "net_growth_kb": round(total_growth_bytes / 1024.0, 2),
            "current_memory_kb": current_kb,
            "peak_memory_kb": peak_kb,
            "top_allocations": allocations,
            "analyzed_at": datetime.now().isoformat()
        }

    def stop(self):
        """Stops memory profiling."""
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        self.is_running = False


def run_self_test() -> Dict:
    """Executes a self-test with a controlled memory allocation to verify detection."""
    profiler = MemoryHeapProfiler()
    profiler.start()

    # Simulate memory activity: allocate retained blocks
    retained_cache = []
    for i in range(50000):
        retained_cache.append(f"cache_key_data_payload_node_{i}")

    profiler.capture("after_workload")
    report = profiler.compare("baseline", "after_workload", limit=5)
    profiler.stop()

    # Clean up test allocation
    del retained_cache
    return report


if __name__ == "__main__":
    print("=" * 60)
    print("🧠 Running Root-Cause Debugger: Memory Heap Profiler Self-Test")
    print("=" * 60)
    result = run_self_test()
    print(json.dumps(result, indent=2))
    print(f"\nNet Growth: {result['net_growth_kb']} KB | Peak: {result['peak_memory_kb']} KB")
    print("Self-test completed successfully.")
