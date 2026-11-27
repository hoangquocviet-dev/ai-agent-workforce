---
name: database-b-tree-index-cardinality-auditor
description: Audits database schema definitions, query execution plans, and migration scripts for B-Tree index cardinality bottlenecks, low-selectivity indexes, and composite index column ordering inefficiencies.
agent: backend-architect
version: 1.0.0
---

# Database B-Tree Index Cardinality & Selectivity Auditor

## Overview
The `database-b-tree-index-cardinality-auditor` skill inspects database DDL statements, migration files, and query patterns to ensure high-throughput systems avoid high-write overhead and low-selectivity scans caused by improper B-Tree index design.

## Core Capabilities
1. **Selectivity Estimation**: Evaluates column uniqueness and cardinality to flag indexes with poor filtering efficiency.
2. **Composite Index Left-Prefix Rule Enforcement**: Validates multi-column index column ordering against frequent query filters.
3. **Over-Indexing Detection**: Identifies redundant prefix indexes that duplicate existing composite indexes.
4. **Write Amplification Risk**: Flags tables with excessive indexes that degrade write/update throughput in OLTP systems.

## Usage
Execute the analysis script against your database schema files or migration directory:
```bash
python3 workflow.py schema_dump.sql
```
