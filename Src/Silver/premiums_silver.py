import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BRONZE_PATH = Path("Data/Bronze/premiums.csv")

SILVER_PATH = Path(
    "Data/Silver/premiums_clean.csv"
)

REJECT_PATH = Path(
    "Data/Rejects/premiums_rejected.csv"
)

# ============================================
# Load Bronze Data
# ============================================

df = pd.read_csv(BRONZE_PATH)

rows_before = len(df)

print(f"Rows Loaded: {rows_before}")

# ============================================
# Standardize Payment Status
# ============================================

df["payment_status"] = (
    df["payment_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================
# Convert Date Columns
# ============================================

date_columns = [
    "premium_month",
    "payment_date"
]

for column in date_columns:

    if column in df.columns:

        df[column] = pd.to_datetime(
            df[column],
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
# Valid Statuses
# ============================================

valid_statuses = [
    "Paid",
    "Partial",
    "Failed"
]

# ============================================
# Rejection Logic
# ============================================

reject_mask = (

    df["transaction_id"].isnull()

    |

    df["policy_id"].isnull()

    |

    ~df["payment_status"].isin(
        valid_statuses
    )

    |

    (df["premium_due"] < 0)

    |

    (df["premium_paid"] < 0)

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
    rejected_df["transaction_id"].isnull(),
    "rejection_reason"
] += "Missing Transaction ID; "

rejected_df.loc[
    rejected_df["policy_id"].isnull(),
    "rejection_reason"
] += "Missing Policy ID; "

rejected_df.loc[
    ~rejected_df["payment_status"].isin(
        valid_statuses
    ),
    "rejection_reason"
] += "Invalid Payment Status; "

rejected_df.loc[
    rejected_df["premium_due"] < 0,
    "rejection_reason"
] += "Negative Premium Due; "

rejected_df.loc[
    rejected_df["premium_paid"] < 0,
    "rejection_reason"
] += "Negative Premium Paid; "

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

print("\nPREMIUMS SILVER RESULTS")

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