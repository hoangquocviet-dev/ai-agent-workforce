---
name: JSON Schema Backward Compatibility Auditor
description: Analyzes two JSON schemas (old and new) to detect backward-incompatible changes that could break existing consumers, focusing on property removals, type changes, and required status modifications.
agent: qa-tdd-engineer
version: 1.0.0
---

## JSON Schema Backward Compatibility Auditor

This skill helps maintain API stability by identifying potential breaking changes between different versions of JSON schemas. It's crucial for `qa-tdd-engineer` agents to ensure that schema evolution doesn't inadvertently disrupt existing clients or services.

### Core Functionality

The auditor takes two JSON schema definitions (an 'old' version and a 'new' version) and performs a deep comparison to pinpoint changes that violate backward compatibility. It focuses on critical aspects such as:

*   **Required Property Changes**: Detects if an optional property becomes required, or if a previously required property is removed.
*   **Property Type Changes**: Identifies changes in the expected data type of a property (e.g., `string` to `number`).
*   **Property Removal**: Flags properties present in the old schema but missing in the new one.

### How it Works

1.  **Input**: Two JSON schema strings (or parsed dictionaries) representing the old and new versions.
2.  **Parsing**: The schemas are parsed into internal representations.
3.  **Comparison**: The skill recursively compares properties and their attributes (like `type` and `required` status) across both schemas.
4.  **Reporting**: A detailed report is generated, listing all detected backward-incompatible changes, categorized by type and location within the schema.

### Benefits

*   **Prevents API Breakages**: Proactively identifies changes that would break existing clients.
*   **Enhances Collaboration**: Provides clear feedback during schema design reviews.
*   **Automates Compliance**: Integrates into CI/CD pipelines to enforce schema evolution policies.
*   **Supports Versioning**: Essential for managing multiple API versions gracefully.

### Example Use Case

Imagine an API team is updating a user profile schema. The auditor would flag if they accidentally change a `username` from `string` to `number`, or if they remove the `email` property which was previously `required`, thus preventing a deployment that would break all existing user management clients.

### Limitations

*   Currently focuses on top-level properties and direct nested object properties. More complex schema constructs (e.g., `oneOf`, `anyOf`, `allOf`, `not`, `patternProperties`, `additionalProperties`, array item changes, enum value changes) are not fully covered in this initial version.
*   Assumes valid JSON schema input.
*   Does not validate the *semantics* of changes, only structural and type compatibility.

This skill provides a foundational layer for robust API contract management within the `qa-tdd-engineer`'s toolkit, ensuring that schema evolution is a controlled and safe process.
