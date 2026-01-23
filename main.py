"""Entry point for the SUA Hybrid Python version."""
from __future__ import annotations

import pathlib
from typing import Any

import yaml

from database import Database
from utils.ai_market_brain import MarketBrain
from utils.ai_triage_brain import TriageBrain
from utils.ai_calibration import CalibrationEngine

CONFIG_PATH = pathlib.Path(__file__).with_name("config.yaml")


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict[str, Any]:
    """Load YAML configuration for the system."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main() -> None:
    """Boot the system using configured components."""
    config = load_config()

    database = Database(config.get("database", {}))
    market_brain = MarketBrain(config.get("market", {}))
    triage_brain = TriageBrain(config.get("triage", {}))
    calibration = CalibrationEngine(config.get("calibration", {}))

    database.connect()
    calibration.calibrate(database)

    market_signal = market_brain.analyze()
    triage_decision = triage_brain.prioritize(market_signal)

    database.record_decision(triage_decision)


if __name__ == "__main__":
    main()
