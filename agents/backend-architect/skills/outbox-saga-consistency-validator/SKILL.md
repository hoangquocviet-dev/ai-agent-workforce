---
name: outbox-saga-consistency-validator
description: Validates transactional outbox implementations and saga orchestrators for idempotency leaks, missing compensating transactions, and dual-write anomalies.
agent: backend-architect
version: 1.0.0
---

# Outbox and Saga Consistency Validator

## Overview
This skill analyzes backend codebase repositories for distributed transaction anti-patterns, specifically focusing on:
- **Dual-Write Vulnerabilities**: Operations updating local databases and publishing events without transactional outbox protection.
- **Saga Compensating Actions**: State machines or workflow orchestrators lacking defined rollback handlers for step failures.
- **Idempotency Key Propagation**: Event consumers or outbox pollers lacking unique idempotency key validation.

## Execution
Run the workflow script to analyze service code files:
```bash
python3 workflow.py --path ./src
```
