import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BRONZE_PATH = Path("Data/Bronze/partners.csv")

SILVER_PATH = Path(
    "Data/Silver/partners_clean.csv"
)

REJECT_PATH = Path(
    "Data/Rejects/partners_rejected.csv"
)

# ============================================
# Load Bronze Data
# ============================================

df = pd.read_csv(BRONZE_PATH)

rows_before = len(df)

print(f"Rows Loaded: {rows_before}")

# ============================================
# Standardize Status
# ============================================

df["status"] = (
    df["status"]
    .astype(str)
    .str.strip()
    .str.title()
)

# ============================================
# Convert Date Column
# ============================================

df["onboard_date"] = pd.to_datetime(
    df["onboard_date"],
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
    "Active",
    "Inactive"
]

# ============================================
# Rejection Logic
# ============================================

reject_mask = (

    df["partner_id"].isnull()

    |

    df["partner_name"].isnull()

    |

    df["partner_type"].isnull()

    |

    df["province"].isnull()

    |

    df["onboard_date"].isnull()

    |

    ~df["status"].isin(
        valid_statuses
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
    rejected_df["partner_id"].isnull(),
    "rejection_reason"
] += "Missing Partner ID; "

rejected_df.loc[
    rejected_df["partner_name"].isnull(),
    "rejection_reason"
] += "Missing Partner Name; "

rejected_df.loc[
    rejected_df["partner_type"].isnull(),
    "rejection_reason"
] += "Missing Partner Type; "

rejected_df.loc[
    rejected_df["province"].isnull(),
    "rejection_reason"
] += "Missing Province; "

rejected_df.loc[
    rejected_df["onboard_date"].isnull(),
    "rejection_reason"
] += "Invalid Or Missing Onboard Date; "

rejected_df.loc[
    ~rejected_df["status"].isin(
        valid_statuses
    ),
    "rejection_reason"
] += "Invalid Status; "

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

print("\nPARTNERS SILVER RESULTS")

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