"""
claim_performance_dimension.py

Purpose:
Create a Gold-layer claims performance dataset supporting analysis by:

- Month
- Partner
- Product
- Product Type
- Province

Gold output:
Data/Gold/claims_performance_by_dimension.csv

Reject output:
Data/Rejects/claim_performance_dimension_rejects.csv

Expected claim_outcome values:
- Paid
- Declined
- Under Investigation

Expected claim_date format:
- YYYY-MM-DD
"""

from pathlib import Path

import pandas as pd


# =============================================================================
# FILE PATHS
# =============================================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CLAIMS_FILE = (
    BASE_DIR
    / "Data"
    / "Silver"
    / "claims_clean.csv"
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
    / "claims_performance_by_dimension.csv"
)

REJECT_OUTPUT_FILE = (
    BASE_DIR
    / "Data"
    / "Rejects"
    / "claim_performance_dimension_rejects.csv"
)


# =============================================================================
# EXPECTED VALUES FROM DATA DICTIONARY
# =============================================================================

EXPECTED_CLAIM_OUTCOMES = {
    "Paid",
    "Declined",
    "Under Investigation",
}


# =============================================================================
# REQUIRED COLUMNS
# =============================================================================

CLAIMS_REQUIRED_COLUMNS = [
    "claim_id",
    "policy_id",
    "claim_date",
    "claim_type",
    "claim_amount",
    "claim_outcome",
    "paid_amount",
]

