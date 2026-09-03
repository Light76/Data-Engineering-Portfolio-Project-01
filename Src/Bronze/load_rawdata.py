import pandas as pd
from pathlib import Path
from datetime import datetime

# ====================================
# Paths
# ====================================

RAW_PATH = Path("Data/Raw")
BRONZE_PATH = Path("Data/Bronze")
LOG_PATH = Path("Logs/ingestion_log.csv")

# ====================================
# Pipeline Timestamp
# One timestamp for entire batch
# ====================================

load_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# ====================================
# Files to Ingest
# ====================================

files = [
    "claims.csv",
    "partners.csv",
    "policies.csv",
    "premiums.csv",
    "products.csv"
]

# ====================================
# Store log entries
# ====================================

log_records = []

# ====================================
# Process files
# ====================================

for file in files:

    try:

        file_path = RAW_PATH / file

        if file_path.exists():

            # Read raw file
            df = pd.read_csv(file_path)

            # Add metadata
            df["source_file"] = file
            df["load_timestamp"] = load_timestamp

            # Count rows
            record_count = len(df)

            # Write Bronze file
            output_path = BRONZE_PATH / file
            df.to_csv(output_path, index=False)

            # Store log entry
            log_records.append({
                "source_file": file,
                "records_loaded": record_count,
                "load_timestamp": load_timestamp,
                "status": "SUCCESS"
            })

            print(f"Loaded: {file} ({record_count} rows)")

        else:

            log_records.append({
                "source_file": file,
                "records_loaded": 0,
                "load_timestamp": load_timestamp,
                "status": "FILE NOT FOUND"
            })

            print(f"Missing File: {file}")

    except Exception as e:

        log_records.append({
            "source_file": file,
            "records_loaded": 0,
            "load_timestamp": load_timestamp,
            "status": f"FAILED: {str(e)}"
        })

        print(f"Failed: {file}")

# ====================================
# Create Log DataFrame
# ====================================

log_df = pd.DataFrame(log_records)

# ====================================
# Save Log File
# ====================================

log_df.to_csv(LOG_PATH, index=False)

print("\nBronze Layer Load Complete")
print(f"Pipeline Timestamp: {load_timestamp}")