import pandas as pd
from pathlib import Path
from datetime import datetime

LOG_PATH = Path("Logs/data_quality_log.csv")


def check_nulls(df, required_columns):
    """
    Check mandatory columns for null values.
    """

    issues = []

    for column in required_columns:

        if column in df.columns:

            null_count = df[column].isnull().sum()

            if null_count > 0:

                issues.append(
                    {
                        "check_type": "NULL_CHECK",
                        "column": column,
                        "issue_count": int(null_count),
                    }
                )

    return issues


def check_duplicates(df, key_column):
    """
    Check duplicate primary keys.
    """

    duplicated_count = df[key_column].duplicated().sum()

    if duplicated_count > 0:

        return [{
            "check_type": "DUPLICATE_CHECK",
            "column": key_column,
            "issue_count": int(duplicated_count)
        }]

    return []


def check_allowed_values(df, column, allowed_values):
    """
    Validate lookup values.
    """

    invalid_values = ~df[column].isin(allowed_values)

    invalid_count = invalid_values.sum()

    if invalid_count > 0:

        return [{
            "check_type": "ALLOWED_VALUES_CHECK",
            "column": column,
            "issue_count": int(invalid_count)
        }]

    return []


def check_positive_values(df, column):
    """
    Validate numeric values greater than zero.
    """

    invalid_count = (df[column] < 0).sum()

    if invalid_count > 0:

        return [{
            "check_type": "POSITIVE_VALUE_CHECK",
            "column": column,
            "issue_count": int(invalid_count)
        }]

    return []

# ==================================================
# Check date format
# ==================================================

def check_date_format(df, column, expected_format="%Y-%m-%d"):

    if column not in df.columns:
        return [{
            "check_type": "MISSING_COLUMN_CHECK",
            "column": column,
            "issue_count": 1
        }]

    populated_values = df[column].dropna()

    converted_dates = pd.to_datetime(
        populated_values,
        format=expected_format,
        errors="coerce"
    )

    invalid_count = int(converted_dates.isna().sum())

    if invalid_count > 0:
        return [{
            "check_type": "DATE_FORMAT_CHECK",
            "column": column,
            "issue_count": invalid_count
        }]

    return []

def calculate_quality_score(
        total_rows,
        duplicate_count,
        null_count,
        invalid_count
):
    """
    Calculate a basic quality score.
    """

    total_issues = (
        duplicate_count
        + null_count
        + invalid_count
    )

    score = (
        (total_rows - total_issues)
        / total_rows
    ) * 100

    return round(max(score, 0), 2)


# ==================================================
# DATA QUALITY RULES CONFIGURATION
# ==================================================

DQ_RULES = {

    "claims.csv": {

        "primary_key": "claim_id",

        "required_columns": [
            "claim_id",
            "policy_id",
            "claim_date",
            "claim_type",
            "claim_amount",
            "claim_outcome",
            "paid_amount"
        ],

        "allowed_values": {
            "claim_type": [
                "Death",
                "Disability",
                "Retrenchment"
            ],

            "claim_outcome": [
                "Paid",
                "Declined",
                "Under Investigation"
            ]
        },

        "positive_value_columns": [
            "claim_amount",
            "paid_amount"
        ],

        "date_columns": [
            "claim_date"
        ]
    },

    "partners.csv": {

        "primary_key": "partner_id",

        "required_columns": [
            "partner_id",
            "partner_name",
            "partner_type",
            "province",
            "onboard_date",
            "status"
        ],

        "allowed_values": {
            "status": [
                "Active",
                "Inactive"
            ]
        },

        "positive_value_columns": [],

        "date_columns": [
            "onboard_date"
        ]
    },

    "policies.csv": {

        "primary_key": "policy_id",

        "required_columns": [
            "policy_id",
            "partner_id",
            "product_id",
            "inception_date",
            "date_of_birth",
            "gender",
            "province",
            "cover_amount",
            "monthly_premium",
            "policy_status"
        ],

        "allowed_values": {
            "gender": [
                "F",
                "M"
            ],

            "policy_status": [
                "Active",
                "Lapsed",
                "Cancelled"
            ]
        },

        "positive_value_columns": [
            "cover_amount",
            "monthly_premium"
        ],

        "date_columns": [
            "inception_date",
            "date_of_birth",
            "termination_date"
        ]
    },

    "premiums.csv": {

        "primary_key": "transaction_id",

        "required_columns": [
            "transaction_id",
            "policy_id",
            "premium_month",
            "premium_due",
            "premium_paid",
            "payment_status"
        ],

        "allowed_values": {
            "payment_status": [
                "Paid",
                "Failed",
                "Partial"
            ]
        },

        "positive_value_columns": [
            "premium_due",
            "premium_paid"
        ],

        "date_columns": [
            "premium_month",
            "payment_date"
        ]
    },

    "products.csv": {

        "primary_key": "product_id",

        "required_columns": [
            "product_id",
            "product_name",
            "product_type",
            "max_cover",
            "rate_or_base_premium",
            "partner_id"
        ],

        "allowed_values": {
            "product_type": [
                "Credit Life",
                "Funeral",
                "Disability"
            ]
        },

        "positive_value_columns": [
            "max_cover",
            "rate_or_base_premium"
        ],

        "date_columns": []
    }
}

