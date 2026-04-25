"""Main SAU underwriting orchestration."""

from app.gates import check_gates
from app.market import build_market_snapshot
from app.models import (
    AuctionCompare,
    DealMath,
    GateStopResponse,
    RiskLevel,
    UnderwriteRequest,
    UnderwriteResponse,
    VehicleSummary,
    Verdict,
)
from app.recon import estimate_recon
from app.rulebook import PROFIT_FLOOR
from app.value_math import calculate_max_buy
from app.vin import decode_vin_stub


def _display(value: object) -> str:
    if value is None:
        return "unspecified"
    if isinstance(value, str) and value.strip() == "":
        return "unspecified"
    return str(value)


def summarize_vehicle(request: UnderwriteRequest) -> VehicleSummary:
    """Echo exact inputs with missing values shown as unspecified."""
    return VehicleSummary(
        vin=request.vin,
        year=request.year,
        make=request.make,
        model=request.model,
        trim=_display(request.trim),
        engine=_display(request.engine),
        drivetrain=_display(request.drivetrain),
        transmission=_display(request.transmission),
        body_style=_display(request.body_style),
        miles=request.miles,
        condition=_display(request.condition),
        title=_display(request.title),
        channel=_display(request.channel),
    )


def determine_risk(request: UnderwriteRequest, recon_most_likely: int | None) -> RiskLevel:
    """Risk label is informational and does not change locked Max Buy math."""
    if request.unseen_risk is True or request.condition == "rough":
        return "HIGH"
    if request.known_mechanical_issues or request.title in {"salvage", "rebuilt", "unknown"}:
        return "HIGH"
    if recon_most_likely is not None and recon_most_likely >= 1500:
        return "HIGH"
    if request.condition == "fair" or (recon_most_likely is not None and recon_most_likely >= 1000):
        return "MEDIUM"
    return "LOW"


def determine_verdict(max_buy: int | None, bid_or_ask: int | None) -> Verdict:
    """Locked verdict rules from SAU master rules."""
    if max_buy is None or bid_or_ask is None:
        return "PENDING"
    if bid_or_ask <= max_buy:
        return "BUY"
    return "PASS"


def build_auction_compare(request: UnderwriteRequest, max_buy: int | None) -> AuctionCompare:
    if request.auction_average is None:
        avg_result = "not provided"
    elif max_buy is None:
        avg_result = "pending - Max Buy unavailable"
    elif request.auction_average <= max_buy:
        avg_result = "BUY ZONE"
    else:
        avg_result = "PASS"

    return AuctionCompare(
        current_bid_or_ask=request.current_bid_or_ask,
        auction_average=request.auction_average,
        current_bid_used_in_math=False,
        auction_average_result=avg_result,
        notes=[
            "Current bid/ask is used only for final BUY/PASS/PENDING comparison, not for value creation.",
            "Auction average is only compared if provided; it is never fabricated.",
        ],
    )


def underwrite_vehicle(request: UnderwriteRequest) -> UnderwriteResponse | GateStopResponse:
    """Run one SAU pass.

    Gates run first. If a gate stops, no market/recon/deal math is performed.
    """
    gate_stop = check_gates(request)
    if gate_stop is not None:
        return gate_stop

    vin_decode = decode_vin_stub(request.vin)
    vehicle = summarize_vehicle(request)
    market = build_market_snapshot(request)

    # MARKET_ONLY mode stops after market/reliability/desirability.
    if request.mode == "MARKET_ONLY":
        return UnderwriteResponse(
            vehicle_summary=vehicle,
            sacramento_market_snapshot=market,
            recon_mechanical=None,
            deal_math=None,
            auction_compare=None,
            verdict=None,
            risk_level=None,
            reasoning=[
                vin_decode["message"],
                "MARKET_ONLY mode: recon, Max Buy, and verdict intentionally skipped.",
            ],
            sources_checked_today=None,
        )

    recon = estimate_recon(request)
    max_buy = calculate_max_buy(market.market_72hr_value, recon.most_likely)
    risk_level = determine_risk(request, recon.most_likely)
    verdict = determine_verdict(max_buy, request.current_bid_or_ask)

    deal_math = DealMath(
        market_72hr_value=market.market_72hr_value,
        recon_used=recon.most_likely,
        profit_floor=PROFIT_FLOOR,
        max_buy=max_buy,
        formula="Max Buy = Sacramento 72-hour private party value - Recon Most-Likely - $2,000",
        notes=[
            "Most-Likely recon is the only recon number used for Max Buy math.",
            "Best and Worst recon are context only.",
            "Current bid/ask does not change Max Buy math.",
        ],
    )

    auction_compare = build_auction_compare(request, max_buy)

    reasoning = [
        vin_decode["message"],
        f"Desirability: {market.desirability_score}/10 {market.desirability_label}.",
        f"Reliability: {market.reliability_score}/10.",
        f"Recon Most-Likely reserve: ${recon.most_likely:,}.",
    ]

    if max_buy is None:
        reasoning.append("Max Buy is pending because 72-hour Sacramento value is missing or not connected.")
    else:
        reasoning.append(f"Max Buy is ${max_buy:,} after protecting the locked ${PROFIT_FLOOR:,} profit floor.")

    if request.current_bid_or_ask is None:
        reasoning.append("Verdict is PENDING because current bid/ask was not provided.")
    elif verdict == "BUY":
        reasoning.append("BUY ZONE because bid/ask is at or below Max Buy.")
    else:
        reasoning.append("PASS because bid/ask is above Max Buy.")

    sources_checked = None
    if request.mode == "DEEP_SEARCH":
        sources_checked = [
            "No live sources checked yet - integration not connected in MVP. Do not claim verified comps.",
        ]

    return UnderwriteResponse(
        vehicle_summary=vehicle,
        sacramento_market_snapshot=market,
        recon_mechanical=recon,
        deal_math=deal_math,
        auction_compare=auction_compare,
        verdict=verdict,
        risk_level=risk_level,
        reasoning=reasoning,
        sources_checked_today=sources_checked,
    )
