"""Locked rules for Sacramento Auction Underwriter.

These rules are intentionally simple and explicit. The MVP should obey these
before any external data integrations are added.
"""

MARKET_ZIP = "95835"
MARKET_RADIUS_MILES = 75
FLIP_GOAL_HOURS = 72
PROFIT_FLOOR = 2000

RULES = {
    "market_zip": MARKET_ZIP,
    "market_radius_miles": MARKET_RADIUS_MILES,
    "flip_goal_hours": FLIP_GOAL_HOURS,
    "profit_floor": PROFIT_FLOOR,
    "max_buy_uses": "most_likely_recon_only",
    "auction_bid_policy": "current auction bid is not used in valuation math",
    "unknown_policy": "do not invent unknown trim, engine, title, condition, or value data",
    "labor_policy": "do not estimate labor hours",
}


def get_rulebook() -> dict:
    """Return the active rulebook for API display."""
    return RULES.copy()
