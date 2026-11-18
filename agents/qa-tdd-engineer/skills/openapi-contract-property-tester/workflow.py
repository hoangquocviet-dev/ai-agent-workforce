import json
import re
import ast
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

@dataclass
class PropertyBoundaryResult:
    property_name: str
    test_type: str
    generated_value: Any
    expected_valid: bool

class OpenAPIContractAnalyzer:
    def __init__(self, schema_json: str):
        self.schema = json.loads(schema_json)

    def generate_boundaries(self, prop_name: str, prop_schema: Dict[str, Any]) -> List[PropertyBoundaryResult]:
        results = []
        ptype = prop_schema.get("type", "string")
        
        if ptype == "integer" or ptype == "number":
            minimum = prop_schema.get("minimum", 0)
            maximum = prop_schema.get("maximum", 100)
            results.extend([
                PropertyBoundaryResult(prop_name, "min_boundary", minimum, True),
                PropertyBoundaryResult(prop_name, "below_min", minimum - 1, False),
                PropertyBoundaryResult(prop_name, "max_boundary", maximum, True),
                PropertyBoundaryResult(prop_name, "above_max", maximum + 1, False)
            ])
        elif ptype == "string":
            max_len = prop_schema.get("maxLength", 50)
            results.extend([
                PropertyBoundaryResult(prop_name, "normal_string", "test_val", True),
                PropertyBoundaryResult(prop_name, "empty_string", "", prop_schema.get("minLength", 0) == 0),
                PropertyBoundaryResult(prop_name, "overflow_string", "A" * (max_len + 1), False)
            ])
        elif ptype == "array":
            min_items = prop_schema.get("minItems", 0)
            results.extend([
                PropertyBoundaryResult(prop_name, "empty_array", [], min_items == 0),
                PropertyBoundaryResult(prop_name, "valid_array", [1, 2], True)
            ])
        return results

    def analyze_contract(self) -> Dict[str, Any]:
        all_tests = []
        paths = self.schema.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                responses = details.get("responses", {})
                for status, resp in responses.items():
                    content = resp.get("content", {})
                    for media_type, media_obj in content.items():
                        schema = media_obj.get("schema", {})
                        props = schema.get("properties", {})
                        for p_name, p_schema in props.items():
                            boundaries = self.generate_boundaries(p_name, p_schema)
                            all_tests.extend([asdict(b) for b in boundaries])
        return {
            "path_count": len(paths),
            "generated_test_count": len(all_tests),
            "tests": all_tests
        }

if __name__ == "__main__":
    sample_spec = '''
    {
      "paths": {
        "/users": {
          "post": {
            "responses": {
              "201": {
                "content": {
                  "application/json": {
                    "schema": {
                      "type": "object",
                      "properties": {
                        "age": { "type": "integer", "minimum": 18, "maximum": 120 },
                        "username": { "type": "string", "maxLength": 10 }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    '''
    analyzer = OpenAPIContractAnalyzer(sample_spec)
    report = analyzer.analyze_contract()
    assert report["path_count"] == 1
    assert report["generated_test_count"] == 7
    assert any(t["test_type"] == "below_min" and not t["expected_valid"] for t in report["tests"])
    print(json.dumps(report, indent=2))
