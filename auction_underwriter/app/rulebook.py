"""Locked rules for Sacramento Auction Underwriter (SAU)."""

MARKET_ZIP = "95835"
MARKET_RADIUS_MILES = 75
FLIP_GOAL_HOURS = 72
PROFIT_FLOOR = 2000

MODES = {
    "DEEP_SEARCH": "default; sources checked required when real browsing is available",
    "QUICK": "offline/no-web; ranges only and no source claims",
    "MARKET_ONLY": "market + desirability + reliability only; no recon or buy math",
    "FULL_UNDERWRITE": "full A-F output with recon, max buy, and verdict",
}

GATE_ORDER = [
    "vehicle_identity",
    "specs",
    "miles",
    "condition_title",
    "channel",
    "damage_risk",
    "bid_or_ask",
    "dtc_codes_optional",
]

REQUIRED_SPECS = ["trim", "engine", "drivetrain", "transmission", "body_style"]

BLIND_RISK_ADDERS = {
    "unknown_maintenance": {"most_likely": 300, "worst": 600},
    "undercarriage_hit": {"most_likely": 400, "worst": 1200},
    "oil_leak": {"most_likely": 250, "worst": 800},
    "cooling_system": {"most_likely": 300, "worst": 900},
    "rough_idle_misfire": {"most_likely": 350, "worst": 1200},
    "transmission_unknown": {"most_likely": 500, "worst": 2500},
    "dash_lights": {"most_likely": 350, "worst": 1200},
    "ac_unknown": {"most_likely": 200, "worst": 800},
    "interior_electrical": {"most_likely": 150, "worst": 500},
}

RULES = {
    "role": "Sacramento Auction Underwriter for an independent dealer",
    "market_zip": MARKET_ZIP,
    "market_radius_miles": MARKET_RADIUS_MILES,
    "flip_goal_hours": FLIP_GOAL_HOURS,
    "profit_floor": PROFIT_FLOOR,
    "modes": MODES,
    "gate_order": GATE_ORDER,
    "required_specs": REQUIRED_SPECS,
    "hard_gate_policy": "Gate 2 runs before analysis. If required input is missing, stop and ask for only the next missing item.",
    "recon_gate_policy": "No recon dollars until channel and damage/risk gate are known.",
    "max_buy_uses": "most_likely_recon_only",
    "auction_bid_policy": "current auction bid is not used in valuation math",
    "unknown_policy": "do not invent unknown year, trim, engine, drivetrain, transmission, body style, title, condition, or value data",
    "evidence_policy": "do not say needs/must unless supported by user, code, visible evidence, or mileage pattern; otherwise use reserve language",
    "labor_policy": "repair time is context only and never changes recon dollars",
    "market_policy": "Sacramento-only for values, velocity, desirability, and market premium notes",
    "mechanical_pattern_policy": "mechanical recon pattern data may be global",
    "formula": "Max Buy = Sacramento 72-hour private party value - Most-Likely Recon - $2,000",
    "blind_risk_adders": BLIND_RISK_ADDERS,
}


def get_rulebook() -> dict:
    """Return the active rulebook for API display."""
    return RULES.copy()
