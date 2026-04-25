"""Sacramento market snapshot logic.

External market sources are still stubbed. This module follows the SAU scoring
rules and never claims that live comps were checked unless a real integration
adds that evidence later.
"""

from app.models import MarketSnapshot, UnderwriteRequest
from app.rulebook import MARKET_RADIUS_MILES, MARKET_ZIP


def _desirability_label(score: int) -> str:
    if score >= 8:
        return "HOT"
    if score >= 5:
        return "WARM"
    return "COLD"


def score_desirability(request: UnderwriteRequest) -> tuple[int, str, list[str]]:
    """Score Sacramento desirability using the SAU quick math."""
    score = 5
    notes: list[str] = ["Started desirability at 5 per SAU rule."]
    make = (request.make or "").lower()
    model = (request.model or "").lower()
    body = (request.body_style or "").lower()
    drivetrain = (request.drivetrain or "").lower()
    transmission = (request.transmission or "").lower()

    toyota_honda_commuters = {"toyota", "honda"}
    commuter_models = ["corolla", "camry", "civic", "accord", "prius", "rav4", "cr-v", "crv"]
    truck_suv_terms = ["truck", "pickup", "suv", "tacoma", "tundra", "4runner", "sequoia", "rav4", "cr-v", "crv", "pilot", "highlander"]
    luxury_euro = {"bmw", "mercedes", "mercedes-benz", "audi", "volkswagen", "vw", "mini", "land rover", "jaguar", "volvo"}

    if make in toyota_honda_commuters and any(term in model for term in commuter_models):
        score += 2
        notes.append("+2 Toyota/Honda commuter sedan/SUV signal.")

    if request.title == "clean" and request.condition == "good":
        score += 1
        notes.append("+1 clean title and good condition signal.")

    if any(term in body or term in model for term in truck_suv_terms) or drivetrain in {"4x4", "awd"}:
        score += 1
        notes.append("+1 truck/SUV/broad buyer pool signal.")

    if make in luxury_euro:
        score -= 1
        notes.append("-1 luxury Euro / thinner buyer pool signal.")

    if "cvt" in transmission:
        score -= 2
        notes.append("-2 CVT reputation / comeback risk signal.")

    if request.title in {"salvage", "rebuilt", "unknown"}:
        score -= 2
        notes.append("-2 salvage/rebuilt/unknown title retail friction.")

    if request.miles is not None and request.miles >= 180_000 and not any(term in model for term in ["tacoma", "tundra", "4runner"]):
        score -= 1
        notes.append("-1 180k+ miles retail friction.")

    score = max(1, min(10, score))
    return score, _desirability_label(score), notes


def score_reliability(request: UnderwriteRequest) -> tuple[int, list[str]]:
    """Simple platform-based reliability score for MVP."""
    make = (request.make or "").lower()
    model = (request.model or "").lower()
    score = 6
    notes: list[str] = []

    if make in {"toyota", "honda", "lexus", "acura"}:
        score += 2
        notes.append("Strong broad used-market reliability reputation.")

    if any(term in model for term in ["corolla", "camry", "civic", "accord", "prius", "tacoma", "4runner"]):
        score += 1
        notes.append("Platform commonly has strong buyer confidence.")

    if make in {"bmw", "mercedes", "mercedes-benz", "audi", "land rover", "jaguar", "mini"}:
        score -= 2
        notes.append("Luxury/Euro platform increases comeback and repair-cost concern.")

    if request.miles is not None and request.miles >= 200_000:
        score -= 1
        notes.append("High mileage trims reliability confidence.")

    score = max(1, min(10, score))
    return score, notes


def build_market_snapshot(request: UnderwriteRequest) -> MarketSnapshot:
    desirability_score, desirability_label, desirability_notes = score_desirability(request)
    reliability_score, reliability_notes = score_reliability(request)

    notes = desirability_notes + reliability_notes
    confidence = "medium" if request.market_72hr_value is not None else "low"

    if request.market_72hr_value is None:
        value_label = "rough estimate unavailable until market value is supplied or live search is connected"
        notes.append("72-hour Sacramento value not supplied; do not finalize Max Buy from guessed value.")
    elif request.mode == "QUICK":
        value_label = "rough estimate supplied by user/offline workflow"
        notes.append("Quick/no-web mode: no verified comp claims.")
    else:
        value_label = "supplied value pending live comp integration"
        notes.append("Using supplied 72-hour value until live Sacramento comp search is connected.")

    if request.kbb_private_party and request.market_72hr_value and request.market_72hr_value > request.kbb_private_party:
        market_premium = "possible premium vs book based on supplied values only"
    elif request.kbb_private_party and request.market_72hr_value:
        market_premium = "no supplied premium vs book signal"
    else:
        market_premium = "not verified; KBB/book baseline not supplied or connected"

    return MarketSnapshot(
        market_area=f"Sacramento {MARKET_ZIP}, {MARKET_RADIUS_MILES}-mile radius",
        mode=request.mode,
        market_72hr_value=request.market_72hr_value,
        value_label=value_label,
        kbb_private_party=request.kbb_private_party,
        kbb_trade_in=request.kbb_trade_in,
        desirability_score=desirability_score,
        desirability_label=desirability_label,
        reliability_score=reliability_score,
        market_premium_vs_book=market_premium,
        confidence=confidence,
        notes=notes,
    )
