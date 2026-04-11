from __future__ import annotations

from dataclasses import dataclass


LOCKED_FLOW = [
    "VIN",
    "IDENTITY",
    "MECHANICAL PROBLEM HISTORY",
    "MARKET",
    "AUCTION",
    "ALIGNMENT",
    "RECON",
    "DEAL MATH",
    "MARKETABILITY CHECK",
]


@dataclass(frozen=True)
class FlowValidator:
    """Validates that app navigation follows the locked phase order."""

    flow: list[str]

    def is_locked_flow(self) -> bool:
        return self.flow == LOCKED_FLOW

    def next_phase(self, current_phase: str) -> str | None:
        if current_phase not in LOCKED_FLOW:
            raise ValueError(f"Unknown phase: {current_phase}")
        idx = LOCKED_FLOW.index(current_phase)
        return LOCKED_FLOW[idx + 1] if idx + 1 < len(LOCKED_FLOW) else None
