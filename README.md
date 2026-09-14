# Data Engineering Portfolio Project 01

## Overview

This project demonstrates the design and implementation of an end-to-end Insurance Data Engineering solution using Python, Pandas, and the Medallion Architecture approach.

The solution transforms raw insurance data into trusted, business-ready information through data ingestion, data quality validation, referential integrity checks, cleansing, transformation, automation, and reporting preparation.

---

## Project Objective

Build a reusable and automated insurance data platform capable of:

- Ingesting raw insurance data
- Validating data quality
- Enforcing referential integrity
- Managing rejected records
- Generating business-ready datasets
- Producing insurance KPIs
- Supporting Power BI reporting

---

## Business Problem

Insurance data received from business partners cannot always be assumed to be complete, accurate, or consistent.

Common data issues include:

- Missing values
- Duplicate records
- Invalid references
- Incorrect dates
- Invalid lookup values
- Negative financial values
- Orphan records
- Data standardisation issues

Before data can be trusted for reporting and analysis, these issues must be identified, managed, and controlled.

This project demonstrates how modern data engineering practices can be used to solve these challenges.

---

## Solution Architecture

The solution follows the Medallion Architecture pattern.

Raw
 ↓
Bronze
 ↓
Silver
 ↓
Integrity
 ↓
Gold
 ↓
Reporting


### Raw Layer

Stores source files exactly as received.

Datasets:

- Claims
- Policies
- Premiums
- Partners
- Products

Location:

Data/Raw

### Bronze Layer

The Bronze layer ingests source files and enriches them with metadata.

Features:

- Source file tracking
- Load timestamp capture
- Metadata enrichment
- Audit logging

Location:

Data/Bronze

Logs:

Logs/ingestion_log.csv

---

### Silver Layer

The Silver layer focuses on cleansing and validation.

Features:

- Null checks
- Mandatory field validation
- Duplicate detection
- Data type validation
- Business rule validation
- Standardisation
- Reject handling

Location:

Data/Silver

Rejects:

Data/Rejects

---

### Referential Integrity Layer

The Referential Integrity Framework validates relationships across datasets.

Checks include:

- Claims → Policies
- Premiums → Policies
- Policies → Products
- Policies → Partners

Outputs:

Data/Integrity

- orphan_claims.csv
- orphan_premiums.csv
- orphan_policy_products.csv
- orphan_policy_partners.csv
- referential_integrity_report.csv

---

### Gold Layer

The Gold layer produces business-ready datasets for reporting and analytics.

Summary Outputs:

portfolio_summary.csv

premiums_summary.csv

claims_summary.csv

performance_summary.csv


Dimensional Outputs:

policy_performance_by_dimension.csv

premium_performance_by_dimension.csv

claims_performance_by_dimension.csv

Dimensions Supported:

- Month
- Partner
- Product
- Product Type
- Province

---

### Reporting Layer

Gold datasets are consumed through Power BI dashboards to support management reporting and business analysis.

Business Areas Covered:

- Portfolio Performance
- Premium Performance
- Claims Performance
- Business Performance

Location:

Reports/

---

## Frameworks Developed

### Configuration Framework

Manages configuration settings and centralises file path management.

### Data Quality Framework

Provides reusable validation controls across all datasets.

Validations include:

- Completeness
- Uniqueness
- Validity
- Accuracy
- Date Validation

### Referential Integrity Framework

Validates relationships between datasets and identifies orphan records.

### Logging Framework

Provides auditability, monitoring, and troubleshooting support.

### Reject Framework

Captures invalid records and stores rejection reasons for investigation.

### Test Framework

Provides validation and testing of framework functionality.

Location:

Src/Frameworks

---

## Business KPIs Generated

### Portfolio KPIs

- Total Policies
- Active Policies
- New Policies
- Lapsed Policies
- Cancelled Policies

### Premium KPIs

- Premium Due
- Premium Collected
- Collection Rate

### Claims KPIs

- Number of Claims
- Claim Amount
- Paid Claims
- Declined Claims
- Claims Paid Amount

### Performance KPIs

- Loss Ratio
- Claims Frequency
- Average Claim Amount
- Average Premium per Policy

---

## Project Structure


Data
│
├── Raw
├── Bronze
├── Silver
├── Rejects
├── Integrity
└── Gold

Docs
│
├── Project_charter.md
├── Architecture.md
└── Data_dictionary.md

Logs
│
├── ingestion_log.csv
├── data_quality_log.csv
└── Pipeline.log

Reports

Src
│
├── Bronze
├── Silver
├── Gold
└── Frameworks

Tests


## Automation

The solution is designed to be repeatable and reusable.

Features include:

- Configuration-driven execution
- Modular architecture
- Automated processing
- Centralised logging
- Single pipeline execution

Pipeline execution:

python Run_pipeline.py


## Technology Stack

| Technology | Purpose |
|------------|----------|
| Python | Data processing |
| Pandas | Data transformation |
| NumPy | Calculations |
| CSV | Data storage |
| Git | Version control |
| GitHub | Source control |
| Power BI | Reporting and analytics |
| VS Code | Development environment |

---

## Business Outcomes

The solution provides:

- Trusted reporting datasets
- Improved data quality visibility
- Partner performance analysis
- Product performance analysis
- Portfolio monitoring
- Premium monitoring
- Claims monitoring
- Business KPI reporting
- Data-driven decision making

---

## Key Data Engineering Concepts Demonstrated

 Medallion Architecture

 Data Ingestion

 Metadata Management

 Data Quality Frameworks

 Reject Management

 Referential Integrity

 Audit Logging

 Root Cause Analysis

 Data Transformation

 KPI Development

 Pipeline Automation

 Reporting Enablement

---

## Project Status

### Completed 

- Raw Layer
- Bronze Layer
- Metadata Tracking
- Ingestion Logging
- Data Quality Framework
- Silver Layer
- Reject Framework
- Referential Integrity Framework
- Root Cause Analysis
- Gold Layer
- Portfolio Analytics
- Premium Analytics
- Claims Analytics
- Performance Analytics
- Dimensional Analytics
- Pipeline Automation

### In Progress 🚧

- Power BI Dashboard Development

### Planned 📋

- Dashboard Enhancements
- Advanced Analytics
- Cloud Migration (Future Enhancement)

---

## Final Outcome

This project demonstrates how raw insurance data can be transformed into trusted, business-ready information through a structured and automated data engineering pipeline.

The final solution combines data quality, integrity validation, business KPI generation, automation, and reporting readiness to support management reporting and analytical decision-making.