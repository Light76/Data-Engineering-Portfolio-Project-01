"""
claims_summary.py

Purpose:
Generate claims metrics from claims_clean.csv

Metrics:
- Number of Claims
- Total Claim Amount
- Paid Claims
- Declined Claims
- Claims Paid Amount

Output:
Data/Gold/claims_summary.csv
"""

import pandas as pd
from pathlib import Path


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "Data" / "Silver" / "claims_clean.csv"
OUTPUT_FILE = BASE_DIR / "Data" / "Gold" / "claims_summary.csv"


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 60)
print("CLAIMS SUMMARY")
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

df["claim_amount"] = pd.to_numeric(
    df["claim_amount"],
    errors="coerce"
).fillna(0)

df["paid_amount"] = pd.to_numeric(
    df["paid_amount"],
    errors="coerce"
).fillna(0)

df["claim_outcome"] = (
    df["claim_outcome"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# =============================================================================
# CLAIM METRICS
# =============================================================================

number_of_claims = len(df)

total_claim_amount = df["claim_amount"].sum()

paid_claims = (
    df["claim_outcome"] == "Paid"
).sum()

declined_claims = (
    df["claim_outcome"] == "Declined"
).sum()

claims_paid_amount = df["paid_amount"].sum()


# =============================================================================
# BUILD OUTPUT
# =============================================================================

claims_summary = pd.DataFrame(
    [{
        "number_of_claims": int(number_of_claims),
        "total_claim_amount": round(total_claim_amount, 2),
        "paid_claims": int(paid_claims),
        "declined_claims": int(declined_claims),
        "claims_paid_amount": round(claims_paid_amount, 2)
    }]
)


# =============================================================================
# SAVE OUTPUT
# =============================================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

claims_summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# DISPLAY RESULTS
# =============================================================================

print()
print("CLAIMS METRICS")
print("-" * 60)

print(f"Number of Claims     : {number_of_claims:,}")
print(f"Total Claim Amount   : R {total_claim_amount:,.2f}")
print(f"Paid Claims          : {paid_claims:,}")
print(f"Declined Claims      : {declined_claims:,}")
print(f"Claims Paid Amount   : R {claims_paid_amount:,.2f}")

print()
print(f"Output saved to: {OUTPUT_FILE}")

print()
print("Claims summary completed successfully.")
print("=" * 60)