"""Tests for SQLite saved underwrite records."""

from app.models import GateStopResponse, UnderwriteRequest, UnderwriteResponse
from app.storage import get_underwrite_run, list_underwrite_runs, save_underwrite_run
from app.underwriter import underwrite_vehicle


def _complete_corolla_request() -> UnderwriteRequest:
    return UnderwriteRequest(
        mode="FULL_UNDERWRITE",
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
        listing_notes=[],
        unseen_risk=False,
        market_72hr_value=6500,
        current_bid_or_ask=1600,
    )


def test_save_completed_underwrite_run(tmp_path, monkeypatch):
    monkeypatch.setenv("SAU_DB_PATH", str(tmp_path / "sau_test.sqlite3"))

    request = _complete_corolla_request()
    response = underwrite_vehicle(request)

    assert isinstance(response, UnderwriteResponse)

    run_id = save_underwrite_run(request, response)
    saved = get_underwrite_run(run_id)

    assert saved is not None
    assert saved["id"] == run_id
    assert saved["status"] == "PASSED"
    assert saved["verdict"] == "BUY"
    assert saved["max_buy"] == 3700
    assert saved["rulebook_version"] == "SAU_MASTER_V0.2.0"
    assert saved["request_json"]["make"] == "Toyota"
    assert saved["response_json"]["deal_math"]["max_buy"] == 3700


def test_save_gate_stop_run(tmp_path, monkeypatch):
    monkeypatch.setenv("SAU_DB_PATH", str(tmp_path / "sau_gate_stop.sqlite3"))

    request = UnderwriteRequest(year=2008, make="Toyota", model="Corolla")
    response = underwrite_vehicle(request)

    assert isinstance(response, GateStopResponse)

    run_id = save_underwrite_run(request, response)
    saved = get_underwrite_run(run_id)

    assert saved is not None
    assert saved["status"] == "STOP"
    assert saved["verdict"] is None
    assert saved["max_buy"] is None
    assert saved["response_json"]["gate"] == "Gate 2 - Specs"
    assert saved["response_json"]["missing_field"] == "trim"


def test_list_underwrite_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("SAU_DB_PATH", str(tmp_path / "sau_list.sqlite3"))

    request = _complete_corolla_request()
    response = underwrite_vehicle(request)
    run_id = save_underwrite_run(request, response)

    runs = list_underwrite_runs(limit=5)

    assert len(runs) == 1
    assert runs[0]["id"] == run_id
    assert runs[0]["make"] == "Toyota"
    assert runs[0]["model"] == "Corolla"
