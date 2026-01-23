"""Entry point for the SUA Hybrid Python version."""
from __future__ import annotations

import pathlib
from dataclasses import asdict
from typing import Any

import yaml
from fastapi import FastAPI
from pydantic import BaseModel, Field

from database import Database
from utils.ai_market_brain import MarketBrain
from utils.ai_triage_brain import TriageBrain
from utils.ai_calibration import CalibrationEngine

CONFIG_PATH = pathlib.Path(__file__).with_name("config.yaml")

app = FastAPI(title="SUA Hybrid System")


class TriageRequest(BaseModel):
    """Request payload for triage decisions."""

    context: dict[str, Any] = Field(default_factory=dict)


class TriageResponse(BaseModel):
    """Response payload for triage decisions."""

    priority: str
    rationale: str
    payload: dict[str, Any]


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict[str, Any]:
    """Load YAML configuration for the system."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


@app.on_event("startup")
def startup() -> None:
    """Initialize system components on startup."""
    config = load_config()

    database = Database(config.get("database", {}))
    database.connect()
    database.init_schema()

    calibration = CalibrationEngine(config.get("calibration", {}))
    calibration.calibrate(database)

    app.state.database = database
    app.state.market_brain = MarketBrain(config.get("market", {}))
    app.state.triage_brain = TriageBrain(config.get("triage", {}))


@app.on_event("shutdown")
def shutdown() -> None:
    """Close resources on shutdown."""
    database: Database | None = getattr(app.state, "database", None)
    if database is not None:
        database.close()


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return service health."""
    return {"status": "ok"}


@app.post("/triage", response_model=TriageResponse)
def triage(request: TriageRequest) -> TriageResponse:
    """Generate a triage decision from market data."""
    database: Database = app.state.database
    market_brain: MarketBrain = app.state.market_brain
    triage_brain: TriageBrain = app.state.triage_brain

    signal = market_brain.analyze(request.context)
    decision = triage_brain.prioritize(signal)
    decision_payload = asdict(decision)

    database.record_decision(decision_payload)

    return TriageResponse(**decision_payload)
