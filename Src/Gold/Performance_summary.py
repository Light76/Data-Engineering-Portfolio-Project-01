"""
performance_summary.py

Purpose:
Generate insurance performance KPIs

Metrics:
- Loss Ratio
- Claims Frequency
- Claim Approval Rate
- Premium Collection Rate

Output:
Data/Gold/performance_summary.csv
"""

import pandas as pd
from pathlib import Path


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CLAIMS_FILE = BASE_DIR / "Data" / "Silver" / "claims_clean.csv"
PREMIUMS_FILE = BASE_DIR / "Data" / "Silver" / "premiums_clean.csv"
POLICIES_FILE = BASE_DIR / "Data" / "Silver" / "policies_clean.csv"

OUTPUT_FILE = BASE_DIR / "Data" / "Gold" / "performance_summary.csv"


# =============================================================================
# LOAD DATA
# =============================================================================

print("=" * 60)
print("PERFORMANCE SUMMARY")
print("=" * 60)

try:
    claims_df = pd.read_csv(CLAIMS_FILE)
    premiums_df = pd.read_csv(PREMIUMS_FILE)
    policies_df = pd.read_csv(POLICIES_FILE)

except Exception as e:
    print(f"Error loading data: {e}")
    raise

print(f"Claims records   : {len(claims_df):,}")
print(f"Premium records  : {len(premiums_df):,}")
print(f"Policy records   : {len(policies_df):,}")


# =============================================================================
# DATA PREPARATION
# =============================================================================

claims_df["claim_amount"] = pd.to_numeric(
    claims_df["claim_amount"],
    errors="coerce"
).fillna(0)

claims_df["paid_amount"] = pd.to_numeric(
    claims_df["paid_amount"],
    errors="coerce"
).fillna(0)

premiums_df["premium_due"] = pd.to_numeric(
    premiums_df["premium_due"],
    errors="coerce"
).fillna(0)

premiums_df["premium_paid"] = pd.to_numeric(
    premiums_df["premium_paid"],
    errors="coerce"
).fillna(0)

claims_df["claim_outcome"] = (
    claims_df["claim_outcome"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# =============================================================================
# BASE METRICS
# =============================================================================

number_of_claims = len(claims_df)

number_of_policies = len(policies_df)

paid_claims = (
    claims_df["claim_outcome"] == "Paid"
).sum()

total_claims_paid = claims_df["paid_amount"].sum()

total_premiums_due = premiums_df["premium_due"].sum()

total_premiums_collected = premiums_df["premium_paid"].sum()


# =============================================================================
# KPI CALCULATIONS
# =============================================================================

loss_ratio_pct = (
    (total_claims_paid / total_premiums_collected) * 100
    if total_premiums_collected > 0
    else 0
)

claims_frequency_pct = (
    (number_of_claims / number_of_policies) * 100
    if number_of_policies > 0
    else 0
)

claim_approval_rate_pct = (
    (paid_claims / number_of_claims) * 100
    if number_of_claims > 0
    else 0
)

premium_collection_rate_pct = (
    (total_premiums_collected / total_premiums_due) * 100
    if total_premiums_due > 0
    else 0
)


# =============================================================================
# BUILD OUTPUT
# =============================================================================

performance_summary = pd.DataFrame(
    [{
        "loss_ratio_pct": round(loss_ratio_pct, 2),
        "claims_frequency_pct": round(claims_frequency_pct, 2),
        "claim_approval_rate_pct": round(claim_approval_rate_pct, 2),
        "premium_collection_rate_pct": round(
            premium_collection_rate_pct, 2
        )
    }]
)


# =============================================================================
# SAVE OUTPUT
# =============================================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

performance_summary.to_csv(
    OUTPUT_FILE,
    index=False
)


# =============================================================================
# DISPLAY RESULTS
# =============================================================================

print()
print("PERFORMANCE METRICS")
print("-" * 60)

print(f"Loss Ratio               : {loss_ratio_pct:.2f}%")
print(f"Claims Frequency         : {claims_frequency_pct:.2f}%")
print(f"Claim Approval Rate      : {claim_approval_rate_pct:.2f}%")
print(f"Premium Collection Rate  : {premium_collection_rate_pct:.2f}%")

print()
print(f"Output saved to: {OUTPUT_FILE}")

print()
print("Performance summary completed successfully.")
print("=" * 60)