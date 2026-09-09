import pandas as pd
from pathlib import Path
from datetime import datetime

# Paths
BRONZE_PATH = Path("Data/Bronze")
SILVER_PATH = Path("Data/Silver")
LOG_PATH = Path("Logs/data_quality_log.csv")

# Create Silver folder
SILVER_PATH.mkdir(parents=True, exist_ok=True)

# Find all bronze csv files
bronze_files = list(BRONZE_PATH.glob("*.csv"))

print(f"Found {len(bronze_files)} bronze files")

for file in bronze_files:
    print(f"Processing {file.name}")