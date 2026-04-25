"""Main underwriting orchestration."""

from app.market import build_market_snapshot
from app.models import (
    AuctionCompare,
    DealMath,
    RiskLevel,
    UnderwriteRequest,
    UnderwriteResponse,
    VehicleSummary,
    Verdict,
)
from app.recon import estimate_recon
from app.rulebook import PROFIT_FLOOR
from app.value_math import calculate_max_buy, safe_buy_zone
from app.vin import decode_vin_stub


def summarize_vehicle(request: UnderwriteRequest) -> VehicleSummary:
    return VehicleSummary(
        vin=request.vin,
        year=request.year,
        make=request.make,
        model=request.model,
        trim=request.trim or "unspecified",
        engine=request.engine or "unspecified",
        miles=request.miles,
        condition=request.condition,
        title=request.title,
        channel=request.channel,
    )


def determine_risk(request: UnderwriteRequest, recon_likely: int) -> RiskLevel:
    if request.unseen_risk or request.condition in {"rough", "unknown"}:
        return "HIGH"
    if request.known_mechanical_issues or recon_likely >= 1500 or request.title != "clean":
        return "HIGH"
    if request.condition == "fair" or recon_likely >= 1000:
        return "MEDIUM"
    return "LOW"


def determine_verdict(max_buy: int | None, risk_level: RiskLevel) -> Verdict:
    if max_buy is None:
        return "WATCH"
    if max_buy <= 0:
        return "PASS"
    if risk_level == "HIGH":
        return "WATCH"
    return "BUY"


def underwrite_vehicle(request: UnderwriteRequest) -> UnderwriteResponse:
    """Run one complete underwriting pass."""
    vin_decode = decode_vin_stub(request.vin)
    vehicle = summarize_vehicle(request)
    market = build_market_snapshot(request)
    recon = estimate_recon(request)
    max_buy = calculate_max_buy(market.market_72hr_value, recon.likely)
    risk_level = determine_risk(request, recon.likely)
    verdict = determine_verdict(max_buy, risk_level)

    deal_math = DealMath(
        market_72hr_value=market.market_72hr_value,
        recon_used=recon.likely,
        profit_floor=PROFIT_FLOOR,
        max_buy=max_buy,
        safe_buy_zone=safe_buy_zone(max_buy),
        notes=[
            "Formula: 72-hour market value - most-likely recon - $2,000 profit floor.",
            "Current auction bid is intentionally excluded from Max Buy math.",
        ],
    )

    auction_compare = AuctionCompare(
        current_auction_bid=request.current_auction_bid,
        used_in_math=False,
        notes=[
            "Auction bid is accepted only for display/compare later.",
            "The app tells the dealer what to bid; it does not let the current bid control value.",
        ],
    )

    reasoning = [
        vin_decode["message"],
        f"Desirability is {market.desirability} based on MVP market rules.",
        f"Recon likely reserve is ${recon.likely:,}.",
    ]

    if max_buy is None:
        reasoning.append("Max Buy is unknown because 72-hour market value is missing.")
    else:
        reasoning.append(f"Max Buy is ${max_buy:,} after protecting ${PROFIT_FLOOR:,} profit.")

    if verdict == "WATCH":
        reasoning.append("WATCH means the app needs more market data or risk is too high for a clean BUY call.")
    elif verdict == "PASS":
        reasoning.append("PASS means the math does not protect the required profit.")
    else:
        reasoning.append("BUY means the deal works at or below the safe buy zone.")

    return UnderwriteResponse(
        vehicle_summary=vehicle,
        sacramento_market_snapshot=market,
        recon_reserve=recon,
        deal_math=deal_math,
        auction_compare=auction_compare,
        verdict=verdict,
        risk_level=risk_level,
        reasoning=reasoning,
    )
