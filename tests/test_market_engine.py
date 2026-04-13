from app.market_engine import ListingSnapshot, analyze_market


def test_market_engine_fast_prefers_fast_movers():
    listings = [
        ListingSnapshot(price=9800, days=7),
        ListingSnapshot(price=9900, days=9),
        ListingSnapshot(price=10500, days=25),
    ]

    result = analyze_market(listings)

    assert result.move_value == 9850.0
    assert result.avg_dom == 14
    assert result.marketability == "NORMAL"
    assert result.listing_count == 3


def test_market_engine_uses_all_if_no_fast_movers():
    listings = [
        ListingSnapshot(price=10500, days=21),
        ListingSnapshot(price=10300, days=24),
        ListingSnapshot(price=10100, days=28),
    ]

    result = analyze_market(listings)

    assert result.move_value == 10300.0
    assert result.avg_dom == 24
    assert result.marketability == "SLOW"


def test_market_engine_fast_marketability():
    listings = [
        ListingSnapshot(price=9200, days=6),
        ListingSnapshot(price=9400, days=8),
        ListingSnapshot(price=9600, days=10),
    ]

    result = analyze_market(listings)

    assert result.avg_dom == 8
    assert result.marketability == "FAST"


def test_market_engine_raises_on_empty():
    try:
        analyze_market([])
        assert False, "Expected ValueError"
    except ValueError as exc:
        assert str(exc) == "No listings provided"
