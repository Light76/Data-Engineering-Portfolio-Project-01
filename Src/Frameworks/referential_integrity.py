import pandas as pd
from pathlib import Path

# ============================================
# Paths
# ============================================

CLAIMS_PATH = Path(
    "Data/Silver/claims_clean.csv"
)

PREMIUMS_PATH = Path(
    "Data/Silver/premiums_clean.csv"
)

POLICIES_PATH = Path(
    "Data/Silver/policies_clean.csv"
)

PRODUCTS_PATH = Path(
    "Data/Silver/products_clean.csv"
)

PARTNERS_PATH = Path(
    "Data/Silver/partners_clean.csv"
)

# Rejected Data

REJECTED_POLICIES_PATH = Path(
    "Data/Rejects/policies_rejected.csv"
)

REJECTED_PRODUCTS_PATH = Path(
    "Data/Rejects/products_rejected.csv"
)

REJECTED_PARTNERS_PATH = Path(
    "Data/Rejects/partners_rejected.csv"
)

# Output Folder

INTEGRITY_PATH = Path(
    "Data/Integrity"
)

# ============================================
# Load Datasets
# ============================================

claims_df = pd.read_csv(
    CLAIMS_PATH
)

premiums_df = pd.read_csv(
    PREMIUMS_PATH
)

policies_df = pd.read_csv(
    POLICIES_PATH
)

products_df = pd.read_csv(
    PRODUCTS_PATH
)

partners_df = pd.read_csv(
    PARTNERS_PATH
)

policies_rejected_df = pd.read_csv(
    REJECTED_POLICIES_PATH
)

products_rejected_df = pd.read_csv(
    REJECTED_PRODUCTS_PATH
)

partners_rejected_df = pd.read_csv(
    REJECTED_PARTNERS_PATH
)

# ============================================
# Claims -> Policies
# ============================================

orphan_claims = claims_df[
    ~claims_df["policy_id"].isin(
        policies_df["policy_id"]
    )
].copy()

orphan_claims[
    "integrity_failure_reason"
] = ""

orphan_claims.loc[
    orphan_claims["policy_id"].isin(
        policies_rejected_df["policy_id"]
    ),
    "integrity_failure_reason"
] = (
    "Referenced policy rejected during Silver processing"
)

orphan_claims.loc[
    orphan_claims[
        "integrity_failure_reason"
    ] == "",
    "integrity_failure_reason"
] = (
    "Referenced policy does not exist in source data"
)

# ============================================
# Premiums -> Policies
# ============================================

orphan_premiums = premiums_df[
    ~premiums_df["policy_id"].isin(
        policies_df["policy_id"]
    )
].copy()

orphan_premiums[
    "integrity_failure_reason"
] = ""

orphan_premiums.loc[
    orphan_premiums["policy_id"].isin(
        policies_rejected_df["policy_id"]
    ),
    "integrity_failure_reason"
] = (
    "Referenced policy rejected during Silver processing"
)

orphan_premiums.loc[
    orphan_premiums[
        "integrity_failure_reason"
    ] == "",
    "integrity_failure_reason"
] = (
    "Referenced policy does not exist in source data"
)

# ============================================
# Policies -> Products
# ============================================

orphan_policy_products = policies_df[
    ~policies_df["product_id"].isin(
        products_df["product_id"]
    )
].copy()

orphan_policy_products[
    "integrity_failure_reason"
] = ""

orphan_policy_products.loc[
    orphan_policy_products["product_id"].isin(
        products_rejected_df["product_id"]
    ),
    "integrity_failure_reason"
] = (
    "Referenced product rejected during Silver processing"
)

orphan_policy_products.loc[
    orphan_policy_products[
        "integrity_failure_reason"
    ] == "",
    "integrity_failure_reason"
] = (
    "Referenced product does not exist in source data"
)

# ============================================
# Policies -> Partners
# ============================================

orphan_policy_partners = policies_df[
    ~policies_df["partner_id"].isin(
        partners_df["partner_id"]
    )
].copy()

