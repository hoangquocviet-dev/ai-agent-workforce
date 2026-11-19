---
name: jwt-policy-cors-auditor
description: Audits Python backend codebases for insecure JWT configurations (e.g., algorithm confusion, disabled verification) and overly permissive CORS wildcard policies.
agent: security-auditor
version: 1.0.0
---

# JWT Algorithm & CORS Policy Hardening Auditor

## Overview
This skill provides automated static analysis for web applications to detect critical security misconfigurations in JWT validation and CORS middleware definitions.

## Capabilities
- Detects hardcoded or disabled JWT algorithm verification (e.g., `algorithms=['none']`, missing `algorithms` parameter).
- Identifies overly permissive CORS policies such as `Access-Control-Allow-Origin: *` combined with credential allowance.
- Generates structured remediation advice and compliance checklists.

## Usage
Run the workflow script against your codebase directory:
```bash
python3 workflow.py
```
