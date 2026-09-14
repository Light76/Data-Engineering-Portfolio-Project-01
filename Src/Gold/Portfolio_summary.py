"""
portfolio_summary.py

Purpose:
Generate portfolio-level policy metrics from policies_clean.csv

Metrics:
- Total Policies
- Active Policies
- New Policies (June 2026)
- Lapsed Policies
- Cancelled Policies

Output:
Data/Gold/portfolio_summary.csv
"""

import pandas as pd
from pathlib import Path


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "Data" / "Silver" / "policies_clean.csv"
OUTPUT_FILE = BASE_DIR / "Data" / "Gold" / "portfolio_summary.csv"


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 60)
print("PORTFOLIO SUMMARY")
print("=" * 60)

try:
    df = pd.read_csv(INPUT_FILE)
except Exception as e:
    print(f"Error loading file: {e}")
    raise

print(f"Records loaded: {len(df):,}")


# =============================================================================
# DATA PREPARATION
# =============================================================================

df["inception_date"] = pd.to_datetime(
    df["inception_date"],
    errors="coerce"
)

df["termination_date"] = pd.to_datetime(
    df["termination_date"],
    errors="coerce"
)

df["policy_status"] = (
    df["policy_status"]
    .fillna("")
    .astype(str)
    .str.strip()
    .str.upper()
)


# =============================================================================
# PORTFOLIO METRICS
# =============================================================================

total_policies = len(df)

active_policies = (
    df["policy_status"] == "ACTIVE"
).sum()

new_policies = (
    (df["inception_date"].dt.year == 2026) &
    (df["inception_date"].dt.month == 6)
).sum()

lapsed_policies = (
    df["policy_status"] == "LAPSED"
).sum()

cancelled_policies = (
    df["policy_status"] == "CANCELLED"
).sum()


# =============================================================================
# BUILD OUTPUT
# =============================================================================

portfolio_summary = pd.DataFrame(
    [{
        "total_policies": int(total_policies),
        "active_policies": int(active_policies),
        "new_policies_june_2026": int(new_policies),
        "lapsed_policies": int(lapsed_policies),
        "cancelled_policies": int(cancelled_policies)
    }]
)


# =============================================================================
# SAVE OUTPUT
# =============================================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

portfolio_summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# DISPLAY RESULTS
# =============================================================================

print()
print("PORTFOLIO METRICS")
print("-" * 60)

print(f"Total Policies       : {total_policies:,}")
print(f"Active Policies      : {active_policies:,}")
print(f"New Policies Jun2026 : {new_policies:,}")
print(f"Lapsed Policies      : {lapsed_policies:,}")
print(f"Cancelled Policies   : {cancelled_policies:,}")

print()
print(f"Output saved to: {OUTPUT_FILE}")

print()
print("Portfolio summary completed successfully.")
print("=" * 60)