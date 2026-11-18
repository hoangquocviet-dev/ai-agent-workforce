---
name: openapi-contract-property-tester
description: Generates property-based boundary tests and validates request-response schemas directly from OpenAPI definitions.
agent: qa-tdd-engineer
version: 1.0.0
---

# OpenAPI Contract Property Tester

## Overview
The `openapi-contract-property-tester` skill analyzes OpenAPI specifications and automatically synthesizes boundary-value test cases and property validation asserts. It detects missing response fields, boundary violations, type mismatches, and contract regressions.

## Capabilities
- Parses OpenAPI JSON/YAML specs (structural subset via Python stdlib).
- Generates edge-case boundary values for numeric, string, and array properties (min/max, empty collections, nulls).
- Validates target payload JSON against schema expectations.
- Produces a comprehensive deterministic test report.

## Usage
Execute the workflow script directly to validate contracts and generate test suites:
```bash
python3 workflow.py
```
