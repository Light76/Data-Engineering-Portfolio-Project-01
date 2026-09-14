"""
config_loader.py

Purpose:
Load pipeline configuration settings from Config/config.json.
"""

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_FILE = (
    PROJECT_ROOT
    / "Config"
    / "config.json"
)


def load_config():
    """
    Load configuration settings.
    """

    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {CONFIG_FILE}"
        )

    with open(
        CONFIG_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        config = json.load(file)

    return config


if __name__ == "__main__":

    configuration = load_config()

    print(configuration)