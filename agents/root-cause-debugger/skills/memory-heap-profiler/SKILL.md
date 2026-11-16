---
name: memory-heap-profiler
description: Autonomous memory profiling and heap leak diagnosis workflow for production Python services.
agent: root-cause-debugger
version: 1.0.0
tags:
  - performance
  - memory-leak
  - root-cause-analysis
  - debugging
---

# 🧠 Memory Heap Profiler

## Overview
The `memory-heap-profiler` skill empowers AI agents to autonomously identify, track, and diagnose memory leaks and abnormal heap growth in long-running Python services and batch workloads.

## When to Use
- A process or worker experiences unbounded memory consumption over time.
- Diagnosing potential memory leaks before and after executing test workloads.
- Identifying specific lines of code responsible for the highest allocations.
- Verifying whether a bug fix successfully eliminates an allocation leak.

## Workflow Execution Steps
1. **Initialize Profiler:** Start `tracemalloc` with designated frame depth (default: 10 frames).
2. **Capture Baseline:** Record initial heap snapshot prior to running target workloads.
3. **Execute & Checkpoint:** Run operations while capturing intermediate memory checkpoints.
4. **Differential Analysis:** Compare current snapshot against baseline, sorting by `size_diff` and `count_diff`.
5. **Report & Isolate:** Export structured JSON diagnostics highlighting top offending files, line numbers, and leak confidence scores.
