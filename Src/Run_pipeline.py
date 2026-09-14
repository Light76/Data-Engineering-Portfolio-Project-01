"""
run_pipeline.py

Purpose:
Execute the complete Data Engineering Portfolio pipeline.

Execution Order:
1. Bronze
2. Silver
3. Data Quality
4. Referential Integrity
5. Gold

Usage:
python Src/run_pipeline.py
"""

from pathlib import Path
import subprocess
import sys

from Frameworks.logger import get_logger

logger = get_logger("pipeline")


def run_script(script_path):

    logger.info(
        f"Starting: {script_path.name}"
    )

    print(
        f"Running: {script_path.name}"
    )

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        logger.error(
            f"FAILED: {script_path.name}"
        )

        logger.error(
            result.stderr
        )

        print()
        print("=" * 75)
        print("PIPELINE FAILED")
        print("=" * 75)
        print(
            f"Failed Script: "
            f"{script_path.name}"
        )
        print()
        print(result.stderr)

        sys.exit(1)

    logger.info(
        f"Completed: {script_path.name}"
    )

    print(
        f"Completed: "
        f"{script_path.name}"
    )


def main():

    project_root = (
        Path(__file__)
        .resolve()
        .parent
    )

    scripts = [

        # ==========================================================
        # BRONZE
        # ==========================================================

        project_root
        / "Bronze"
        / "load_rawdata.py",

        # ==========================================================
        # SILVER
        # ==========================================================

        project_root
        / "Silver"
        / "partners_silver.py",

        project_root
        / "Silver"
        / "products_silver.py",

        project_root
        / "Silver"
        / "policies_silver.py",

        project_root
        / "Silver"
        / "premiums_silver.py",

        project_root
        / "Silver"
        / "claims_silver.py",

        # ==========================================================
        # FRAMEWORKS
        # ==========================================================

        project_root
        / "Frameworks"
        / "Data_quality.py",

        project_root
        / "Frameworks"
        / "referential_integrity.py",

        # ==========================================================
        # GOLD SUMMARYS
        # ==========================================================

        project_root
        / "Gold"
        / "Portfolio_summary.py",

        project_root
        / "Gold"
        / "Premiums_summary.py",

        project_root
        / "Gold"
        / "Claims_summary.py",

        project_root
        / "Gold"
        / "Performance_summary.py",

        # ==========================================================
        # GOLD DIMENSIONAL
        # ==========================================================

        project_root
        / "Gold"
        / "Premium_performance_dimension.py",

        project_root
        / "Gold"
        / "claim_performance_dimension.py",

        project_root
        / "Gold"
        / "policy_performance_dimension.py",
    ]

    print()
    print("=" * 75)
    print("DATA ENGINEERING PORTFOLIO PIPELINE")
    print("=" * 75)

    logger.info(
        "Pipeline execution started."
    )

    for script in scripts:

        if not script.exists():

            logger.error(
                f"Missing script: {script}"
            )

            raise FileNotFoundError(
                f"Script not found: {script}"
            )

        run_script(script)

    logger.info(
        "Pipeline execution completed."
    )

    print()
    print("=" * 75)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 75)


if __name__ == "__main__":
    main()