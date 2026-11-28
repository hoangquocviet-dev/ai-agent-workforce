"""
Tail Latency Hotspot Correlator Workflow
Isolates production tail latency (p99/p99.9) spikes by correlating resource metrics.
"""

import json
import statistics
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class TelemetrySample:
    timestamp: int
    p50_latency_ms: float
    p99_latency_ms: float
    thread_pool_utilization_pct: float
    gc_pause_ms: float
    downstream_timeout_count: int


class LatencyCorrelatorAnalyzer:
    def __init__(self, samples: List[Dict[str, Any]]):
        self.samples = [
            TelemetrySample(
                timestamp=s["timestamp"],
                p50_latency_ms=s["p50_latency_ms"],
                p99_latency_ms=s["p99_latency_ms"],
                thread_pool_utilization_pct=s["thread_pool_utilization_pct"],
                gc_pause_ms=s["gc_pause_ms"],
                downstream_timeout_count=s["downstream_timeout_count"]
            )
            for s in samples
        ]

    def analyze(self) -> Dict[str, Any]:
        if not self.samples:
            return {"status": "insufficient_data", "hotspot": None}

        p99_vals = [s.p99_latency_ms for s in self.samples]
        p50_vals = [s.p50_latency_ms for s in self.samples]
        tp_vals = [s.thread_pool_utilization_pct for s in self.samples]
        gc_vals = [s.gc_pause_ms for s in self.samples]
        timeout_vals = [s.downstream_timeout_count for s in self.samples]

        max_p99 = max(p99_vals)
        mean_p50 = statistics.mean(p50_vals)
        p99_to_p50_ratio = max_p99 / mean_p50 if mean_p50 > 0 else 0.0

        avg_tp = statistics.mean(tp_vals)
        max_gc = max(gc_vals)
        total_timeouts = sum(timeout_vals)

        hotspot = "none"
        confidence = "low"

        if max_gc > 100.0:
            hotspot = "garbage_collection_pause"
            confidence = "high"
        elif avg_tp > 50.0:
            hotspot = "thread_pool_exhaustion"
            confidence = "high"
        elif total_timeouts > 5:
            hotspot = "downstream_io_timeout"
            confidence = "medium"
        elif p99_to_p50_ratio > 4.0:
            hotspot = "unidentified_contention"
            confidence = "moderate"

        return {
            "status": "success",
            "max_p99_ms": max_p99,
            "p99_to_p50_ratio": round(p99_to_p50_ratio, 2),
            "isolated_hotspot": hotspot,
            "confidence": confidence,
            "metrics_summary": {
                "avg_thread_pool_pct": round(avg_tp, 1),
                "max_gc_pause_ms": max_gc,
                "total_downstream_timeouts": total_timeouts
            }
        }


if __name__ == "__main__":
    test_payload_thread_exhaustion = [
        {"timestamp": 1000, "p50_latency_ms": 12.0, "p99_latency_ms": 45.0, "thread_pool_utilization_pct": 60.0, "gc_pause_ms": 5.0, "downstream_timeout_count": 0},
        {"timestamp": 2000, "p50_latency_ms": 15.0, "p99_latency_ms": 350.0, "thread_pool_utilization_pct": 98.5, "gc_pause_ms": 8.0, "downstream_timeout_count": 1}
    ]

    test_payload_gc_spike = [
        {"timestamp": 1000, "p50_latency_ms": 10.0, "p99_latency_ms": 30.0, "thread_pool_utilization_pct": 40.0, "gc_pause_ms": 2.0, "downstream_timeout_count": 0},
        {"timestamp": 2000, "p50_latency_ms": 11.0, "p99_latency_ms": 620.0, "thread_pool_utilization_pct": 45.0, "gc_pause_ms": 250.0, "downstream_timeout_count": 0}
    ]

    analyzer1 = LatencyCorrelatorAnalyzer(test_payload_thread_exhaustion)
    res1 = analyzer1.analyze()
    assert res1["isolated_hotspot"] == "thread_pool_exhaustion"
    assert res1["confidence"] == "high"

    analyzer2 = LatencyCorrelatorAnalyzer(test_payload_gc_spike)
    res2 = analyzer2.analyze()
    assert res2["isolated_hotspot"] == "garbage_collection_pause"
    assert res2["confidence"] == "high"

    print(json.dumps({
        "test_suite": "passed",
        "results": [res1, res2]
    }, indent=2))