POLICIES_REQUIRED_COLUMNS = [
    "policy_id",
    "partner_id",
    "product_id",
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


def clean_text_columns(dataframe, columns):
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
    Create a reason explaining why a claim record was rejected.
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
    print("CLAIMS PERFORMANCE BY DIMENSION")
    print("=" * 75)

    # =========================================================================
    # LOAD SILVER DATA
    # =========================================================================

    claims_df = load_csv(
        CLAIMS_FILE,
        "Claims"
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
        claims_df,
        CLAIMS_REQUIRED_COLUMNS,
        "Claims"
    )

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
        claims_df,
        [
            "claim_id",
            "policy_id",
            "claim_type",
            "claim_outcome",
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
    # PREPARE CLAIM DATES
    # =========================================================================

    claims_df["claim_date"] = pd.to_datetime(
        claims_df["claim_date"],
        format="%Y-%m-%d",
        errors="coerce"
    )

    invalid_date_count = (
        claims_df["claim_date"]
        .isna()
        .sum()
    )

    if invalid_date_count > 0:
        raise ValueError(
            f"{invalid_date_count:,} invalid claim_date value(s). "
            f"Expected format: YYYY-MM-DD."
        )

    # Convert claim dates into a common monthly reporting key.
    # Example: 2026-06-17 becomes 2026-06-01.

    claims_df["month"] = (
        claims_df["claim_date"]
        .dt.to_period("M")
        .dt.to_timestamp()
        .dt.strftime("%Y-%m-01")
    )

    # =========================================================================
    # PREPARE NUMERIC COLUMNS
    # =========================================================================

    claims_df["claim_amount"] = pd.to_numeric(
        claims_df["claim_amount"],
        errors="coerce"
    )

    claims_df["paid_amount"] = pd.to_numeric(
        claims_df["paid_amount"],
        errors="coerce"
    )

    invalid_claim_amount_count = (
        claims_df["claim_amount"]
        .isna()
        .sum()
    )

    invalid_paid_amount_count = (
        claims_df["paid_amount"]
        .isna()
        .sum()
    )

    if invalid_claim_amount_count > 0:
        raise ValueError(
            f"{invalid_claim_amount_count:,} invalid claim_amount "
            f"value(s). Expected a decimal value."
        )

    if invalid_paid_amount_count > 0:
        raise ValueError(
            f"{invalid_paid_amount_count:,} invalid paid_amount "
            f"value(s). Expected a decimal value."
        )

    # =========================================================================
    # VALIDATE CLAIM OUTCOMES
    # =========================================================================

    actual_claim_outcomes = set(
        claims_df["claim_outcome"]
        .dropna()
        .unique()
    )

    invalid_claim_outcomes = sorted(
        actual_claim_outcomes
        - EXPECTED_CLAIM_OUTCOMES
    )

    if invalid_claim_outcomes:
        raise ValueError(
            "Undocumented claim_outcome values found: "
            f"{invalid_claim_outcomes}. Expected values are "
            "'Paid', 'Declined', and 'Under Investigation'."
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
    # JOIN CLAIMS TO POLICIES
    # =========================================================================

    claim_detail_df = claims_df.merge(
        policy_lookup,
        on="policy_id",
        how="left",
        validate="many_to_one",
        indicator="policy_join"
    )

    # =========================================================================
    # JOIN TO PARTNERS
    # =========================================================================

    claim_detail_df = claim_detail_df.merge(
        partner_lookup,
        on="partner_id",
        how="left",
        validate="many_to_one",
        indicator="partner_join"
    )

    # =========================================================================
    # JOIN TO PRODUCTS
    # =========================================================================

    claim_detail_df = claim_detail_df.merge(
        product_lookup,
        on="product_id",
        how="left",
        validate="many_to_one",
        indicator="product_join"
    )

    # =========================================================================
    # IDENTIFY REJECTED RECORDS
    # =========================================================================

    claim_detail_df["rejection_reason"] = (
        claim_detail_df.apply(
            create_rejection_reason,
            axis=1
        )
    )

    rejection_mask = (
        claim_detail_df["rejection_reason"] != ""
    )

    reject_columns = [
        "claim_id",
        "policy_id",
        "claim_date",
        "claim_type",
        "claim_amount",
        "claim_outcome",
        "paid_amount",
        "partner_id",
        "partner_name",
        "product_id",
        "product_name",
        "product_type",
        "province",
        "rejection_reason",
    ]

    rejects_df = claim_detail_df.loc[
        rejection_mask,
        reject_columns
    ].copy()

    if not rejects_df.empty:
        rejects_df["claim_date"] = (
            rejects_df["claim_date"]
            .dt.strftime("%Y-%m-%d")
        )

    # =========================================================================
    # KEEP VALID RECORDS
    # =========================================================================

    valid_claims_df = claim_detail_df.loc[
        ~rejection_mask
    ].copy()

    # =========================================================================
    # CREATE CLAIM OUTCOME INDICATORS
    # =========================================================================

    valid_claims_df["paid_claim"] = (
        valid_claims_df["claim_outcome"] == "Paid"
    ).astype(int)

    valid_claims_df["declined_claim"] = (
        valid_claims_df["claim_outcome"] == "Declined"
    ).astype(int)

    valid_claims_df["under_investigation_claim"] = (
        valid_claims_df["claim_outcome"]
        == "Under Investigation"
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
        "number_of_claims",
        "paid_claims",
        "declined_claims",
        "under_investigation_claims",
        "total_claim_amount",
        "claims_paid_amount",
        "average_claim_amount",
        "claim_approval_rate_pct",
        "claim_payout_rate_pct",
    ]

    # =========================================================================
    # CREATE GOLD DATASET
    # =========================================================================

    if valid_claims_df.empty:

        claims_performance_df = pd.DataFrame(
            columns=gold_columns
        )

    else:

        claims_performance_df = (
            valid_claims_df
            .groupby(
                dimension_columns,
                as_index=False,
                dropna=False
            )
            .agg(
                number_of_claims=(
                    "claim_id",
                    "nunique"
                ),
                paid_claims=(
                    "paid_claim",
                    "sum"
                ),
                declined_claims=(
                    "declined_claim",
                    "sum"
                ),
                under_investigation_claims=(
                    "under_investigation_claim",
                    "sum"
                ),
                total_claim_amount=(
                    "claim_amount",
                    "sum"
                ),
                claims_paid_amount=(
                    "paid_amount",
                    "sum"
                ),
                average_claim_amount=(
                    "claim_amount",
                    "mean"
                ),
            )
        )

        # =====================================================================
        # CALCULATE CLAIM APPROVAL RATE
        # =====================================================================

        claims_performance_df[
            "claim_approval_rate_pct"
        ] = 0.0

        positive_claim_count_mask = (
            claims_performance_df["number_of_claims"] > 0
        )

        claims_performance_df.loc[
            positive_claim_count_mask,
            "claim_approval_rate_pct"
        ] = (
            claims_performance_df.loc[
                positive_claim_count_mask,
                "paid_claims"
            ]
            / claims_performance_df.loc[
                positive_claim_count_mask,
                "number_of_claims"
            ]
            * 100
        )

        # =====================================================================
        # CALCULATE CLAIM PAYOUT RATE
        # =====================================================================

        claims_performance_df[
            "claim_payout_rate_pct"
        ] = 0.0

        positive_claim_amount_mask = (
            claims_performance_df["total_claim_amount"] > 0
        )

        claims_performance_df.loc[
            positive_claim_amount_mask,
            "claim_payout_rate_pct"
        ] = (
            claims_performance_df.loc[
                positive_claim_amount_mask,
                "claims_paid_amount"
            ]
            / claims_performance_df.loc[
                positive_claim_amount_mask,
                "total_claim_amount"
            ]
            * 100
        )

        # =====================================================================
        # ROUND OUTPUT VALUES
        # =====================================================================

        monetary_columns = [
            "total_claim_amount",
            "claims_paid_amount",
            "average_claim_amount",
        ]

        claims_performance_df[monetary_columns] = (
            claims_performance_df[monetary_columns]
            .round(2)
        )

        percentage_columns = [
            "claim_approval_rate_pct",
            "claim_payout_rate_pct",
        ]

        claims_performance_df[percentage_columns] = (
            claims_performance_df[percentage_columns]
            .round(2)
        )

        # =====================================================================
        # SET FINAL COLUMN ORDER
        # =====================================================================

        claims_performance_df = (
            claims_performance_df[gold_columns]
            .sort_values(
                by=dimension_columns
            )
            .reset_index(drop=True)
        )

    # =========================================================================
    # RECONCILIATION VALUES
    # =========================================================================

    source_record_count = len(claims_df)
    valid_record_count = len(valid_claims_df)
    rejected_record_count = len(rejects_df)

    valid_claim_count = int(
        valid_claims_df["claim_id"].nunique()
    )

    gold_claim_count = int(
        claims_performance_df[
            "number_of_claims"
        ].sum()
    )

    valid_claim_amount = round(
        valid_claims_df["claim_amount"].sum(),
        2
    )

    gold_claim_amount = round(
        claims_performance_df[
            "total_claim_amount"
        ].sum(),
        2
    )

    valid_paid_amount = round(
        valid_claims_df["paid_amount"].sum(),
        2
    )

    gold_paid_amount = round(
        claims_performance_df[
            "claims_paid_amount"
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

    if valid_claim_count != gold_claim_count:
        raise ValueError(
            "Claim count reconciliation failed. "
            f"Valid Silver claims: {valid_claim_count:,}. "
            f"Gold claims: {gold_claim_count:,}."
        )

    if valid_claim_amount != gold_claim_amount:
        raise ValueError(
            "Claim amount reconciliation failed. "
            f"Valid Silver amount: R {valid_claim_amount:,.2f}. "
            f"Gold amount: R {gold_claim_amount:,.2f}."
        )

    if valid_paid_amount != gold_paid_amount:
        raise ValueError(
            "Paid amount reconciliation failed. "
            f"Valid Silver amount: R {valid_paid_amount:,.2f}. "
            f"Gold amount: R {gold_paid_amount:,.2f}."
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

    claims_performance_df.to_csv(
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

    total_paid_claims = int(
        valid_claims_df["paid_claim"].sum()
    )

    total_declined_claims = int(
        valid_claims_df["declined_claim"].sum()
    )

    total_under_investigation_claims = int(
        valid_claims_df[
            "under_investigation_claim"
        ].sum()
    )

    average_claim_amount = (
        valid_claim_amount
        / valid_claim_count
        if valid_claim_count > 0
        else 0
    )

    overall_approval_rate = (
        total_paid_claims
        / valid_claim_count
        * 100
        if valid_claim_count > 0
        else 0
    )

    overall_payout_rate = (
        valid_paid_amount
        / valid_claim_amount
        * 100
        if valid_claim_amount > 0
        else 0
    )

    # =========================================================================
    # DISPLAY RESULTS
    # =========================================================================

    print()
    print("RECORD PROCESSING")
    print("-" * 75)

    print(
        f"Source Claim Records       : "
        f"{source_record_count:,}"
    )

    print(
        f"Valid Claim Records        : "
        f"{valid_record_count:,}"
    )

    print(
        f"Rejected Claim Records     : "
        f"{rejected_record_count:,}"
    )

    print(
        f"Gold Rows                  : "
        f"{len(claims_performance_df):,}"
    )

    print()
    print("CLAIMS PERFORMANCE")
    print("-" * 75)

    print(
        f"Number of Claims           : "
        f"{valid_claim_count:,}"
    )

    print(
        f"Paid Claims                : "
        f"{total_paid_claims:,}"
    )

    print(
        f"Declined Claims            : "
        f"{total_declined_claims:,}"
    )

    print(
        f"Under Investigation Claims: "
        f"{total_under_investigation_claims:,}"
    )

    print(
        f"Total Claim Amount         : "
        f"R {valid_claim_amount:,.2f}"
    )

    print(
        f"Claims Paid Amount         : "
        f"R {valid_paid_amount:,.2f}"
    )

    print(
        f"Average Claim Amount       : "
        f"R {average_claim_amount:,.2f}"
    )

    print(
        f"Overall Approval Rate      : "
        f"{overall_approval_rate:.2f}%"
    )

    print(
        f"Overall Payout Rate        : "
        f"{overall_payout_rate:.2f}%"
    )

    print()
    print("RECONCILIATION")
    print("-" * 75)

    print("Record reconciliation      : Passed")
    print("Claim count reconciliation : Passed")
    print("Claim amount reconciliation: Passed")
    print("Paid amount reconciliation : Passed")

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
        "Claims performance by dimension "
        "completed successfully."
    )

    print("=" * 75)


# =============================================================================
# RUN SCRIPT
# =============================================================================

if __name__ == "__main__":
    main()