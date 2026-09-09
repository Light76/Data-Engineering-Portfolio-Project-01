import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BRONZE_PATH = Path("Data/Bronze/policies.csv")

SILVER_PATH = Path(
    "Data/Silver/policies_clean.csv"
)

REJECT_PATH = Path(
    "Data/Rejects/policies_rejected.csv"
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

df["policy_status"] = (
    df["policy_status"]
    .astype(str)
    .str.strip()
    .str.title()
)

df["gender"] = (
    df["gender"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# ============================================
# Standardize Gender Values
# ============================================

df["gender"] = df["gender"].replace({
    "MALE": "M",
    "FEMALE": "F"
})

# ============================================
# Convert Date Columns
# ============================================

date_columns = [
    "inception_date",
    "date_of_birth",
    "termination_date"
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
# Business Rules
# ============================================

valid_genders = [
    "M",
    "F"
]

valid_statuses = [
    "Active",
    "Lapsed",
    "Cancelled"
]

# ============================================
# Rejection Logic
# ============================================

reject_mask = (

    df["policy_id"].isnull()

    |

    df["partner_id"].isnull()

    |

    df["product_id"].isnull()

    |

    ~df["gender"].isin(
        valid_genders
    )

    |

    ~df["policy_status"].isin(
        valid_statuses
    )

    |

    (df["cover_amount"] < 0)

    |

    (df["monthly_premium"] < 0)

    |

    (
        df["termination_date"].notna()
        &
        (
            df["termination_date"]
            <
            df["inception_date"]
        )
    )
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
    rejected_df["policy_id"].isnull(),
    "rejection_reason"
] += "Missing Policy ID; "

rejected_df.loc[
    rejected_df["partner_id"].isnull(),
    "rejection_reason"
] += "Missing Partner ID; "

rejected_df.loc[
    rejected_df["product_id"].isnull(),
    "rejection_reason"
] += "Missing Product ID; "

rejected_df.loc[
    ~rejected_df["gender"].isin(
        valid_genders
    ),
    "rejection_reason"
] += "Invalid Gender; "

rejected_df.loc[
    ~rejected_df["policy_status"].isin(
        valid_statuses
    ),
    "rejection_reason"
] += "Invalid Policy Status; "

rejected_df.loc[
    rejected_df["cover_amount"] < 0,
    "rejection_reason"
] += "Negative Cover Amount; "

rejected_df.loc[
    rejected_df["monthly_premium"] < 0,
    "rejection_reason"
] += "Negative Monthly Premium; "

rejected_df.loc[
    (
        rejected_df["termination_date"].notna()
        &
        (
            rejected_df["termination_date"]
            <
            rejected_df["inception_date"]
        )
    ),
    "rejection_reason"
] += "Termination Date Before Inception Date; "

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

print("\nPOLICIES SILVER RESULTS")

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