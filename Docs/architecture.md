# Architecture Overview

## Project Objective

Build an end-to-end Insurance Data Engineering Pipeline using the Medallion Architecture approach.

---

## Source Layer (Raw)

The Raw layer contains source files received from external business partners.

Datasets:

- Claims
- Policies
- Premiums
- Partners
- Products

Location:

Data/Raw

Purpose:

- Preserve original source files
- Maintain source system integrity
- Provide traceability

---

## Bronze Layer

The Bronze layer ingests raw files and enriches them with metadata.

Metadata Added:

- source_file
- load_timestamp

Location:

Data/Bronze

Audit Log:

Logs/ingestion_log.csv

Purpose:

- Data ingestion
- Metadata enrichment
- Data lineage tracking
- Audit logging

---

## Silver Layer

The Silver layer will perform data quality checks and cleansing.

Planned Features:

- Schema validation
- Missing value checks
- Duplicate detection
- Data standardization

Location:

Data/Silver

---

## Gold Layer

The Gold layer will contain business-ready datasets for reporting and analytics.

Planned Features:

- KPI calculations
- Aggregated business metrics
- Reporting datasets

Location:

Data/Gold

---

## Audit and Monitoring

The ingestion process generates operational logs containing:

- Source file name
- Records loaded
- Load timestamp
- Status

Location:

Logs/ingestion_log.csv

---

## Technology Stack

- Python
- Pandas
- Git
- GitHub
- VS Code

Future Technologies:

- Databricks
- PySpark
- Delta Lake
- Power BI