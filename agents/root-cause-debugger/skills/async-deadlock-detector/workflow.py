import json
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

@dataclass
class CoroutineNode:
    task_id: str
    state: str
    awaits_id: str

class AsyncDeadlockAnalyzer:
    def __init__(self, trace_data: str):
        self.trace_data = trace_data

    def parse_traces(self) -> List[CoroutineNode]:
        nodes = []
        # Fix: Make 'AWAITS' case-insensitive to handle 'AWAits' typo
        pattern = re.compile(r'TASK_ID=(\w+)\s+STATE=(\w+)\s+AWAITS=(\w+)?', re.IGNORECASE)
        for line in self.trace_data.splitlines():
            match = pattern.search(line)
            if match:
                task_id, state, awaits = match.groups()
                nodes.append(CoroutineNode(task_id=task_id, state=state, awaits_id=awaits or ""))
        return nodes

    def detect_deadlock_cycles(self) -> List[List[str]]:
        nodes = self.parse_traces()
        adj: Dict[str, str] = {n.task_id: n.awaits_id for n in nodes if n.awaits_id}
        
        cycles = []
        visited: Set[str] = set()
        
        for start_node in adj:
            if start_node in visited:
                continue
            path = []
            curr = start_node
            local_visited = set()
            
            while curr in adj:
                if curr in local_visited:
                    # Cycle detected
                    cycle_start_idx = path.index(curr)
                    cycle = path[cycle_start_idx:]
                    cycles.append(cycle)
                    break
                if curr in visited:
                    break
                local_visited.add(curr)
                path.append(curr)
                curr = adj[curr]
            
            visited.update(local_visited)
            
        return cycles

    def analyze(self) -> dict:
        cycles = self.detect_deadlock_cycles()
        return {
            "status": "DEADLOCK_DETECTED" if cycles else "HEALTHY",
            "cycles_found": len(cycles),
            "deadlock_chains": cycles
        }

if __name__ == '__main__':
    sample_trace_1 = """
    TASK_ID=t1 STATE=SUSPENDED AWAITS=t2
    TASK_ID=t2 STATE=SUSPENDED AWAits=t3
    TASK_ID=t3 STATE=SUSPENDED AWAITS=t1
    """
    
    sample_trace_2 = """
    TASK_ID=t1 STATE=RUNNING AWAITS=
    TASK_ID=t2 STATE=SUSPENDED AWAITS=t1
    """
    
    analyzer_1 = AsyncDeadlockAnalyzer(sample_trace_1)
    res_1 = analyzer_1.analyze()
    assert res_1["status"] == "DEADLOCK_DETECTED"
    assert len(res_1["deadlock_chains"]) == 1
    
    analyzer_2 = AsyncDeadlockAnalyzer(sample_trace_2)
    res_2 = analyzer_2.analyze()
    assert res_2["status"] == "HEALTHY"
    
    summary = {
        "skill": "async-deadlock-detector",
        "test_cases_run": 2,
        "assertions_passed": True,
        "result_sample": res_1
    }
    print(json.dumps(summary, indent=2))
    sys.exit(0)
