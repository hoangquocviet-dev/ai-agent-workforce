# SSRF & Path Traversal Sanitizer Skill

This skill is an automated security analyzer designed for the `security-auditor` agent. It statically analyzes Python code to identify high-risk Server-Side Request Forgery (SSRF) and Path Traversal vulnerabilities.

## Features
- AST-based code parsing.
- Zero external dependencies (Python standard library only).
- Automated self-test execution on invocation.

## Quick Start
Execute the workflow to run tests and analyze sample inputs:
```bash
python3 workflow.py
```
