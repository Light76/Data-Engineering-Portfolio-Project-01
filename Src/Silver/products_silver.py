import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

BRONZE_PATH = Path("Data/Bronze/products.csv")

SILVER_PATH = Path(
    "Data/Silver/products_clean.csv"
)

REJECT_PATH = Path(
    "Data/Rejects/products_rejected.csv"
)

# ============================================
# Load Bronze Data
# ============================================

df = pd.read_csv(BRONZE_PATH)

rows_before = len(df)

print(f"Rows Loaded: {rows_before}")

# ============================================
# Standardize Product Type
# ============================================

df["product_type"] = (
    df["product_type"]
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
# Valid Product Types
# ============================================

valid_product_types = [
    "Credit Life",
    "Funeral",
    "Disability"
]

# ============================================
# Rejection Logic
# ============================================

reject_mask = (

    df["product_id"].isnull()

    |

    df["product_name"].isnull()

    |

    df["partner_id"].isnull()

    |

    ~df["product_type"].isin(
        valid_product_types
    )

    |

    (df["max_cover"] < 0)

    |

    (df["rate_or_base_premium"] < 0)

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
    rejected_df["product_id"].isnull(),
    "rejection_reason"
] += "Missing Product ID; "

rejected_df.loc[
    rejected_df["product_name"].isnull(),
    "rejection_reason"
] += "Missing Product Name; "

rejected_df.loc[
    rejected_df["partner_id"].isnull(),
    "rejection_reason"
] += "Missing Partner ID; "

rejected_df.loc[
    ~rejected_df["product_type"].isin(
        valid_product_types
    ),
    "rejection_reason"
] += "Invalid Product Type; "

rejected_df.loc[
    rejected_df["max_cover"] < 0,
    "rejection_reason"
] += "Negative Max Cover; "

rejected_df.loc[
    rejected_df["rate_or_base_premium"] < 0,
    "rejection_reason"
] += "Negative Base Premium; "

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

print("\nPRODUCTS SILVER RESULTS")

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