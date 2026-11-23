---
name: Kubernetes SLO Error Budget Auditor
description: Evaluates Kubernetes deployment specifications and Prometheus alerting rules against reliability targets to calculate burn rates and error budgets.
agent: devops-sre
version: 1.0.0
---

# Kubernetes SLO Error Budget Auditor

## Overview
The **Kubernetes SLO Error Budget Auditor** is an autonomous engineering skill designed to analyze Kubernetes deployment manifests alongside Service Level Objective (SLO) definitions and Prometheus alert rules. It validates whether pod resource configurations, replica counts, and alert burn-rate thresholds align with error budget consumption policies.

## Capabilities
- **Replica & Availability Check**: Validates minimum replica constraints for high availability (HA) targets.
- **Burn Rate Calculator**: Computes multi-window multi-burn-rate alerting thresholds based on defined availability objectives (e.g., 99.9%).
- **Proactive Remediation Suggestions**: Generates actionable configuration recommendations for missing probes, insufficient replicas, or overly aggressive alerting rules.

## Usage
Execute the workflow script directly via Python 3 to audit deployment specifications and SLO configurations.
```bash
python3 workflow.py
```
