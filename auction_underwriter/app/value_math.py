"""Profit and max-buy math for underwriting."""

from app.rulebook import PROFIT_FLOOR


def calculate_max_buy(market_72hr_value: int | None, recon_likely: int) -> int | None:
    """Calculate max buy using locked formula.

    Max Buy = 72-hour retail value - most-likely recon - profit floor.
    If market value is unknown, max buy must stay unknown instead of guessed.
    """
    if market_72hr_value is None:
        return None
    return market_72hr_value - recon_likely - PROFIT_FLOOR


def safe_buy_zone(max_buy: int | None) -> str:
    """Return a simple safe-buy phrase."""
    if max_buy is None:
        return "unknown until 72-hour market value is supplied"
    return f"≤ ${max_buy:,}"
