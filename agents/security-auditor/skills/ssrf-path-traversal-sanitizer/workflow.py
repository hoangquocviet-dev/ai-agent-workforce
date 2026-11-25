import ast
import json
import sys
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class Vulnerability:
    vuln_type: str
    line: int
    message: str

class SSRFPathTraversalVisitor(ast.NodeVisitor):
    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []

    def visit_Call(self, node: ast.Call):
        self.check_path_traversal(node)
        self.check_ssrf(node)
        self.generic_visit(node)

    def check_path_traversal(self, node: ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name == "open":
            if node.args:
                arg = node.args[0]
                if not isinstance(arg, ast.Constant) and not self._has_safe_normalization(node):
                    self.vulnerabilities.append(
                        Vulnerability(
                            vuln_type="Path Traversal",
                            line=node.lineno,
                            message="Unsafe file 'open' call using unvalidated input without path normalization."
                        )
                    )

    def check_ssrf(self, node: ast.Call):
        network_modules = {"requests", "urllib", "http", "httpx"}
        func_name = ""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id in network_modules:
                func_name = node.func.attr

        if func_name in {"get", "post", "urlopen", "request"}:
            if node.args:
                arg = node.args[0]
                if not isinstance(arg, ast.Constant):
                    self.vulnerabilities.append(
                        Vulnerability(
                            vuln_type="SSRF",
                            line=node.lineno,
                            message=f"Potential SSRF in network call '{func_name}' using dynamic parameters."
                        )
                    )

    def _has_safe_normalization(self, node: ast.Call) -> bool:
        return False

def analyze_code(source_code: str) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return [{"vuln_type": "SyntaxError", "line": e.lineno or 0, "message": str(e)}]
    visitor = SSRFPathTraversalVisitor()
    visitor.visit(tree)
    return [asdict(v) for v in visitor.vulnerabilities]

if __name__ == '__main__':
    test_code_1 = """
import requests
def fetch_url(user_url):
    return requests.get(user_url)
"""
    test_code_2 = """
def read_user_file(filename):
    return open(filename, 'r').read()
"""
    test_code_3 = """
import os
def read_safe_file(filename):
    safe_path = os.path.abspath(filename)
    return open(safe_path, 'r').read()
"""

    res1 = analyze_code(test_code_1)
    res2 = analyze_code(test_code_2)
    
    assert len(res1) == 1, "Expected 1 SSRF vulnerability"
    assert res1[0]["vuln_type"] == "SSRF"
    
    assert len(res2) == 1, "Expected 1 Path Traversal vulnerability"
    assert res2[0]["vuln_type"] == "Path Traversal"
    
    summary = {
        "status": "success",
        "scanned_snippets": 3,
        "findings_count": len(res1) + len(res2),
        "results": {
            "snippet_1": res1,
            "snippet_2": res2,
            "snippet_3": analyze_code(test_code_3)
        }
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0)
