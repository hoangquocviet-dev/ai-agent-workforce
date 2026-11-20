import os
import re
import ast
import json
import sys
import argparse
from dataclasses import dataclass, asdict
from typing import List, Dict, Any

@dataclass
class Violation:
    rule_id: str
    severity: str
    message: str
    line_number: int
    file_path: str

class OutboxSagaValidator(ast.NodeVisitor):
    def __init__(self, file_path: str, source_code: str):
        self.file_path = file_path
        self.source_code = source_code
        self.violations: List[Violation] = []
        self.tree = ast.parse(source_code)
        self.lines = source_code.splitlines()

    def run(self) -> List[Violation]:
        self.visit(self.tree)
        self._check_raw_kafka_publish()
        return self.violations

    def visit_FunctionDef(self, node: ast.FunctionDef):
        func_name = node.name.lower()
        if 'saga' in func_name or 'workflow' in func_name:
            self._check_saga_compensation(node)
        if 'consume' in func_name or 'handler' in func_name:
            self._check_idempotency(node)
        self.generic_visit(node)

    def _check_saga_compensation(self, node: ast.FunctionDef):
        has_try = False
        has_compensate = False
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                has_try = True
                for handler in child.handlers:
                    for sub in ast.walk(handler):
                        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name):
                            if 'compensate' in sub.func.id.lower() or 'rollback' in sub.func.id.lower():
                                has_compensate = True
        if has_try and not has_compensate:
            self.violations.append(Violation(
                rule_id="SAGA_MISSING_COMPENSATION",
                severity="HIGH",
                message=f"Saga function '{node.name}' catches exceptions but invokes no compensating rollback action.",
                line_number=node.lineno,
                file_path=self.file_path
            ))

    def _check_idempotency(self, node: ast.FunctionDef):
        body_text = "\n".join(self.lines[node.lineno-1:node.end_lineno or node.lineno])
        if 'idempot' not in body_text.lower() and 'dedup' not in body_text.lower():
            self.violations.append(Violation(
                rule_id="IDEMPOTENCY_KEY_MISSING",
                severity="MEDIUM",
                message=f"Consumer/Handler '{node.name}' lacks explicit idempotency or deduplication check.",
                line_number=node.lineno,
                file_path=self.file_path
            ))

    def _check_raw_kafka_publish(self):
        for idx, line in enumerate(self.lines):
            if re.search(r'\b(producer\.send|kafka_client\.publish)\b', line):
                if not any(outbox in line.lower() for outbox in ['outbox', 'transactional']):
                    self.violations.append(Violation(
                rule_id="DUAL_WRITE_RISK",
                severity="CRITICAL",
                message="Direct message broker publish detected outside transactional outbox pattern.",
                line_number=idx + 1,
                file_path=self.file_path
            ))

def analyze_code(file_path: str, source: str) -> List[Dict[str, Any]]:
    validator = OutboxSagaValidator(file_path, source)
    return [asdict(v) for v in validator.run()]

if __name__ == '__main__':
    sample_bad_saga = '''
def execute_order_saga(order_id):
    try:
        db.execute("UPDATE orders SET status='PROCESSING'")
        payment_client.charge(order_id)
    except Exception as e:
        logging.error(f"Failed: {e}")

def consume_payment_event(event):
    db.execute("INSERT INTO ledger VALUES (:id)", event)

producer.send("orders", b"payload")
'''
    violations = analyze_code("services/order_service.py", sample_bad_saga)
    assert len(violations) >= 3, f"Expected at least 3 violations, got {len(violations)}"
    
    summary = {
        "status": "SUCCESS",
        "total_violations": len(violations),
        "violations": violations
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0)
