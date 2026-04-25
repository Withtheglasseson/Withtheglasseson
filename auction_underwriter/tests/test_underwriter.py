"""Basic tests for the underwriting engine."""

from app.models import UnderwriteRequest
from app.underwriter import underwrite_vehicle
from app.value_math import calculate_max_buy


def test_calculate_max_buy():
    assert calculate_max_buy(6500, 600) == 3900


def test_underwrite_buy_call_for_clean_corolla():
    request = UnderwriteRequest(
        year=2008,
        make="Toyota",
        model="Corolla",
        trim="CE/LE/S",
        miles=150000,
        condition="good",
        title="clean",
        channel="auction",
        known_mechanical_issues=[],
        known_cosmetic_issues=["roof rust"],
        unseen_risk=False,
        market_72hr_value=6500,
        current_auction_bid=1600,
    )

    response = underwrite_vehicle(request)

    assert response.deal_math.profit_floor == 2000
    assert response.auction_compare.used_in_math is False
    assert response.deal_math.max_buy == 3700
    assert response.verdict in {"BUY", "WATCH"}


def test_missing_market_value_does_not_guess_max_buy():
    request = UnderwriteRequest(
        year=2007,
        make="Honda",
        model="Civic Si",
        miles=180000,
        condition="good",
        title="clean",
        channel="auction",
    )

    response = underwrite_vehicle(request)

    assert response.deal_math.max_buy is None
    assert response.verdict == "WATCH"
