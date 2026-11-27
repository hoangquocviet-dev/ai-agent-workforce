import sys
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Set, Optional

@dataclass
class IndexAuditFinding:
    table_name: str
    index_name: str
    severity: str
    message: str
    recommendation: str

class BTreeIndexAuditor:
    def __init__(self, ddl_content: str):
        self.ddl_content = ddl_content

    def audit(self) -> List[IndexAuditFinding]:
        findings = []
        table_indexes = self._parse_indexes()
        
        for table, indexes in table_indexes.items():
            if len(indexes) > 5:
                findings.append(IndexAuditFinding(
                    table_name=table,
                    index_name="MULTIPLE",
                    severity="WARNING",
                    message=f"Table '{table}' has {len(indexes)} indexes, increasing write amplification.",
                    recommendation="Consolidate redundant single-column indexes into composite indexes."
                ))
            
            for idx in indexes:
                # Check for low-cardinality flags or status/boolean prefix flags
                cols = [c.strip().lower() for c in idx['columns']]
                if len(cols) == 1 and any(term in cols[0] for term in ['status', 'is_', 'active', 'type']):
                    findings.append(IndexAuditFinding(
                        table_name=table,
                        index_name=idx['name'],
                        severity="INFO",
                        message=f"Index '{idx['name']}' on low-cardinality column '{cols[0]}' may result in poor B-Tree selectivity.",
                        recommendation="Consider partial indexes (WHERE status = 'ACTIVE') or composite indexing with high-cardinality keys first."
                    ))
                
                # Check for prefix redundancy
                for other in indexes:
                    if idx['name'] != other['name']:
                        other_cols = [c.strip().lower() for c in other['columns']]
                        if len(other_cols) > len(cols) and other_cols[:len(cols)] == cols:
                            findings.append(IndexAuditFinding(
                                table_name=table,
                                index_name=idx['name'],
                                severity="CRITICAL",
                                message=f"Index '{idx['name']}' is a strict left prefix of '{other['name']}'.",
                                recommendation=f"Drop redundant index '{idx['name']}' as '{other['name']}' covers its access path."
                            ))
        return findings

    def _parse_indexes(self) -> Dict[str, List[Dict]]:
        table_indexes: Dict[str, List[Dict]] = {}
        create_index_pattern = re.compile(r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(\w+)\s+ON\s+(\w+)\s*\(([^)]+)\)', re.IGNORECASE)
        for match in create_index_pattern.finditer(self.ddl_content):
            idx_name, table_name, cols_raw = match.groups()
            table_name = table_name.lower()
            cols = [c.split()[0] for c in cols_raw.split(',')]
            if table_name not in table_indexes:
                table_indexes[table_name] = []
            table_indexes[table_name].append({'name': idx_name, 'columns': cols})
        return table_indexes

if __name__ == '__main__':
    sample_ddl = '''
        CREATE TABLE users (
            id INT PRIMARY KEY,
            email VARCHAR(255),
            status VARCHAR(50),
            is_active BOOLEAN
        );
        CREATE INDEX idx_users_status ON users(status);
        CREATE INDEX idx_users_status_email ON users(status, email);
        CREATE INDEX idx_users_email ON users(email);
    '''
    auditor = BTreeIndexAuditor(sample_ddl)
    results = auditor.audit()
    assert len(results) > 0, "Expected audit findings"
    output = {
        "status": "success",
        "findings_count": len(results),
        "findings": [asdict(f) for f in results]
    }
    print(json.dumps(output, indent=2))
    sys.exit(0)
