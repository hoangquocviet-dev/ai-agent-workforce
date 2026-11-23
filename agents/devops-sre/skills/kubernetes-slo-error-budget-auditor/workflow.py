"""
Kubernetes SLO Error Budget Auditor
Evaluates Kubernetes deployment specifications and SLO targets to compute error budgets and burn rates.
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class SLOSpec:
    target_availability: float  # e.g., 99.9
    window_days: int            # e.g., 30
    current_error_budget_pct: float

@dataclass
class AuditResult:
    compliant: bool
    service_name: str
    error_budget_minutes: float
    burn_rate_alerts: List[Dict[str, Any]]
    recommendations: List[str]

class SLOBudgetAuditor:
    def __init__(self, slo: SLOSpec):
        self.slo = slo

    def calculate_error_budget(self) -> float:
        total_minutes = self.slo.window_days * 24 * 60
        allowed_downtime_pct = 100.0 - self.slo.target_availability
        return total_minutes * (allowed_downtime_pct / 100.0)

    def audit_deployment(self, deployment_manifest: str, service_name: str) -> AuditResult:
        budget_mins = self.calculate_error_budget()
        recommendations = []
        compliant = True

        # Check replicas
        replica_match = re.search(r'replicas:\s*(\d+)', deployment_manifest)
        replicas = int(replica_match.group(1)) if replica_match else 1
        if replicas < 3 and self.slo.target_availability >= 99.9:
            compliant = False
            recommendations.append(f"Increase replicas from {replicas} to at least 3 for high availability (target {self.slo.target_availability}%).")

        # Check probes
        if 'livenessProbe' not in deployment_manifest:
            compliant = False
            recommendations.append("Missing livenessProbe in container specification.")
        if 'readinessProbe' not in deployment_manifest:
            compliant = False
            recommendations.append("Missing readinessProbe in container specification.")

        # Generate standard burn rate alert configurations (Google SRE workbook multi-window)
        burn_rate_alerts = [
            {"window": "1h", "burn_rate": 14.4, "budget_consumed_pct": 2.0},
            {"window": "6h", "burn_rate": 6.0, "budget_consumed_pct": 5.0}
        ]

        return AuditResult(
            compliant=compliant,
            service_name=service_name,
            error_budget_minutes=round(budget_mins, 2),
            burn_rate_alerts=burn_rate_alerts,
            recommendations=recommendations
        )

if __name__ == '__main__':
    # Unit Test 1: Compliant Deployment
    slo_spec = SLOSpec(target_availability=99.9, window_days=30, current_error_budget_pct=100.0)
    auditor = SLOBudgetAuditor(slo_spec)
    
    manifest_good = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: payment-service
    spec:
      replicas: 3
      template:
        spec:
          containers:
          - name: app
            livenessProbe:
              httpGet:
                path: /healthz
                port: 8080
            readinessProbe:
              httpGet:
                path: /ready
                port: 8080
    """
    result_good = auditor.audit_deployment(manifest_good, "payment-service")
    assert result_good.compliant is True
    assert result_good.error_budget_minutes == 43.2

    # Unit Test 2: Non-Compliant Deployment (Missing Probes & Low Replicas)
    manifest_bad = """
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: legacy-service
    spec:
      replicas: 1
      template:
        spec:
          containers:
          - name: app
    """
    result_bad = auditor.audit_deployment(manifest_bad, "legacy-service")
    assert result_bad.compliant is False
    assert len(result_bad.recommendations) >= 3

    summary = {
        "status": "SUCCESS",
        "tests_passed": 2,
        "sample_audit": asdict(result_bad)
    }
    print(json.dumps(summary, indent=2))
