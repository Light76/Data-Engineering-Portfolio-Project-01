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

df["claim_type"] = (
    df["claim_type"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================
# Convert Date Columns
# ============================================

df["claim_date"] = pd.to_datetime(
    df["claim_date"],
    errors="coerce"
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
# Valid Values
# ============================================

valid_outcomes = [
    "Paid",
    "Declined",
    "Under Investigation"
]

valid_claim_types = [
    "Death",
    "Disability",
    "Retrenchment"
]

# ============================================
# Rejection Logic
# ============================================

reject_mask = (

    df["claim_id"].isnull()

    |

    df["policy_id"].isnull()

    |

    df["claim_date"].isnull()

    |

    ~df["claim_type"].isin(
        valid_claim_types
    )

    |

    ~df["claim_outcome"].isin(
        valid_outcomes
    )

    |

    (df["claim_amount"] < 0)

    |

    (df["paid_amount"] < 0)

)

# ============================================
# Rejected Records
# ============================================

rejected_df = df[
    reject_mask
].copy()

# ============================================
# Rejection Reasons
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
    rejected_df["claim_date"].isnull(),
    "rejection_reason"
] += "Invalid Or Missing Claim Date; "

rejected_df.loc[
    ~rejected_df["claim_type"].isin(
        valid_claim_types
    ),
    "rejection_reason"
] += "Invalid Claim Type; "

rejected_df.loc[
    ~rejected_df["claim_outcome"].isin(
        valid_outcomes
    ),
    "rejection_reason"
] += "Invalid Claim Outcome; "

rejected_df.loc[
    rejected_df["claim_amount"] < 0,
    "rejection_reason"
] += "Negative Claim Amount; "

rejected_df.loc[
    rejected_df["paid_amount"] < 0,
    "rejection_reason"
] += "Negative Paid Amount; "

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

print("\nCLAIMS SILVER RESULTS")

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