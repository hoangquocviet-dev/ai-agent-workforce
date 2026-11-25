---
name: ssrf-path-traversal-sanitizer
description: Detects Server-Side Request Forgery (SSRF) and path traversal vulnerabilities in Python source code by analyzing AST nodes for unsafe file access and outbound HTTP requests.
agent: security-auditor
version: 1.0.0
---

# SSRF & Path Traversal Sanitizer

## Overview
The `ssrf-path-traversal-sanitizer` skill inspects Python AST representations to locate potentially vulnerable patterns involving file path construction (`open`, `os.path`) and network requests (`requests`, `urllib`). It flags usage lacking proper path normalization or domain allowlist validation.

## Capabilities
- **Path Traversal Detection**: Flags variable-based file reads without safe base directory confinement.
- **SSRF Detection**: Identifies dynamic URL fetching using user-supplied parameters without scheme/host validation.
- **Zero-Dependency AST Scanning**: Operates purely within Python Standard Library capabilities.

## Usage
Run the workflow script to analyze code snippets or files for vulnerabilities:
```bash
python3 workflow.py
```
