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
    marketability: str  # FAST, NORMAL, SLOW


def _marketability_from_dom(avg_dom: float) -> str:
    if avg_dom <= 10:
        return "FAST"
    if avg_dom <= 20:
        return "NORMAL"
    return "SLOW"


def evaluate_market(listings: list[Listing]) -> MarketOutput:
    """Compute Phase 3 Market Engine outputs from listing price/day data.

    Note: the source spec defines `move_value` but does not define how to derive it.
    This implementation uses average listing price as move_value.
    """
    if not listings:
        raise ValueError("listings must contain at least one listing")

    avg_price = sum(item.price for item in listings) / len(listings)
    avg_dom = sum(item.days for item in listings) / len(listings)

    return MarketOutput(
        move_value=round(avg_price, 2),
        avg_dom=round(avg_dom, 2),
        marketability=_marketability_from_dom(avg_dom),
    )
