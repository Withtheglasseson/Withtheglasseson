"""Basic tests for the SAU underwriting engine."""

from app.models import GateStopResponse, UnderwriteRequest, UnderwriteResponse
from app.underwriter import underwrite_vehicle
from app.value_math import calculate_max_buy


def test_calculate_max_buy():
    assert calculate_max_buy(6500, 600) == 3900


def test_gate_2_stops_before_analysis_when_specs_missing():
    request = UnderwriteRequest(
        year=2008,
        make="Toyota",
        model="Corolla",
    )

    response = underwrite_vehicle(request)

    assert isinstance(response, GateStopResponse)
    assert response.status == "STOP"
    assert response.gate == "Gate 2 - Specs"
    assert response.missing_field == "trim"


def test_underwrite_buy_call_for_clean_corolla_after_gates_pass():
    request = UnderwriteRequest(
        year=2008,
        make="Toyota",
        model="Corolla",
        trim="CE/LE/S",
        engine="unspecified",
        drivetrain="FWD",
        transmission="automatic",
        body_style="sedan",
        miles=150000,
        condition="good",
        title="clean",
        channel="auction",
        known_mechanical_issues=[],
        known_cosmetic_issues=["roof rust"],
        unseen_risk=False,
        market_72hr_value=6500,
        current_bid_or_ask=1600,
    )

    response = underwrite_vehicle(request)

    assert isinstance(response, UnderwriteResponse)
    assert response.deal_math is not None
    assert response.auction_compare is not None
    assert response.deal_math.profit_floor == 2000
    assert response.auction_compare.current_bid_used_in_math is False
    assert response.deal_math.max_buy == 3700
    assert response.verdict == "BUY"


def test_missing_market_value_does_not_guess_max_buy_after_gates_pass():
    request = UnderwriteRequest(
        year=2007,
        make="Honda",
        model="Civic Si",
        trim="Si",
        engine="2.0L",
        drivetrain="FWD",
        transmission="manual",
        body_style="coupe",
        miles=180000,
        condition="good",
        title="clean",
        channel="auction",
        unseen_risk=False,
    )

    response = underwrite_vehicle(request)

    assert isinstance(response, UnderwriteResponse)
    assert response.deal_math is not None
    assert response.deal_math.max_buy is None
    assert response.verdict == "PENDING"
