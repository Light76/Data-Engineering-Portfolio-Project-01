"""
Premium_performance_dimension.py

Purpose:
Create a Gold-layer premium performance dataset supporting analysis by:

- Month
- Partner
- Product
- Product Type
- Province

Outputs:
- Data/Gold/premium_performance_by_dimension.csv
- Data/Rejects/premium_performance_dimension_rejects.csv

Expected payment_status values:
- Paid
- Failed
- Partial

Expected premium_month format:
- YYYY-MM-01
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

PREMIUMS_FILE = (
    BASE_DIR
    / "Data"
    / "Silver"
    / "premiums_clean.csv"
)

POLICIES_FILE = (
    BASE_DIR
    / "Data"
    / "Silver"
    / "policies_clean.csv"
)

PARTNERS_FILE = (
    BASE_DIR
    / "Data"
    / "Silver"
    / "partners_clean.csv"
)

PRODUCTS_FILE = (
    BASE_DIR
    / "Data"
    / "Silver"
    / "products_clean.csv"
)

GOLD_OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "Gold"
    / "premium_performance_by_dimension.csv"
)

REJECT_OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "Rejects"
    / "premium_performance_dimension_rejects.csv"
)


# =============================================================================
# EXPECTED VALUES
# =============================================================================

EXPECTED_PAYMENT_STATUSES = {
    "Paid",
    "Failed",
    "Partial",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_csv(file_path, dataset_name):
    """
    Load a CSV file.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"{dataset_name} file not found: {file_path}"
        )

    dataframe = pd.read_csv(file_path)

    print(
        f"{dataset_name:<10}: "
        f"{len(dataframe):,} records loaded"
    )

    return dataframe


def validate_required_columns(
    dataframe,
    required_columns,
    dataset_name
):
    """
    Validate that all required columns exist.
    """

    missing_columns = [
        column
        for column in required_columns
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{dataset_name} is missing required columns: "
            f"{missing_columns}"
        )


def clean_text_columns(
    dataframe,
    columns
):
    """
    Remove leading and trailing spaces from text columns.
    """

    for column in columns:
        dataframe[column] = (
            dataframe[column]
            .astype("string")
            .str.strip()
        )


def validate_unique_key(
    dataframe,
    key_column,
    dataset_name
):
    """
    Check that lookup keys are unique before joining.
    """

    duplicate_count = (
        dataframe[key_column]
        .dropna()
        .duplicated()
        .sum()
    )

    if duplicate_count > 0:
        raise ValueError(
            f"{dataset_name} contains {duplicate_count:,} duplicate "
            f"value(s) in '{key_column}'."
        )


def create_rejection_reason(row):
    """
    Create a reason describing why a premium record was rejected.
    """

    reasons = []

    if row["policy_join"] == "left_only":
        reasons.append(
            "policy_id not found in policies_clean.csv"
        )

        return "; ".join(reasons)

    if pd.isna(row["partner_id"]):
        reasons.append(
            "matched policy has missing partner_id"
        )

    elif row["partner_join"] == "left_only":
        reasons.append(
            "partner_id not found in partners_clean.csv"
        )

    if pd.isna(row["product_id"]):
        reasons.append(
            "matched policy has missing product_id"
        )

    elif row["product_join"] == "left_only":
        reasons.append(
            "product_id not found in products_clean.csv"
        )

    if (
        pd.isna(row["province"])
        or str(row["province"]).strip() == ""
    ):
        reasons.append(
            "matched policy has missing province"
        )

    return "; ".join(reasons)


# =============================================================================
# MAIN PROCESS
# =============================================================================

