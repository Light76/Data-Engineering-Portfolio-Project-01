"""
policy_performance_dimension.py

Purpose:
Create a Gold-layer policy performance dataset supporting analysis by:

- Month, based on inception_date
- Partner
- Product
- Product Type
- Province

Gold output:
Data/Gold/policy_performance_by_dimension.csv

Reject output:
Data/Rejects/policy_performance_dimension_rejects.csv

Expected policy_status values:
- Active
- Lapsed
- Cancelled

Expected inception_date format:
- YYYY-MM-DD
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

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
    / "policy_performance_by_dimension.csv"
)

REJECT_OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "Rejects"
    / "policy_performance_dimension_rejects.csv"
)


# =============================================================================
# EXPECTED VALUES FROM DATA DICTIONARY
# =============================================================================

EXPECTED_POLICY_STATUSES = {
    "Active",
    "Lapsed",
    "Cancelled",
}


# =============================================================================
# REQUIRED COLUMNS
# =============================================================================

POLICIES_REQUIRED_COLUMNS = [
    "policy_id",
    "partner_id",
    "product_id",
    "inception_date",
    "cover_amount",
    "monthly_premium",
    "policy_status",
    "province",
]

PARTNERS_REQUIRED_COLUMNS = [
    "partner_id",
    "partner_name",
]

PRODUCTS_REQUIRED_COLUMNS = [
    "product_id",
    "product_name",
    "product_type",
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_csv(file_path, dataset_name):
    """
    Load a CSV file and display the number of records loaded.
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
    Confirm that all required columns exist.
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
    Confirm that a lookup key is unique before joining.
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
            f"value(s) in '{key_column}'. Duplicate lookup keys could "
            f"inflate Gold totals."
        )


def create_rejection_reason(row):
    """
    Create a reason explaining why a policy was rejected.
    """

    reasons = []

    if (
        pd.isna(row["partner_id"])
        or str(row["partner_id"]).strip() == ""
    ):
        reasons.append(
            "policy has missing partner_id"
        )

    elif row["partner_join"] == "left_only":
        reasons.append(
            "partner_id not found in partners_clean.csv"
        )

    if (
        pd.isna(row["product_id"])
        or str(row["product_id"]).strip() == ""
    ):
        reasons.append(
            "policy has missing product_id"
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
            "policy has missing province"
        )

    return "; ".join(reasons)


# =============================================================================
# MAIN PROCESS
# =============================================================================

