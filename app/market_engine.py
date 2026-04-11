from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Listing:
    price: float
    days: float


@dataclass(frozen=True)
class MarketOutput:
    move_value: float
    avg_dom: float
    marketability: str


def evaluate_market(listings: list[Listing]) -> MarketOutput:
    """
    Evaluate Phase 3 market outputs.

    Note: "move_value" is implemented as the arithmetic mean of listing prices.
    """
    if not listings:
        raise ValueError("At least one listing is required")

    avg_price = sum(item.price for item in listings) / len(listings)
    avg_dom = sum(item.days for item in listings) / len(listings)

    if avg_dom <= 10:
        marketability = "FAST"
    elif avg_dom <= 20:
        marketability = "NORMAL"
    else:
        marketability = "SLOW"

    return MarketOutput(
        move_value=round(avg_price, 2),
        avg_dom=round(avg_dom, 2),
        marketability=marketability,
    )
