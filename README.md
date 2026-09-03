# Data-Engineering-Portfolio-Project-01
This is an end-to-end insurance data engineering project, implementing a Medallion Architecture (Bronze, Silver, Gold) to transform raw policy, premium, and claims data into trusted analytical datasets for reporting and decision-making.

## Project Overview

This project demonstrates the design and implementation of an end-to-end data engineering solution for processing insurance data.

The objective is to transform raw data received from external business partners into trusted, analytics-ready datasets that support operational reporting and business decision-making.

The solution follows a modern Medallion Architecture approach inspired by industry-standard Lakehouse patterns:

Raw Files → Bronze → Silver → Gold → Reporting

## Business Problem

Insurance data received from external partners cannot always be assumed to be correct, complete, or consistent.

Data quality issues such as:

- Missing values
- Invalid policy references
- Duplicate records
- Incorrect datatypes
- Inconsistent business rules

must be identified and resolved before data can be trusted for reporting and analytics.

The goal of this project is to build a reusable pipeline capable of validating, transforming and preparing insurance datasets for consumption by reporting tools.

---

## Datasets Used

The project uses five source datasets:

| Dataset | Description |
|----------|-------------|
| partners.csv | Business partner information |
| products.csv | Product master data |
| policies.csv | Policy level information |
| premiums.csv | Premium transactions |
| claims.csv | Insurance claims data |

---

## Architecture
## Bronze Layer

The Bronze layer ingests raw source files into the medallion architecture.

Features:

- Reads source CSV files from Data/Raw
- Adds source_file metadata column
- Adds load_timestamp metadata column
- Writes data to Data/Bronze
- Generates ingestion audit logs
- Records record counts and load status

### Silver Layer

Purpose:
Create clean, validated datasets.

Activities:
- Remove duplicates
- Standardize formats
- Data type corrections
- Null handling
- Business rule validation
- Create rejected records table

### Gold Layer

Purpose:
Create business-ready datasets.

Activities:
- Insurance KPI calculations
- Claims analysis
- Premium analysis
- Partner performance metrics
- Reporting tables

---

## Technology Stack

| Technology | Purpose |
|------------|---------|
| Python | Data processing |
| Pandas | Data transformation |
| SQL | Data modelling |
| Git | Version control |
| GitHub | Source control |
| Logging | Pipeline monitoring |
| Power BI | Reporting |
| Databricks (Future Enhancement) | Lakehouse implementation |

---
