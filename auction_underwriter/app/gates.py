"""SAU gatekeeper.

This module enforces the one-question-at-a-time gate system. If a required
field is missing, the engine must stop before market, recon, or deal math.
"""

from app.models import GateStopResponse, UnderwriteRequest
from app.rulebook import REQUIRED_SPECS


UNSPECIFIED = "unspecified"


def _has_value(value: object) -> bool:
    """True when a gate answer exists.

    The string "unspecified" counts as a deliberate answer for specs because
    the user is allowed to say unknown. None means unanswered.
    """
    if value is None:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    return True


def _received_so_far(request: UnderwriteRequest) -> dict:
    return {
        "vin": request.vin,
        "year": request.year,
        "make": request.make,
        "model": request.model,
        "trim": request.trim,
        "engine": request.engine,
        "drivetrain": request.drivetrain,
        "transmission": request.transmission,
        "body_style": request.body_style,
        "miles": request.miles,
        "condition": request.condition,
        "title": request.title,
        "channel": request.channel,
        "known_mechanical_issues": request.known_mechanical_issues,
        "known_cosmetic_issues": request.known_cosmetic_issues,
        "listing_notes": request.listing_notes,
        "unseen_risk": request.unseen_risk,
        "current_bid_or_ask": request.current_bid_or_ask,
    }


def _stop(gate: str, missing_field: str, question: str, request: UnderwriteRequest) -> GateStopResponse:
    return GateStopResponse(
        gate=gate,
        missing_field=missing_field,
        question=question,
        received_so_far=_received_so_far(request),
        rule="Hard gate: ask for the next missing item only. Do not continue to market, recon, or deal math.",
    )


def check_gates(request: UnderwriteRequest) -> GateStopResponse | None:
    """Return a STOP response when the next required gate is missing.

    Gate order is strict:
    1) VIN or Year/Make/Model
    2) Specs
    3) Miles
    4) Condition + title
    5) Channel
    6) Damage/Risk Gate
    7) Current bid/ask or unknown
    """

    # Gate 1: VIN preferred. If no VIN, Year/Make/Model are required.
    if not _has_value(request.vin):
        if not _has_value(request.year):
            return _stop("Gate 1 - Vehicle Identity", "year", "What year is the vehicle? VIN is preferred, but year/make/model works.", request)
        if not _has_value(request.make):
            return _stop("Gate 1 - Vehicle Identity", "make", "What make is the vehicle?", request)
        if not _has_value(request.model):
            return _stop("Gate 1 - Vehicle Identity", "model", "What model is the vehicle?", request)

    # Gate 2: Specs. The user may answer each as "unspecified".
    for spec in REQUIRED_SPECS:
        if not _has_value(getattr(request, spec)):
            return _stop(
                "Gate 2 - Specs",
                spec,
                f"What is the {spec.replace('_', ' ')}? You can answer 'unspecified' if unknown.",
                request,
            )

    # Gate 3: Miles.
    if request.miles is None:
        return _stop("Gate 3 - Miles", "miles", "How many miles are on it?", request)

    # Gate 4: Condition + title.
    if request.condition is None:
        return _stop("Gate 4 - Condition", "condition", "Condition: good, fair, or rough?", request)
    if request.title is None:
        return _stop("Gate 4 - Title", "title", "Title status: clean, salvage, rebuilt, or unknown?", request)

    # Gate 5: Channel.
    if request.channel is None:
        return _stop("Gate 5 - Channel", "channel", "Is the channel auction or private?", request)

    # Gate 6: Damage/Risk Gate.
    has_known_risk_info = bool(request.known_mechanical_issues or request.known_cosmetic_issues or request.listing_notes)
    if not has_known_risk_info and request.unseen_risk is None:
        return _stop(
            "Gate 6 - Damage/Risk",
            "unseen_risk",
            "Damage/risk gate: what is known from lights, leaks, noises, visible damage, or listing notes? If unknown, choose unseen risk ON or unseen risk OFF.",
            request,
        )

    # Gate 7: Current bid/ask. User may enter unknown by leaving this absent; this
    # does not block Max Buy, but it changes verdict to PENDING.
    return None
