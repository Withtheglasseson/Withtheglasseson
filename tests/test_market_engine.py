import pytest

from app.market_engine import Listing, evaluate_market


def test_market_fast():
    output = evaluate_market([
        Listing(price=10000, days=7),
        Listing(price=12000, days=9),
    ])
    assert output.move_value == 11000
    assert output.avg_dom == 8
    assert output.marketability == "FAST"


def test_market_normal():
    output = evaluate_market([
        Listing(price=10000, days=10),
        Listing(price=11000, days=20),
    ])
    assert output.avg_dom == 15
    assert output.marketability == "NORMAL"


def test_market_slow():
    output = evaluate_market([
        Listing(price=9000, days=21),
        Listing(price=9500, days=35),
    ])
    assert output.avg_dom == 28
    assert output.marketability == "SLOW"


def test_market_requires_listings():
    with pytest.raises(ValueError):
        evaluate_market([])
