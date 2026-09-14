"""
premiums_summary.py

Purpose:
Generate premium collection metrics from premiums_clean.csv

Metrics:
- Total Premium Due
- Total Premium Collected
- Collection Rate (%)

Output:
Data/Gold/premiums_summary.csv
"""

import pandas as pd
from pathlib import Path


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "Data" / "Silver" / "premiums_clean.csv"
OUTPUT_FILE = BASE_DIR / "Data" / "Gold" / "premiums_summary.csv"


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 60)
print("PREMIUMS SUMMARY")
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

df["premium_due"] = pd.to_numeric(
    df["premium_due"],
    errors="coerce"
).fillna(0)

df["premium_paid"] = pd.to_numeric(
    df["premium_paid"],
    errors="coerce"
).fillna(0)


# =============================================================================
# METRICS
# =============================================================================

total_premium_due = df["premium_due"].sum()

total_premium_collected = df["premium_paid"].sum()

collection_rate = (
    (total_premium_collected / total_premium_due) * 100
    if total_premium_due > 0
    else 0
)


# =============================================================================
# BUILD OUTPUT
# =============================================================================

premiums_summary = pd.DataFrame(
    [{
        "total_premium_due": round(total_premium_due, 2),
        "total_premium_collected": round(total_premium_collected, 2),
        "collection_rate_pct": round(collection_rate, 2)
    }]
)


# =============================================================================
# SAVE OUTPUT
# =============================================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

premiums_summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# DISPLAY RESULTS
# =============================================================================

print()
print("PREMIUM COLLECTION METRICS")
print("-" * 60)

print(f"Total Premium Due        : R {total_premium_due:,.2f}")
print(f"Total Premium Collected  : R {total_premium_collected:,.2f}")
print(f"Collection Rate          : {collection_rate:.2f}%")

print()
print(f"Output saved to: {OUTPUT_FILE}")

print()
print("Premiums summary completed successfully.")
print("=" * 60)