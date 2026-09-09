import pandas as pd

from Data_quality import (
    run_data_quality_checks,
    generate_quality_report,
    write_quality_log
)

# Load test dataset
df = pd.read_csv("Data/Bronze/claims.csv")

# Run framework checks
results = run_data_quality_checks(
    df,
    "claims.csv"
)

# Generate report
generate_quality_report(
    file_name="claims.csv",
    total_rows=len(df),
    results=results
)

write_quality_log(
    file_name="claims.csv",
    total_rows=len(df),
    results=results
)