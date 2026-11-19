import ast
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class SecurityFinding:
    rule_id: str
    severity: str
    message: str
    line_number: int

class SecurityAuditorVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings: List[SecurityFinding] = []

    def visit_Call(self, node: ast.Call):
        self._check_jwt_decode(node)
        self._check_cors_policy(node)
        self.generic_visit(node)

    def _check_jwt_decode(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        elif isinstance(node.func, ast.Name):
            func_name = node.func.id

        if "decode" in func_name.lower():
            has_algorithms = False
            allow_none = False
            for keyword in node.keywords:
                if keyword.arg == "algorithms":
                    has_algorithms = True
                    if isinstance(keyword.value, ast.List):
                        for elt in keyword.value.elts:
                            if isinstance(elt, ast.Constant) and str(elt.value).lower() in ["none", "hs256"]: # simplistic check for weak/none
                                if str(elt.value).lower() == "none":
                                    allow_none = True
            if not has_algorithms:
                self.findings.append(SecurityFinding(
                    rule_id="JWT-001",
                    severity="HIGH",
                    message="JWT decode called without explicit 'algorithms' parameter restriction.",
                    line_number=node.lineno
                ))
            elif allow_none:
                self.findings.append(SecurityFinding(
                    rule_id="JWT-002",
                    severity="CRITICAL",
                    message="JWT decode allows 'none' algorithm which bypasses signature verification.",
                    line_number=node.lineno
                ))

    def _check_cors_policy(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if "cors" in func_name.lower() or any(kw.arg == "allow_origins" for kw in node.keywords):
            for kw in node.keywords:
                if kw.arg == "allow_origins" and isinstance(kw.value, ast.List):
                    for elt in kw.value.elts:
                        if isinstance(elt, ast.Constant) and elt.value == "*":
                            self.findings.append(SecurityFinding(
                                rule_id="CORS-001",
                                severity="MEDIUM",
                                message="CORS policy allows wildcard origin ('*'). Ensure credentials are not allowed simultaneously.",
                                line_number=node.lineno
                            ))

def audit_source_code(source_code: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(source_code)
        visitor = SecurityAuditorVisitor()
        visitor.visit(tree)
        return [asdict(f) for f in visitor.findings]
    except SyntaxError as e:
        return [{"rule_id": "SYNTAX-ERR", "severity": "ERROR", "message": str(e), "line_number": e.lineno or 0}]

if __name__ == '__main__':
    test_code_secure = """
jwt.decode(token, secret, algorithms=["RS256"])
app.add_middleware(CORSMiddleware, allow_origins=["https://example.com"])
"""

    test_code_insecure = """
jwt.decode(token, secret)
jwt.decode(token, secret, algorithms=["none"])
app.add_middleware(CORSMiddleware, allow_origins=["*"])
"""

    findings_secure = audit_source_code(test_code_secure)
    findings_insecure = audit_source_code(test_code_insecure)

    assert len(findings_secure) == 0, f"Expected 0 findings, got {findings_secure}"
    assert len(findings_insecure) == 3, f"Expected 3 findings, got {len(findings_insecure)}"

    summary = {
        "status": "SUCCESS",
        "audited_cases": 2,
        "total_findings_detected": len(findings_insecure),
        "findings": findings_insecure
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0)
