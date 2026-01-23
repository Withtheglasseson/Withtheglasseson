"""Triage decisioning brain logic."""
from __future__ import annotations

from typing import Any

from models import MarketSignal, TriageDecision


class TriageBrain:
    """Prioritize actions based on market signals."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    def prioritize(self, signal: MarketSignal) -> dict[str, Any]:
        """Return a dictionary-based triage decision."""
        decision = TriageDecision(
            priority="low",
            rationale="Placeholder triage outcome.",
            payload={"signal": signal.summary, "metadata": signal.metadata},
        )
        return decision.__dict__
