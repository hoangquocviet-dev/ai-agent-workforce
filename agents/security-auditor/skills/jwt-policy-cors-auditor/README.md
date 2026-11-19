# JWT & CORS Security Auditor

An automated analyzer designed for the `security-auditor` agent to inspect Python source code for insecure JWT token decoding practices and overly permissive CORS configurations.

## Quick Start
Execute the validator script:
```bash
python3 workflow.py
```

## Rules Enforced
- **JWT-001**: Missing explicit `algorithms` parameter during decoding.
- **JWT-002**: Use of the insecure `none` algorithm in `jwt.decode`.
- **CORS-001**: Wildcard origin (`*`) detected in CORS middleware configuration.
