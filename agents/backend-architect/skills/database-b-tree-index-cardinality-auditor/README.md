# Database B-Tree Index Cardboard & Selectivity Auditor

An autonomous backend engineering skill that analyzes DDL schemas to detect low-selectivity B-Tree indexes, high write-amplification risks, and left-prefix index redundancies in relational databases.

## Features
- **Redundancy Detection**: Flags single-column indexes that are completely covered by existing composite indexes.
- **Selectivity Analysis**: Warns against indexing low-cardinality boolean/status columns without partial filtering.
- **Write Amplification Mitigation**: Detects excessive indexing per table to protect write-heavy OLTP workloads.

## Execution
```bash
python3 workflow.py
```
