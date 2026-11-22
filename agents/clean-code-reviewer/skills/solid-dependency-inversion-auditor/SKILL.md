---
name: solid-dependency-inversion-auditor
description: Scans Python AST to detect direct instantiation of concrete classes inside service boundaries, validating the Dependency Inversion Principle (DIP) and identifying tight coupling.
agent: clean-code-reviewer
version: 1.0.0
---

# SOLID Dependency Inversion and Coupling Auditor

## Overview
This skill audits Python source files via AST analysis to identify violations of the Dependency Inversion Principle (DIP). It flags direct instantiation of concrete implementation classes inside high-level service modules, ensuring components depend on abstractions rather than low-level details.

## Capabilities
- AST-based traversal of class definitions and function bodies.
- Detection of `Call` nodes instantiating concrete classes inside business logic.
- Generation of structural coupling metrics and actionable refactoring suggestions.

## Usage
Execute the workflow script directly with a target path or run unit tests:
```bash
python workflow.py
```
