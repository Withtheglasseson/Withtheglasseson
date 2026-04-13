from app.deal_decision import DealInputs, calculate_outcome
from app.flow import FlowValidator, LOCKED_FLOW
from app.market_engine import ListingSnapshot, analyze_market


def test_flow_is_locked():
    validator = FlowValidator(flow=LOCKED_FLOW.copy())
    assert validator.is_locked_flow() is True
    assert validator.next_phase("VIN") == "IDENTITY"


def test_buy_decision():
    outcome = calculate_outcome(
        DealInputs(sell_price=15000, buy_price=11000, recon=1200, fees=500, marketability="FAST")
    )
    assert outcome.profit == 2300
    assert outcome.decision == "BUY"


def test_watch_decision():
    outcome = calculate_outcome(
        DealInputs(sell_price=13000, buy_price=10000, recon=1200, fees=500, marketability="NORMAL")
    )
    assert outcome.profit == 1300
    assert outcome.decision == "WATCH"


def test_pass_decision():
    outcome = calculate_outcome(
        DealInputs(sell_price=12000, buy_price=10000, recon=700, fees=400, marketability="SLOW")
    )
    assert outcome.decision == "PASS"


def test_market_engine_feeds_deal_decision():
    listings = [
        ListingSnapshot(price=9800, days=7),
        ListingSnapshot(price=9900, days=9),
        ListingSnapshot(price=10500, days=25),
    ]

    market = analyze_market(listings)

    outcome = calculate_outcome(
        DealInputs(
            sell_price=market.move_value,
            buy_price=7200,
            recon=1000,
            fees=400,
            marketability=market.marketability,
        )
    )

    assert market.move_value == 9850.0
    assert market.marketability == "NORMAL"
    assert outcome.total_cost == 8600.0
    assert outcome.profit == 1250.0
    assert outcome.decision == "WATCH"