orphan_policy_partners[
    "integrity_failure_reason"
] = ""

orphan_policy_partners.loc[
    orphan_policy_partners["partner_id"].isin(
        partners_rejected_df["partner_id"]
    ),
    "integrity_failure_reason"
] = (
    "Referenced partner rejected during Silver processing"
)

orphan_policy_partners.loc[
    orphan_policy_partners[
        "integrity_failure_reason"
    ] == "",
    "integrity_failure_reason"
] = (
    "Referenced partner does not exist in source data"
)

# ============================================
# Save Orphan Files
# ============================================

orphan_claims.to_csv(
    INTEGRITY_PATH /
    "orphan_claims.csv",
    index=False
)

orphan_premiums.to_csv(
    INTEGRITY_PATH /
    "orphan_premiums.csv",
    index=False
)

orphan_policy_products.to_csv(
    INTEGRITY_PATH /
    "orphan_policy_products.csv",
    index=False
)

orphan_policy_partners.to_csv(
    INTEGRITY_PATH /
    "orphan_policy_partners.csv",
    index=False
)

# ============================================
# Root Cause Summary
# ============================================

rejected_silver_issues = (

    (
        orphan_claims[
            "integrity_failure_reason"
        ]
        ==
        "Referenced policy rejected during Silver processing"
    ).sum()

    +

    (
        orphan_premiums[
            "integrity_failure_reason"
        ]
        ==
        "Referenced policy rejected during Silver processing"
    ).sum()

    +

    (
        orphan_policy_products[
            "integrity_failure_reason"
        ]
        ==
        "Referenced product rejected during Silver processing"
    ).sum()

    +

    (
        orphan_policy_partners[
            "integrity_failure_reason"
        ]
        ==
        "Referenced partner rejected during Silver processing"
    ).sum()

)

source_data_issues = (

    len(orphan_claims)
    +
    len(orphan_premiums)
    +
    len(orphan_policy_products)
    +
    len(orphan_policy_partners)

) - rejected_silver_issues

# ============================================
# Integrity Report
# ============================================

total_issues = (

    len(orphan_claims)
    +
    len(orphan_premiums)
    +
    len(orphan_policy_products)
    +
    len(orphan_policy_partners)

)

status = "PASS"

if total_issues > 0:
    status = "FAIL"

report_df = pd.DataFrame([
    {
        "claims_checked":
            len(claims_df),

        "orphan_claims":
            len(orphan_claims),

        "premiums_checked":
            len(premiums_df),

        "orphan_premiums":
            len(orphan_premiums),

        "policies_checked":
            len(policies_df),

        "orphan_policy_products":
            len(orphan_policy_products),

        "orphan_policy_partners":
            len(orphan_policy_partners),

        "issues_caused_by_rejected_silver_records":
            rejected_silver_issues,

        "issues_caused_by_missing_source_records":
            source_data_issues,

        "total_integrity_issues":
            total_issues,

        "status":
            status
    }
])

report_df.to_csv(
    INTEGRITY_PATH /
    "referential_integrity_report.csv",
    index=False
)

# ============================================
# Console Report
# ============================================

print(
    "\nREFERENTIAL INTEGRITY REPORT V1.1"
)

print("=" * 60)

print(
    f"Claims Checked: {len(claims_df)}"
)

print(
    f"Orphan Claims: {len(orphan_claims)}"
)

print()

print(
    f"Premiums Checked: {len(premiums_df)}"
)

print(
    f"Orphan Premiums: {len(orphan_premiums)}"
)

print()

print(
    f"Policies Checked: {len(policies_df)}"
)

print(
    f"Missing Products: {len(orphan_policy_products)}"
)

print(
    f"Missing Partners: {len(orphan_policy_partners)}"
)

print()

print(
    f"Issues From Rejected Silver Records: "
    f"{rejected_silver_issues}"
)

print(
    f"Issues From Missing Source Records: "
    f"{source_data_issues}"
)

print()

print(
    f"Total Issues: {total_issues}"
)

print(
    f"Status: {status}"
)

print("=" * 60)