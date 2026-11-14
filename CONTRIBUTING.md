# Contributing to AI Agent Workforce

Thank you for your interest in expanding our specialized AI workforce! Community contributions help keep skills robust, modern, and production-tested.

---

## 📌 Ways to Contribute

1. **Propose a New Skill:** Open an issue using the [Skill Proposal template](.github/ISSUE_TEMPLATE/new-skill-proposal.md) to discuss ideas.
2. **Submit a Skill via Pull Request:** Create a skill directory under the appropriate agent's `skills/` folder.
3. **Report Bugs or Edge Cases:** Found a workflow that fails under certain runtime conditions? Open a [Bug Report](.github/ISSUE_TEMPLATE/bug-report.md).

---

## 🛠️ Skill Specification Standard

Each skill must follow this minimal folder layout:

```text
agents/<agent-name>/skills/<skill-name>/
├── SKILL.md       # Metadata, instructions, constraints, and execution workflow
├── workflow.py    # Executable implementation or automation script (Python or TS)
└── README.md      # Usage instructions and example scenarios
```

### Requirements:
- **Executable Code:** Any script included must be runnable without undeclared dependencies.
- **Clear Constraints:** Document failure modes, rate limits, and prerequisite environment variables.
- **Original Content:** Please do not copy copyrighted text or proprietary prompts.
