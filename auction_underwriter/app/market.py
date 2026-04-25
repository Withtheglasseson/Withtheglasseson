"""Sacramento market snapshot logic.

External data sources are intentionally stubbed for the MVP. The engine can run
with user-supplied values first, then real integrations can be added later.
"""

from app.models import MarketSnapshot, UnderwriteRequest
from app.rulebook import MARKET_RADIUS_MILES, MARKET_ZIP


def classify_desirability(request: UnderwriteRequest) -> tuple[str, list[str]]:
    """Return HOT/WARM/COLD using simple MVP heuristics."""
    notes: list[str] = []
    make = (request.make or "").lower()
    model = (request.model or "").lower()

    reliable_fast_flip_keywords = [
        "corolla",
        "camry",
        "civic",
        "accord",
        "prius",
        "rav4",
        "cr-v",
        "crv",
        "tacoma",
        "4runner",
    ]

    if any(keyword in model for keyword in reliable_fast_flip_keywords):
        notes.append("Model matches common fast-flip reliable-demand segment.")
        return "HOT", notes

    if make in {"toyota", "honda", "lexus", "acura"}:
        notes.append("Make has strong used-market reputation in Sacramento-style retail.")
        return "WARM", notes

    notes.append("No MVP hot-market signal found yet.")
    return "WARM", notes


def build_market_snapshot(request: UnderwriteRequest) -> MarketSnapshot:
    desirability, notes = classify_desirability(request)

    confidence = "medium" if request.market_72hr_value is not None else "low"
    if request.market_72hr_value is None:
        notes.append("72-hour market value not supplied; max buy cannot be finalized.")
    else:
        notes.append("Using supplied 72-hour market value until live market search is connected.")

    if request.kbb_private_party is None:
        notes.append("KBB private party value not connected/supplied yet.")
    if request.kbb_trade_in is None:
        notes.append("KBB trade-in value not connected/supplied yet.")

    return MarketSnapshot(
        market_area=f"Sacramento {MARKET_ZIP}, {MARKET_RADIUS_MILES}-mile radius",
        market_72hr_value=request.market_72hr_value,
        kbb_private_party=request.kbb_private_party,
        kbb_trade_in=request.kbb_trade_in,
        desirability=desirability,
        confidence=confidence,
        notes=notes,
    )
