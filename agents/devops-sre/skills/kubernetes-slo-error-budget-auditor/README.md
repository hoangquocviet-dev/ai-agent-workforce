# Kubernetes SLO Error Budget Auditor Skill

## Overview
Autonomous engineering skill for the `devops-sre` agent that inspects Kubernetes workloads and evaluates them against established Service Level Objectives (SLOs) and error budget policies.

## Features
- **Automated Budget Calculation**: Determines exact error budget minutes over sliding 30-day windows.
- **Reliability Validation**: Flags single-replica setups and missing liveness/readiness probes that risk SLO breaches.
- **Standardized Burn-Rate Alerting**: Outputs multi-window burn rate recommendations.

## Quick Start
Run tests and validate functionality:
```bash
python3 workflow.py
```
