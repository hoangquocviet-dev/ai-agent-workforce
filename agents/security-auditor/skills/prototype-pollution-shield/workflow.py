"""
Prototype Pollution Vulnerability Scanner & Validator
=====================================================
Tool for scanning untrusted JSON structures to identify dangerous prototype pollution vectors.
"""

import json
import sys

def audit_payload(data: str) -> dict:
    """Audits raw JSON string for prototype pollution indicators."""
    issues = []
    
    # Check for direct __proto__
    if '"__proto__"' in data:
        issues.append({
            "severity": "CRITICAL",
            "pattern": "__proto__",
            "message": "Direct __proto__ property found in payload."
        })

    # Check for nested constructor.prototype
    if '"constructor"' in data and '"prototype"' in data:
        try:
            parsed = json.loads(data)
            def check_dict(d):
                if isinstance(d, dict):
                    if "constructor" in d and isinstance(d["constructor"], dict) and "prototype" in d["constructor"]:
                        issues.append({
                            "severity": "HIGH",
                            "pattern": "constructor.prototype",
                            "message": "Malicious constructor.prototype nesting detected."
                        })
                    for v in d.values():
                        check_dict(v)
            check_dict(parsed)
        except Exception:
            pass

    return {
        "safe": len(issues) == 0,
        "issues_count": len(issues),
        "issues": issues
    }

if __name__ == "__main__":
    test_vector = '{"user": "alice", "constructor": {"prototype": {"admin": true}}}'
    res = audit_payload(test_vector)
    print("Audit Result:", json.dumps(res, indent=2))