def main():

    print("=" * 75)
    print("PREMIUM PERFORMANCE BY DIMENSION")
    print("=" * 75)

    # =========================================================================
    # LOAD SILVER DATA
    # =========================================================================

    premiums_df = load_csv(
        PREMIUMS_FILE,
        "Premiums"
    )

    policies_df = load_csv(
        POLICIES_FILE,
        "Policies"
    )

    partners_df = load_csv(
        PARTNERS_FILE,
        "Partners"
    )

    products_df = load_csv(
        PRODUCTS_FILE,
        "Products"
    )

    # =========================================================================
    # VALIDATE REQUIRED COLUMNS
    # =========================================================================

    validate_required_columns(
        premiums_df,
        [
            "transaction_id",
            "policy_id",
            "premium_month",
            "premium_due",
            "premium_paid",
            "payment_status",
        ],
        "Premiums"
    )

    validate_required_columns(
        policies_df,
        [
            "policy_id",
            "partner_id",
            "product_id",
            "province",
        ],
        "Policies"
    )

    validate_required_columns(
        partners_df,
        [
            "partner_id",
            "partner_name",
        ],
        "Partners"
    )

    validate_required_columns(
        products_df,
        [
            "product_id",
            "product_name",
            "product_type",
        ],
        "Products"
    )

    # =========================================================================
    # CLEAN TEXT COLUMNS
    # =========================================================================

    clean_text_columns(
        premiums_df,
        [
            "transaction_id",
            "policy_id",
            "payment_status",
        ]
    )

    clean_text_columns(
        policies_df,
        [
            "policy_id",
            "partner_id",
            "product_id",
            "province",
        ]
    )

    clean_text_columns(
        partners_df,
        [
            "partner_id",
            "partner_name",
        ]
    )

    clean_text_columns(
        products_df,
        [
            "product_id",
            "product_name",
            "product_type",
        ]
    )

    # =========================================================================
    # VALIDATE LOOKUP KEYS
    # =========================================================================

    validate_unique_key(
        policies_df,
        "policy_id",
        "Policies"
    )

    validate_unique_key(
        partners_df,
        "partner_id",
        "Partners"
    )

    validate_unique_key(
        products_df,
        "product_id",
        "Products"
    )

    # =========================================================================
    # PREPARE PREMIUM DATA
    # =========================================================================

    premiums_df["premium_month"] = pd.to_datetime(
        premiums_df["premium_month"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    invalid_date_count = (
        premiums_df["premium_month"]
        .isna()
        .sum()
    )

    if invalid_date_count > 0:
        raise ValueError(
            f"{invalid_date_count:,} invalid premium_month "
            f"value(s). Expected format: YYYY-MM-01."
        )

    invalid_month_day_count = (
        premiums_df["premium_month"].dt.day != 1
    ).sum()

    if invalid_month_day_count > 0:
        raise ValueError(
            f"{invalid_month_day_count:,} premium_month value(s) "
            f"are not the first day of the month."
        )

    premiums_df["premium_due"] = pd.to_numeric(
        premiums_df["premium_due"],
        errors="coerce"
    )

    premiums_df["premium_paid"] = pd.to_numeric(
        premiums_df["premium_paid"],
        errors="coerce"
    )

    invalid_due_count = (
        premiums_df["premium_due"]
        .isna()
        .sum()
    )

    invalid_paid_count = (
        premiums_df["premium_paid"]
        .isna()
        .sum()
    )

    if invalid_due_count > 0:
        raise ValueError(
            f"{invalid_due_count:,} invalid premium_due "
            f"value(s). Expected Decimal."
        )

    if invalid_paid_count > 0:
        raise ValueError(
            f"{invalid_paid_count:,} invalid premium_paid "
            f"value(s). Expected Decimal."
        )

    actual_payment_statuses = set(
        premiums_df["payment_status"]
        .dropna()
        .unique()
    )

    invalid_payment_statuses = sorted(
        actual_payment_statuses
        - EXPECTED_PAYMENT_STATUSES
    )

    if invalid_payment_statuses:
        raise ValueError(
            "Undocumented payment_status values found: "
            f"{invalid_payment_statuses}"
        )

    premiums_df["month"] = (
        premiums_df["premium_month"]
        .dt.strftime("%Y-%m-01")
    )

    # =========================================================================
    # PREPARE LOOKUP TABLES
    # =========================================================================

    policy_lookup = policies_df[
        [
            "policy_id",
            "partner_id",
            "product_id",
            "province",
        ]
    ].copy()

    partner_lookup = partners_df[
        [
            "partner_id",
            "partner_name",
        ]
    ].copy()

    product_lookup = products_df[
        [
            "product_id",
            "product_name",
            "product_type",
        ]
    ].copy()

    # =========================================================================
    # JOIN PREMIUMS TO POLICIES
    # =========================================================================

    premium_detail_df = premiums_df.merge(
        policy_lookup,
        on="policy_id",
        how="left",
        validate="many_to_one",
        indicator="policy_join"
    )

    # =========================================================================
    # JOIN TO PARTNERS
    # =========================================================================

    premium_detail_df = premium_detail_df.merge(
        partner_lookup,
        on="partner_id",
        how="left",
        validate="many_to_one",
        indicator="partner_join"
    )

    # =========================================================================
    # JOIN TO PRODUCTS
    # =========================================================================

    premium_detail_df = premium_detail_df.merge(
        product_lookup,
        on="product_id",
        how="left",
        validate="many_to_one",
        indicator="product_join"
    )

    # =========================================================================
    # IDENTIFY REJECTS
    # =========================================================================

    premium_detail_df["rejection_reason"] = (
        premium_detail_df.apply(
            create_rejection_reason,
            axis=1
        )
    )

    rejection_mask = (
        premium_detail_df["rejection_reason"] != ""
    )

    reject_columns = [
        "transaction_id",
        "policy_id",
        "premium_month",
        "premium_due",
        "premium_paid",
        "payment_status",
        "partner_id",
        "partner_name",
        "product_id",
        "product_name",
        "product_type",
        "province",
        "rejection_reason",
    ]

    rejects_df = premium_detail_df.loc[
        rejection_mask,
        reject_columns
    ].copy()

    if not rejects_df.empty:
        rejects_df["premium_month"] = (
            rejects_df["premium_month"]
            .dt.strftime("%Y-%m-01")
        )

    # =========================================================================
    # KEEP VALID RECORDS
    # =========================================================================

    valid_premium_df = premium_detail_df.loc[
        ~rejection_mask
    ].copy()

    valid_premium_df["paid_transaction"] = (
        valid_premium_df["payment_status"] == "Paid"
    ).astype(int)

    valid_premium_df["failed_transaction"] = (
        valid_premium_df["payment_status"] == "Failed"
    ).astype(int)

    valid_premium_df["partial_transaction"] = (
        valid_premium_df["payment_status"] == "Partial"
    ).astype(int)

    # =========================================================================
    # DEFINE GOLD DIMENSIONS AND COLUMNS
    # =========================================================================

    dimension_columns = [
        "month",
        "partner_id",
        "partner_name",
        "product_id",
        "product_name",
        "product_type",
        "province",
    ]

    gold_columns = dimension_columns + [
        "premium_transactions",
        "paid_transactions",
        "failed_transactions",
        "partial_transactions",
        "total_premium_due",
        "total_premium_collected",
        "outstanding_premium",
        "collection_rate_pct",
    ]

    # =========================================================================
    # CREATE GOLD DATASET
    # =========================================================================

    if valid_premium_df.empty:

        premium_performance_df = pd.DataFrame(
            columns=gold_columns
        )

    else:

        premium_performance_df = (
            valid_premium_df
            .groupby(
                dimension_columns,
                as_index=False
            )
            .agg(
                premium_transactions=(
                    "transaction_id",
                    "nunique"
                ),
                paid_transactions=(
                    "paid_transaction",
                    "sum"
                ),
                failed_transactions=(
                    "failed_transaction",
                    "sum"
                ),
                partial_transactions=(
                    "partial_transaction",
                    "sum"
                ),
                total_premium_due=(
                    "premium_due",
                    "sum"
                ),
                total_premium_collected=(
                    "premium_paid",
                    "sum"
                ),
            )
        )

        premium_performance_df["outstanding_premium"] = (
            premium_performance_df["total_premium_due"]
            - premium_performance_df[
                "total_premium_collected"
            ]
        )

        premium_performance_df["collection_rate_pct"] = (
            premium_performance_df[
                "total_premium_collected"
            ]
            .div(
                premium_performance_df[
                    "total_premium_due"
                ].replace(0, pd.NA)
            )
            .mul(100)
            .fillna(0)
        )

        monetary_columns = [
            "total_premium_due",
            "total_premium_collected",
            "outstanding_premium",
        ]

        premium_performance_df[monetary_columns] = (
            premium_performance_df[monetary_columns]
            .round(2)
        )

        premium_performance_df[
            "collection_rate_pct"
        ] = (
            premium_performance_df[
                "collection_rate_pct"
            ]
            .round(2)
        )

        premium_performance_df = (
            premium_performance_df[
                gold_columns
            ]
            .sort_values(
                by=dimension_columns
            )
            .reset_index(drop=True)
        )

    # =========================================================================
    # CREATE OUTPUT DIRECTORIES
    # =========================================================================

    GOLD_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    REJECT_OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # =========================================================================
    # SAVE OUTPUTS
    # =========================================================================

    premium_performance_df.to_csv(
        GOLD_OUTPUT_FILE,
        index=False
    )

    rejects_df.to_csv(
        REJECT_OUTPUT_FILE,
        index=False
    )

    # =========================================================================
    # RECONCILIATION
    # =========================================================================

    valid_premium_due = round(
        valid_premium_df["premium_due"].sum(),
        2
    )

    gold_premium_due = round(
        premium_performance_df[
            "total_premium_due"
        ].sum(),
        2
    )

    valid_premium_collected = round(
        valid_premium_df["premium_paid"].sum(),
        2
    )

    gold_premium_collected = round(
        premium_performance_df[
            "total_premium_collected"
        ].sum(),
        2
    )

    if (
        valid_premium_due != gold_premium_due
        or valid_premium_collected
        != gold_premium_collected
    ):
        raise ValueError(
            "Silver-to-Gold financial reconciliation failed."
        )

    if (
        len(valid_premium_df) + len(rejects_df)
        != len(premiums_df)
    ):
        raise ValueError(
            "Record reconciliation failed."
        )

    # =========================================================================
    # DISPLAY RESULTS
    # =========================================================================

    overall_collection_rate = (
        (
            valid_premium_collected
            / valid_premium_due
        )
        * 100
        if valid_premium_due > 0
        else 0
    )

    print()
    print("RECORD PROCESSING")
    print("-" * 75)

    print(
        f"Source Premium Records   : "
        f"{len(premiums_df):,}"
    )

    print(
        f"Valid Premium Records    : "
        f"{len(valid_premium_df):,}"
    )

    print(
        f"Rejected Premium Records : "
        f"{len(rejects_df):,}"
    )

    print(
        f"Gold Rows                : "
        f"{len(premium_performance_df):,}"
    )

    print()
    print("PREMIUM PERFORMANCE")
    print("-" * 75)

    print(
        f"Total Premium Due        : "
        f"R {valid_premium_due:,.2f}"
    )

    print(
        f"Total Premium Collected  : "
        f"R {valid_premium_collected:,.2f}"
    )

    print(
        f"Overall Collection Rate  : "
        f"{overall_collection_rate:.2f}%"
    )

    print()
    print("OUTPUT FILES")
    print("-" * 75)

    print(
        f"Gold output   : "
        f"{GOLD_OUTPUT_FILE}"
    )

    print(
        f"Reject output : "
        f"{REJECT_OUTPUT_FILE}"
    )

    print()
    print("Reconciliation checks passed.")
    print(
        "Premium performance by dimension "
        "completed successfully."
    )

    print("=" * 75)


# =============================================================================
# RUN SCRIPT
# =============================================================================

if __name__ == "__main__":
    main()