from app.deal_decision import DealInputs, calculate_outcome
from app.flow import FlowValidator, LOCKED_FLOW


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
