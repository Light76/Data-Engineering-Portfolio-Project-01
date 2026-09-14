"""
logger.py

Purpose:
Provide a reusable logger for the entire pipeline.

Used by:
- Bronze
- Silver
- Integrity
- Gold
- run_pipeline.py
"""

import logging
from pathlib import Path

from Frameworks.config_loader import load_config


def get_logger(logger_name="pipeline"):

    config = load_config()

    project_root = Path(__file__).resolve().parents[2]

    log_directory = (
        project_root
        / config["paths"]["logs"]
    )

    log_directory.mkdir(
        parents=True,
        exist_ok=True
    )

    log_file = (
        log_directory
        / config["logging"]["file_name"]
    )

    logger = logging.getLogger(
        logger_name
    )

    logger.setLevel(
        getattr(
            logging,
            config["logging"]["level"]
        )
    )

    if not logger.handlers:

        file_handler = logging.FileHandler(
            log_file,
            mode="a",
            encoding="utf-8"
        )

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler.setFormatter(
            formatter
        )

        logger.addHandler(
            file_handler
        )

    return logger


if __name__ == "__main__":

    logger = get_logger()

    logger.info(
        "Logger test successful."
    )

    print(
        "Logger executed successfully."
    )