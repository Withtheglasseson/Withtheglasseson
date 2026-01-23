"""Domain models for the SUA hybrid system."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class MarketSignal:
    """Represents market signals produced by the market brain."""

    summary: str
    metadata: dict[str, Any]


@dataclass
class TriageDecision:
    """Represents a triage outcome for a given market signal."""

    priority: str
    rationale: str
    payload: dict[str, Any]
