# Prototype Pollution Shield

This skill belongs to the **`security-auditor`** agent. It provides automated detection of prototype poisoning patterns in untrusted input streams.

## Quick Start

Run the validator script:

```bash
python workflow.py
```

## Integration with Agents

When an AI agent processes incoming untrusted JSON structures, invoke `audit_payload()` before merging dictionaries or passing raw parsed objects into sensitive application contexts.
