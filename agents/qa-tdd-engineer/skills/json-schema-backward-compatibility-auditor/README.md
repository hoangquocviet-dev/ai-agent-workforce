# JSON Schema Backward Compatibility Auditor

This repository contains the `json-schema-backward-compatibility-auditor` skill designed for the `qa-tdd-engineer` agent. Its primary purpose is to help maintain the stability and reliability of APIs and data contracts by automatically detecting changes in JSON schemas that could break existing consumers.

## Overview

In a rapidly evolving software ecosystem, APIs and data structures frequently undergo changes. While adding new features or optimizing existing ones, it's crucial to ensure that these modifications do not inadvertently introduce breaking changes for clients that rely on older versions of the contract. This auditor automates the process of comparing two versions of a JSON schema and reporting any backward-incompatible alterations.

## Features

*   **Property Removal Detection**: Identifies properties that were present in the old schema but are missing in the new one.
*   **Property Type Change Detection**: Flags instances where the data type of an existing property has been altered (e.g., `string` to `number`).
*   **Required Status Change Detection**: Reports when an optional property in the old schema becomes a required property in the new schema, forcing clients to provide a value they previously weren't obligated to.
*   **Nested Schema Traversal**: Recursively analyzes properties within nested objects to ensure deep compatibility.
*   **Clear Reporting**: Provides a structured JSON report detailing all detected breaking changes, including their type and exact path within the schema.

## How It Works

The `workflow.py` script takes two JSON schema strings as input: an `old_schema_str` and a `new_schema_str`. It parses these strings into Python dictionaries and then performs a systematic comparison:

1.  **Schema Parsing**: Converts the input JSON strings into traversable Python objects.
2.  **Property Extraction**: Recursively extracts property definitions, including their types and `required` status, for both schemas.
3.  **Compatibility Check**: Iterates through the properties of the old schema and checks their corresponding presence and attributes in the new schema.
    *   If an old property is missing in the new schema, it's a `PROPERTY_REMOVED` breaking change.
    *   If an old property's type differs from the new property's type, it's a `TYPE_CHANGED` breaking change.
    *   If an old property was optional but is now required, it's a `REQUIRED_STATUS_CHANGED` breaking change.
4.  **Report Generation**: Compiles all detected breaking changes into a comprehensive JSON report, indicating the overall compatibility status.

## Usage (within the Agent Framework)

This skill is intended to be executed by the `qa-tdd-engineer` agent. It would typically be invoked during a CI/CD pipeline step, a pull request review, or as part of a pre-deployment check. The agent would provide the old and new schema definitions (e.g., from version control or a schema registry) to the `analyze_schema_compatibility` function.

```python
# Example of how an agent might use the skill
import json

# Assume these come from version control or a schema registry
old_schema_content = """{
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"}
    },
    "required": ["id"]
}"""

new_schema_content = """{
    "type": "object",
    "properties": {
        "id": {"type": "number"}, # Breaking: type change
        "email": {"type": "string"} # Non-breaking: new optional prop
    },
    "required": ["id"]
}"""

# Call the analysis function
# from workflow import analyze_schema_compatibility
# compatibility_report = analyze_schema_compatibility(old_schema_content, new_schema_content)
# print(json.dumps(compatibility_report, indent=2))
```

## Limitations

This initial version of the auditor focuses on fundamental breaking changes related to property presence, types, and required status. More advanced JSON Schema constructs (like `oneOf`, `anyOf`, `allOf`, `not`, `patternProperties`, `additionalProperties`, array item changes, and `enum` value modifications) are not yet fully supported. Future iterations may expand coverage to these more complex scenarios.
