import ast
import json
import sys
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class CouplingViolation:
    lineno: int
    class_instantiated: str
    message: str

class DIPVisitor(ast.NodeVisitor):
    def __init__(self, allowed_suffixes: List[str] = None):
        self.violations: List[CouplingViolation] = []
        self.allowed_suffixes = allowed_suffixes or ['Exception', 'Error', 'Config', 'Context', 'Builder']

    def visit_Call(self, node: ast.Call):
        self.generic_visit(node)
        target_name = ""
        if isinstance(node.func, ast.Name):
            target_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            target_name = node.func.attr

        if target_name and target_name[0].isupper():
            if not any(target_name.endswith(suf) for suf in self.allowed_suffixes):
                self.violations.append(CouplingViolation(
                    lineno=node.lineno,
                    class_instantiated=target_name,
                    message=f"Direct instantiation of concrete class '{target_name}' violates Dependency Inversion Principle."
                ))

def audit_code(source_code: str) -> str:
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return json.dumps({"error": str(e)})
    
    visitor = DIPVisitor()
    visitor.visit(tree)
    result = {
        "violation_count": len(visitor.violations),
        "violations": [asdict(v) for v in visitor.violations]
    }
    return json.dumps(result, indent=2)

if __name__ == '__main__':
    test_code_clean = """
class OrderService:
    def __init__(self, payment_gateway: PaymentGateway):
        self.gateway = payment_gateway

    def checkout(self, amount):
        return self.gateway.charge(amount)
    """

    test_code_violation = """
class OrderService:
    def __init__(self):
        self.gateway = StripePaymentGateway()

    def checkout(self, amount):
        logger = FileLogger()
        logger.log("checkout started")
        return self.gateway.charge(amount)
    """

    res_clean = json.loads(audit_code(test_code_clean))
    assert res_clean["violation_count"] == 0, f"Expected 0 violations, got {res_clean['violation_count']}"

    res_viol = json.loads(audit_code(test_code_violation))
    assert res_viol["violation_count"] == 2, f"Expected 2 violations, got {res_viol['violation_count']}"
    assert res_viol["violations"][0]["class_instantiated"] == "StripePaymentGateway"

    summary = {
        "status": "SUCCESS",
        "skill": "solid-dependency-inversion-auditor",
        "tests_passed": 2,
        "sample_violation_caught": res_viol["violations"][0]["class_instantiated"]
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0)
