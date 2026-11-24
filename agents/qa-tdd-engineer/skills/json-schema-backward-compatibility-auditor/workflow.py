import json
import collections

def _get_property_details(schema_obj, path="#"):
    properties = {}
    # Only process if it's an object schema
    if isinstance(schema_obj, dict) and schema_obj.get("type") == "object" and "properties" in schema_obj:
        for prop_name, prop_schema in schema_obj["properties"].items():
            current_path = f"{path}/properties/{prop_name}"
            is_required = prop_name in schema_obj.get("required", [])
            prop_type = prop_schema.get("type", "any")
            
            properties[prop_name] = {
                "type": prop_type,
                "required": is_required,
                "path": current_path,
                "nested_properties": {}
            }
            
            if prop_type == "object":
                properties[prop_name]["nested_properties"] = _get_property_details(prop_schema, current_path)
                
    return properties

def analyze_schema_compatibility(old_schema_str: str, new_schema_str: str) -> dict:
    report = {
        "status": "compatible",
        "breaking_changes": []
    }

    try:
        old_schema = json.loads(old_schema_str)
        new_schema = json.loads(new_schema_str)
    except json.JSONDecodeError as e:
        report["status"] = "error"
        report["breaking_changes"].append({"type": "INVALID_JSON", "message": f"Invalid JSON schema input: {e}"})
        return report

    # Check if root schemas are valid object schemas for comparison
    if not (isinstance(old_schema, dict) and old_schema.get("type") == "object"):
        report["status"] = "error"
        report["breaking_changes"].append({"type": "INVALID_SCHEMA_STRUCTURE", "message": "Old schema is not a valid object schema."})
        return report

    if not (isinstance(new_schema, dict) and new_schema.get("type") == "object"):
        report["status"] = "error"
        report["breaking_changes"].append({"type": "INVALID_SCHEMA_STRUCTURE", "message": "New schema is not a valid object schema."})
        return report

    old_props = _get_property_details(old_schema)
    new_props = _get_property_details(new_schema)

    queue = collections.deque([ (old_props, new_props, "#") ])

    while queue:
        current_old_props, current_new_props, current_path = queue.popleft()

        for prop_name, old_prop_details in current_old_props.items():
            full_path = old_prop_details["path"]
            
            if prop_name not in current_new_props:
                report["breaking_changes"].append({
                    "type": "PROPERTY_REMOVED",
                    "message": f"Property '{prop_name}' removed.",
                    "path": full_path
                })
                report["status"] = "incompatible"
                continue

            new_prop_details = current_new_props[prop_name]

            if old_prop_details["type"] != new_prop_details["type"]:
                report["breaking_changes"].append({
                    "type": "TYPE_CHANGED",
                    "message": f"Type of property '{prop_name}' changed from '{old_prop_details['type']}' to '{new_prop_details['type']}'.",
                    "path": full_path
                })
                report["status"] = "incompatible"

            if not old_prop_details["required"] and new_prop_details["required"]:
                report["breaking_changes"].append({
                    "type": "REQUIRED_STATUS_CHANGED",
                    "message": f"Property '{prop_name}' changed from optional to required.",
                    "path": full_path
                })
                report["status"] = "incompatible"
            
            if old_prop_details["type"] == "object" and new_prop_details["type"] == "object":
                queue.append((old_prop_details["nested_properties"], new_prop_details["nested_properties"], full_path))

        # Check for newly added required properties in the new schema (breaking change if added to existing object)
        # This part was missing and is crucial for comprehensive compatibility checks
        for prop_name, new_prop_details in current_new_props.items():
            if prop_name not in current_old_props and new_prop_details["required"]:
                report["breaking_changes"].append({
                    "type": "REQUIRED_PROPERTY_ADDED",
                    "message": f"New required property '{prop_name}' added.",
                    "path": new_prop_details["path"]
                })
                report["status"] = "incompatible"

    return report

if __name__ == '__main__':
    old_schema_1 = json.dumps({
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string", "minLength": 1}
        },
        "required": ["id", "name"]
    })
    new_schema_1 = json.dumps({
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string", "minLength": 1},
            "email": {"type": "string", "format": "email"}
        },
        "required": ["id", "name"]
    })
    result_1 = analyze_schema_compatibility(old_schema_1, new_schema_1)
    assert result_1["status"] == "compatible", f"Test 1 Failed: {result_1}"
    assert len(result_1["breaking_changes"]) == 0, f"Test 1 Failed: {result_1}"

    old_schema_2 = json.dumps({
        "type": "object",
        "properties": {
            "userId": {"type": "string"},
            "age": {"type": "number"},
            "isActive": {"type": "boolean"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "city": {"type": "string"}
                },
                "required": ["street"]
            }
        },
        "required": ["userId", "age"]
    })
    new_schema_2 = json.dumps({
        "type": "object",
        "properties": {
            "userId": {"type": "number"},
            "isActive": {"type": "boolean"},
            "address": {
                "type": "object",
                "properties": {
                    "street": {"type": "string"},
                    "zipCode": {"type": "string"}
                },
                "required": ["street", "zipCode"]
            }
        },
        "required": ["userId", "isActive"]
    })
    result_2 = analyze_schema_compatibility(old_schema_2, new_schema_2)
    assert result_2["status"] == "incompatible", f"Test 2 Failed: {result_2}"
    assert len(result_2["breaking_changes"]) == 5, f"Test 2 Failed: {result_2}" # Changed from 4 to 5 due to new check
    assert any(c["type"] == "PROPERTY_REMOVED" and c["path"] == "#/properties/age" for c in result_2["breaking_changes"])
    assert any(c["type"] == "TYPE_CHANGED" and c["path"] == "#/properties/userId" for c in result_2["breaking_changes"])
    assert any(c["type"] == "REQUIRED_STATUS_CHANGED" and c["path"] == "#/properties/isActive" for c in result_2["breaking_changes"])
    assert any(c["type"] == "PROPERTY_REMOVED" and c["path"] == "#/properties/address/properties/city" for c in result_2["breaking_changes"])
    assert any(c["type"] == "REQUIRED_PROPERTY_ADDED" and c["path"] == "#/properties/address/properties/zipCode" for c in result_2["breaking_changes"])

    invalid_schema = '{"key": "value"}' # This is valid JSON, but not a valid object schema for comparison
    result_3 = analyze_schema_compatibility(old_schema_1, invalid_schema)
    assert result_3["status"] == "error", f"Test 3 Failed: {result_3}"
    assert len(result_3["breaking_changes"]) == 1, f"Test 3 Failed: {result_3}"
    assert result_3["breaking_changes"][0]["type"] == "INVALID_SCHEMA_STRUCTURE"

    print(json.dumps({
        "test_results": [
            {"name": "Test Case 1: Compatible change", "result": result_1},
            {"name": "Test Case 2: Incompatible changes", "result": result_2},
            {"name": "Test Case 3: Invalid JSON input", "result": result_3}
        ]
    }, indent=2))