def main():

    print("=" * 75)
    print("POLICY PERFORMANCE BY DIMENSION")
    print("=" * 75)

    # =========================================================================
    # LOAD SILVER DATA
    # =========================================================================

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
        policies_df,
        POLICIES_REQUIRED_COLUMNS,
        "Policies"
    )

    validate_required_columns(
        partners_df,
        PARTNERS_REQUIRED_COLUMNS,
        "Partners"
    )

    validate_required_columns(
        products_df,
        PRODUCTS_REQUIRED_COLUMNS,
        "Products"
    )

    # =========================================================================
    # CLEAN TEXT COLUMNS
    # =========================================================================

    clean_text_columns(
        policies_df,
        [
            "policy_id",
            "partner_id",
            "product_id",
            "policy_status",
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
    # PREPARE INCEPTION DATE
    # =========================================================================

    policies_df["inception_date"] = pd.to_datetime(
        policies_df["inception_date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    invalid_date_count = (
        policies_df["inception_date"]
        .isna()
        .sum()
    )

    if invalid_date_count > 0:
        raise ValueError(
            f"{invalid_date_count:,} invalid inception_date "
            f"value(s). Expected format: YYYY-MM-DD."
        )

    # Convert inception_date to a monthly reporting key.
    # Example: 2026-06-15 becomes 2026-06-01.

    policies_df["month"] = (
        policies_df["inception_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
        .dt.strftime("%Y-%m-01")
    )

    # =========================================================================
    # PREPARE NUMERIC COLUMNS
    # =========================================================================

    policies_df["cover_amount"] = pd.to_numeric(
        policies_df["cover_amount"],
        errors="coerce"
    )

    policies_df["monthly_premium"] = pd.to_numeric(
        policies_df["monthly_premium"],
        errors="coerce"
    )

    invalid_cover_count = (
        policies_df["cover_amount"]
        .isna()
        .sum()
    )

    invalid_premium_count = (
        policies_df["monthly_premium"]
        .isna()
        .sum()
    )

    if invalid_cover_count > 0:
        raise ValueError(
            f"{invalid_cover_count:,} invalid cover_amount "
            f"value(s). Expected Decimal."
        )

    if invalid_premium_count > 0:
        raise ValueError(
            f"{invalid_premium_count:,} invalid monthly_premium "
            f"value(s). Expected Decimal."
        )

    # =========================================================================
    # VALIDATE POLICY STATUS
    # =========================================================================

    actual_policy_statuses = set(
        policies_df["policy_status"]
        .dropna()
        .unique()
    )

    invalid_policy_statuses = sorted(
        actual_policy_statuses
        - EXPECTED_POLICY_STATUSES
    )

    if invalid_policy_statuses:
        raise ValueError(
            "Undocumented policy_status values found: "
            f"{invalid_policy_statuses}. Expected values are "
            "'Active', 'Lapsed', and 'Cancelled'."
        )

    # =========================================================================
    # PREPARE LOOKUP TABLES
    # =========================================================================

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
    # JOIN POLICIES TO PARTNERS
    # =========================================================================

    policy_detail_df = policies_df.merge(
        partner_lookup,
        on="partner_id",
        how="left",
        validate="many_to_one",
        indicator="partner_join"
    )

    # =========================================================================
    # JOIN POLICIES TO PRODUCTS
    # =========================================================================

    policy_detail_df = policy_detail_df.merge(
        product_lookup,
        on="product_id",
        how="left",
        validate="many_to_one",
        indicator="product_join"
    )

    # =========================================================================
    # IDENTIFY REJECTED POLICIES
    # =========================================================================

    policy_detail_df["rejection_reason"] = (
        policy_detail_df.apply(
            create_rejection_reason,
            axis=1
        )
    )

    rejection_mask = (
        policy_detail_df["rejection_reason"] != ""
    )

    reject_columns = [
        "policy_id",
        "partner_id",
        "partner_name",
        "product_id",
        "product_name",
        "product_type",
        "inception_date",
        "province",
        "cover_amount",
        "monthly_premium",
        "policy_status",
        "rejection_reason",
    ]

    rejects_df = policy_detail_df.loc[
        rejection_mask,
        reject_columns
    ].copy()

    if not rejects_df.empty:
        rejects_df["inception_date"] = (
            rejects_df["inception_date"]
            .dt.strftime("%Y-%m-%d")
        )

    # =========================================================================
    # KEEP VALID POLICIES
    # =========================================================================

    valid_policies_df = policy_detail_df.loc[
        ~rejection_mask
    ].copy()

    # =========================================================================
    # CREATE POLICY STATUS INDICATORS
    # =========================================================================

    valid_policies_df["active_policy"] = (
        valid_policies_df["policy_status"] == "Active"
    ).astype(int)

    valid_policies_df["lapsed_policy"] = (
        valid_policies_df["policy_status"] == "Lapsed"
    ).astype(int)

    valid_policies_df["cancelled_policy"] = (
        valid_policies_df["policy_status"] == "Cancelled"
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
        "total_policies",
        "active_policies",
        "lapsed_policies",
        "cancelled_policies",
        "total_cover_amount",
        "average_cover_amount",
        "total_monthly_premium",
        "average_monthly_premium",
        "active_policy_pct",
        "lapsed_policy_pct",
        "cancelled_policy_pct",
    ]

    # =========================================================================
    # CREATE GOLD DATASET
    # =========================================================================

    if valid_policies_df.empty:

        policy_performance_df = pd.DataFrame(
            columns=gold_columns
        )

    else:

        policy_performance_df = (
            valid_policies_df
            .groupby(
                dimension_columns,
                as_index=False,
                dropna=False
            )
            .agg(
                total_policies=(
                    "policy_id",
                    "nunique"
                ),
                active_policies=(
                    "active_policy",
                    "sum"
                ),
                lapsed_policies=(
                    "lapsed_policy",
                    "sum"
                ),
                cancelled_policies=(
                    "cancelled_policy",
                    "sum"
                ),
                total_cover_amount=(
                    "cover_amount",
                    "sum"
                ),
                average_cover_amount=(
                    "cover_amount",
                    "mean"
                ),
                total_monthly_premium=(
                    "monthly_premium",
                    "sum"
                ),
                average_monthly_premium=(
                    "monthly_premium",
                    "mean"
                ),
            )
        )

        # =====================================================================
        # CALCULATE POLICY STATUS PERCENTAGES
        # =====================================================================

        policy_count_denominator = (
            policy_performance_df[
                "total_policies"
            ]
            .replace(0, pd.NA)
        )

        policy_performance_df["active_policy_pct"] = (
            policy_performance_df["active_policies"]
            .div(policy_count_denominator)
            .mul(100)
            .fillna(0)
        )

        policy_performance_df["lapsed_policy_pct"] = (
            policy_performance_df["lapsed_policies"]
            .div(policy_count_denominator)
            .mul(100)
            .fillna(0)
        )

        policy_performance_df["cancelled_policy_pct"] = (
            policy_performance_df["cancelled_policies"]
            .div(policy_count_denominator)
            .mul(100)
            .fillna(0)
        )

        # =====================================================================
        # ROUND OUTPUT VALUES
        # =====================================================================

        monetary_columns = [
            "total_cover_amount",
            "average_cover_amount",
            "total_monthly_premium",
            "average_monthly_premium",
        ]

        percentage_columns = [
            "active_policy_pct",
            "lapsed_policy_pct",
            "cancelled_policy_pct",
        ]

        policy_performance_df[monetary_columns] = (
            policy_performance_df[monetary_columns]
            .round(2)
        )

        policy_performance_df[percentage_columns] = (
            policy_performance_df[percentage_columns]
            .round(2)
        )

        # =====================================================================
        # SET FINAL COLUMN ORDER AND SORT
        # =====================================================================

        policy_performance_df = (
            policy_performance_df[gold_columns]
            .sort_values(
                by=dimension_columns
            )
            .reset_index(drop=True)
        )

    # =========================================================================
    # RECONCILIATION VALUES
    # =========================================================================

    source_record_count = len(policies_df)
    valid_record_count = len(valid_policies_df)
    rejected_record_count = len(rejects_df)

    valid_policy_count = int(
        valid_policies_df["policy_id"].nunique()
    )

    gold_policy_count = int(
        policy_performance_df[
            "total_policies"
        ].sum()
    )

    valid_cover_total = round(
        valid_policies_df["cover_amount"].sum(),
        2
    )

    gold_cover_total = round(
        policy_performance_df[
            "total_cover_amount"
        ].sum(),
        2
    )

    valid_monthly_premium_total = round(
        valid_policies_df["monthly_premium"].sum(),
        2
    )

    gold_monthly_premium_total = round(
        policy_performance_df[
            "total_monthly_premium"
        ].sum(),
        2
    )

    # =========================================================================
    # RUN RECONCILIATION CHECKS
    # =========================================================================

    if (
        valid_record_count + rejected_record_count
        != source_record_count
    ):
        raise ValueError(
            "Record reconciliation failed. "
            f"Source records: {source_record_count:,}. "
            f"Valid records: {valid_record_count:,}. "
            f"Rejected records: {rejected_record_count:,}."
        )

    if valid_policy_count != gold_policy_count:
        raise ValueError(
            "Policy count reconciliation failed. "
            f"Valid Silver policies: {valid_policy_count:,}. "
            f"Gold policies: {gold_policy_count:,}."
        )

    if valid_cover_total != gold_cover_total:
        raise ValueError(
            "Cover amount reconciliation failed. "
            f"Valid Silver amount: R {valid_cover_total:,.2f}. "
            f"Gold amount: R {gold_cover_total:,.2f}."
        )

    if (
        valid_monthly_premium_total
        != gold_monthly_premium_total
    ):
        raise ValueError(
            "Monthly premium reconciliation failed. "
            f"Valid Silver amount: "
            f"R {valid_monthly_premium_total:,.2f}. "
            f"Gold amount: "
            f"R {gold_monthly_premium_total:,.2f}."
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
    # SAVE OUTPUT FILES
    # =========================================================================

    policy_performance_df.to_csv(
        GOLD_OUTPUT_FILE,
        index=False
    )

    rejects_df.to_csv(
        REJECT_OUTPUT_FILE,
        index=False
    )

    # =========================================================================
    # CALCULATE OVERALL METRICS
    # =========================================================================

    total_active_policies = int(
        valid_policies_df["active_policy"].sum()
    )

    total_lapsed_policies = int(
        valid_policies_df["lapsed_policy"].sum()
    )

    total_cancelled_policies = int(
        valid_policies_df["cancelled_policy"].sum()
    )

    average_cover_amount = (
        valid_cover_total
        / valid_policy_count
        if valid_policy_count > 0
        else 0
    )

    average_monthly_premium = (
        valid_monthly_premium_total
        / valid_policy_count
        if valid_policy_count > 0
        else 0
    )

    active_policy_pct = (
        total_active_policies
        / valid_policy_count
        * 100
        if valid_policy_count > 0
        else 0
    )

    lapsed_policy_pct = (
        total_lapsed_policies
        / valid_policy_count
        * 100
        if valid_policy_count > 0
        else 0
    )

    cancelled_policy_pct = (
        total_cancelled_policies
        / valid_policy_count
        * 100
        if valid_policy_count > 0
        else 0
    )

    # =========================================================================
    # DISPLAY RESULTS
    # =========================================================================

    print()
    print("RECORD PROCESSING")
    print("-" * 75)

    print(
        f"Source Policy Records      : "
        f"{source_record_count:,}"
    )

    print(
        f"Valid Policy Records       : "
        f"{valid_record_count:,}"
    )

    print(
        f"Rejected Policy Records    : "
        f"{rejected_record_count:,}"
    )

    print(
        f"Gold Rows                  : "
        f"{len(policy_performance_df):,}"
    )

    print()
    print("POLICY PERFORMANCE")
    print("-" * 75)

    print(
        f"Total Policies             : "
        f"{valid_policy_count:,}"
    )

    print(
        f"Active Policies            : "
        f"{total_active_policies:,} "
        f"({active_policy_pct:.2f}%)"
    )

    print(
        f"Lapsed Policies            : "
        f"{total_lapsed_policies:,} "
        f"({lapsed_policy_pct:.2f}%)"
    )

    print(
        f"Cancelled Policies         : "
        f"{total_cancelled_policies:,} "
        f"({cancelled_policy_pct:.2f}%)"
    )

    print(
        f"Total Cover Amount         : "
        f"R {valid_cover_total:,.2f}"
    )

    print(
        f"Average Cover Amount       : "
        f"R {average_cover_amount:,.2f}"
    )

    print(
        f"Total Monthly Premium      : "
        f"R {valid_monthly_premium_total:,.2f}"
    )

    print(
        f"Average Monthly Premium    : "
        f"R {average_monthly_premium:,.2f}"
    )

    print()
    print("RECONCILIATION")
    print("-" * 75)

    print("Record reconciliation      : Passed")
    print("Policy count reconciliation: Passed")
    print("Cover amount reconciliation: Passed")
    print("Premium reconciliation     : Passed")

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
    print(
        "Policy performance by dimension "
        "completed successfully."
    )

    print("=" * 75)


# =============================================================================
# RUN SCRIPT
# =============================================================================

if __name__ == "__main__":
    main()