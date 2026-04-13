from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ListingSnapshot:
    price: float
    days: int


@dataclass(frozen=True)
class MarketData:
    move_value: float
    avg_dom: int
    marketability: str  # FAST, NORMAL, SLOW
    listing_count: int


def analyze_market(listings: list[ListingSnapshot]) -> MarketData:
    if not listings:
        raise ValueError("No listings provided")

    fast_prices = [row.price for row in listings if row.days <= 10]

    if fast_prices:
        move_value = sum(fast_prices) / len(fast_prices)
    else:
        move_value = sum(row.price for row in listings) / len(listings)

    avg_dom = int(round(sum(row.days for row in listings) / len(listings)))

    if avg_dom <= 10:
        marketability = "FAST"
    elif avg_dom <= 20:
        marketability = "NORMAL"
    else:
        marketability = "SLOW"

    return MarketData(
        move_value=round(move_value, 2),
        avg_dom=avg_dom,
        marketability=marketability,
        listing_count=len(listings),
    )
