from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DealInputs:
    sell_price: float
    buy_price: float
    recon: float
    fees: float
    marketability: str  # FAST, NORMAL, SLOW


@dataclass(frozen=True)
class DealOutcome:
    total_cost: float
    profit: float
    decision: str  # BUY, WATCH, PASS


def calculate_outcome(inputs: DealInputs) -> DealOutcome:
    total_cost = inputs.buy_price + inputs.recon + inputs.fees
    profit = inputs.sell_price - total_cost

    mk = inputs.marketability.upper().strip()

    if profit >= 2000 and mk == "FAST":
        decision = "BUY"
    elif profit >= 1200 and mk == "NORMAL":
        decision = "WATCH"
    else:
        decision = "PASS"

    return DealOutcome(total_cost=round(total_cost, 2), profit=round(profit, 2), decision=decision)
