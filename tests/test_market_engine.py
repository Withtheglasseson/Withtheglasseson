import pytest

from app.market_engine import Listing, evaluate_market


def test_market_engine_fast():
    result = evaluate_market(
        [
            Listing(price=10000, days=7),
            Listing(price=11000, days=10),
            Listing(price=9000, days=8),
        ]
    )
    assert result.move_value == 10000
    assert result.avg_dom == 8.33
    assert result.marketability == "FAST"


def test_market_engine_normal():
    result = evaluate_market(
        [
            Listing(price=12000, days=12),
            Listing(price=13000, days=18),
            Listing(price=15000, days=20),
        ]
    )
    assert result.avg_dom == 16.67
    assert result.marketability == "NORMAL"


def test_market_engine_slow():
    result = evaluate_market(
        [
            Listing(price=14000, days=21),
            Listing(price=13500, days=30),
        ]
    )
    assert result.avg_dom == 25.5
    assert result.marketability == "SLOW"


def test_market_engine_requires_data():
    with pytest.raises(ValueError, match="at least one"):
        evaluate_market([])
