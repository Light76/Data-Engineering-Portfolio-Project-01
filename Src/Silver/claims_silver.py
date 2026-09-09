import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BRONZE_PATH = Path("Data/Bronze/claims.csv")

SILVER_PATH = Path(
    "Data/Silver/claims_clean.csv"
)

REJECT_PATH = Path(
    "Data/Rejects/claims_rejected.csv"
)

# ============================================
# Load Bronze Data
# ============================================

df = pd.read_csv(BRONZE_PATH)

rows_before = len(df)

print(f"Rows Loaded: {rows_before}")

# ============================================
# Standardize Text Fields
# ============================================

df["claim_outcome"] = (
    df["claim_outcome"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================
# Remove Exact Duplicates
# ============================================

rows_before_dedup = len(df)

df = df.drop_duplicates()

duplicates_removed = (
    rows_before_dedup - len(df)
)

# ============================================
# Rejected Records
# ============================================

valid_outcomes = [
    "Paid",
    "Declined",
    "Under Investigation"
]

reject_mask = (

    df["claim_id"].isnull()

    |

    df["policy_id"].isnull()

    |

    ~df["claim_outcome"].isin(
        valid_outcomes
    )

)

rejected_df = df[
    reject_mask
].copy()

# ============================================
# Add Rejection Reason
# ============================================

rejected_df["rejection_reason"] = ""

rejected_df.loc[
    rejected_df["claim_id"].isnull(),
    "rejection_reason"
] += "Missing Claim ID; "

rejected_df.loc[
    rejected_df["policy_id"].isnull(),
    "rejection_reason"
] += "Missing Policy ID; "

rejected_df.loc[
    ~rejected_df["claim_outcome"].isin(
        valid_outcomes
    ),
    "rejection_reason"
] += "Invalid Claim Outcome; "

# ============================================
# Clean Records
# ============================================

clean_df = df[
    ~reject_mask
].copy()

# ============================================
# Save Outputs
# ============================================

clean_df.to_csv(
    SILVER_PATH,
    index=False
)

rejected_df.to_csv(
    REJECT_PATH,
    index=False
)

# ============================================
# Metrics
# ============================================

print("\nSILVER PIPELINE RESULTS")

print(
    f"Duplicates Removed: "
    f"{duplicates_removed}"
)

print(
    f"Clean Records: "
    f"{len(clean_df)}"
)

print(
    f"Rejected Records: "
    f"{len(rejected_df)}"
)

print(
    f"Silver File Saved: "
    f"{SILVER_PATH}"
)

print(
    f"Reject File Saved: "
    f"{REJECT_PATH}"
)