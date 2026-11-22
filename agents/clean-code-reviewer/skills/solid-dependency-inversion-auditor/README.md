# SOLID Dependency Inversion and Coupling Auditor

An autonomous engineering skill for the `clean-code-reviewer` agent that parses Python AST to identify tight coupling and violations of the Dependency Inversion Principle (DIP).

## Quick Start
Run the built-in test suite and verify workflow execution:
```bash
python workflow.py
```

## Architecture
- **`workflow.py`**: Standard library AST parser enforcing clean code rules without external dependencies.
- **`SKILL.md`**: Metadata and functional documentation.