# ==================================================
# Run data quality check function
# ==================================================

def run_data_quality_checks(df, file_name):

    results = []

    rules = DQ_RULES[file_name]

    # ------------------------------------------------
    # NULL CHECKS
    # ------------------------------------------------

    results.extend(
        check_nulls(
            df,
            rules["required_columns"]
        )
    )

    # ------------------------------------------------
    # DUPLICATE CHECKS
    # ------------------------------------------------

    results.extend(
        check_duplicates(
            df,
            rules["primary_key"]
        )
    )

    # ------------------------------------------------
    # ALLOWED VALUES CHECKS
    # ------------------------------------------------

    for column, values in rules["allowed_values"].items():

        results.extend(
            check_allowed_values(
                df,
                column,
                values
            )
        )

    # ------------------------------------------------
    # POSITIVE VALUE CHECKS
    # ------------------------------------------------

    for column in rules["positive_value_columns"]:

        results.extend(
            check_positive_values(
                df,
                column
            )
        )

    # ------------------------------------------------
    # DATE FORMAT CHECKS
    # ------------------------------------------------

    for column in rules["date_columns"]:

        results.extend(
            check_date_format(
                df,
                column
            )
        )

    return results


# ==================================================
# Generate data quality report
# ==================================================

def generate_quality_report(file_name, total_rows, results):

    print("\n" + "=" * 50)
    print("DATA QUALITY REPORT")
    print("=" * 50)

    print(f"Dataset: {file_name}")
    print(f"Rows Checked: {total_rows}")

    if len(results) == 0:

        print("\nNo data quality issues found.")
        print("Quality Status: PASS")
        print("Quality Score: 100.00%")

        print("=" * 50)

        return

    total_issues = 0

    duplicate_count = 0
    null_count = 0
    invalid_count = 0

    print("\nIssues Found:\n")

    for result in results:

        print(
            f"{result['check_type']} | "
            f"{result['column']} | "
            f"Issues: {result['issue_count']}"
        )

        total_issues += result["issue_count"]

        if result["check_type"] == "DUPLICATE_CHECK":
            duplicate_count += result["issue_count"]

        elif result["check_type"] == "NULL_CHECK":
            null_count += result["issue_count"]

        else:
            invalid_count += result["issue_count"]

    quality_score = calculate_quality_score(
        total_rows,
        duplicate_count,
        null_count,
        invalid_count
    )

    status = "PASS"

    if total_issues > 0:
        status = "FAIL"

    print("\n" + "-" * 50)

    print(f"Total Issues: {total_issues}")
    print(f"Duplicates: {duplicate_count}")
    print(f"Null Issues: {null_count}")
    print(f"Other Validation Issues: {invalid_count}")

    print(f"\nQuality Score: {quality_score}%")
    print(f"Quality Status: {status}")

    print("=" * 50)

    # ==================================================
# Write data quality audit log
# ==================================================

def write_quality_log(file_name, total_rows, results):

    duplicate_count = 0
    null_count = 0
    invalid_count = 0

    for result in results:

        if result["check_type"] == "DUPLICATE_CHECK":
            duplicate_count += result["issue_count"]

        elif result["check_type"] == "NULL_CHECK":
            null_count += result["issue_count"]

        else:
            invalid_count += result["issue_count"]

    total_issues = (
        duplicate_count
        + null_count
        + invalid_count
    )

    quality_score = calculate_quality_score(
        total_rows,
        duplicate_count,
        null_count,
        invalid_count
    )

    status = "PASS"

    if total_issues > 0:
        status = "FAIL"

    log_record = pd.DataFrame([{
        "run_timestamp": datetime.now(),
        "file_name": file_name,
        "rows_checked": total_rows,
        "duplicate_issues": duplicate_count,
        "null_issues": null_count,
        "validation_issues": invalid_count,
        "total_issues": total_issues,
        "quality_score": quality_score,
        "status": status
    }])

    if LOG_PATH.exists():

        existing_log = pd.read_csv(LOG_PATH)

        updated_log = pd.concat(
            [existing_log, log_record],
            ignore_index=True
        )

        updated_log.to_csv(
            LOG_PATH,
            index=False
        )

    else:

        log_record.to_csv(
            LOG_PATH,
            index=False
        )

    print(
        f"\nQuality log updated: {LOG_PATH}"
    )