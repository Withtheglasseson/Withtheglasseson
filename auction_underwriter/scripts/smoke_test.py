"""Local smoke test for Sacramento Auction Underwriter.

Run this only after starting the API:

    uvicorn app.main:app --reload

Then in another terminal:

    python scripts/smoke_test.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Any

BASE_URL = "http://127.0.0.1:8000"


def request_json(method: str, path: str, payload: dict | None = None) -> Any:
    url = f"{BASE_URL}{path}"
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach {url}. Make sure the API is running with: uvicorn app.main:app --reload"
        ) from exc


def assert_equal(actual: object, expected: object, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")
    print(f"✅ {label}: {actual!r}")


def assert_true(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"✅ {label}")


def main() -> int:
    print("Running SAU local smoke test...")

    health = request_json("GET", "/health")
    assert_equal(health.get("status"), "ok", "health status")
    assert_equal(health.get("version"), "0.3.0", "api version")

    rulebook = request_json("GET", "/rulebook")
    assert_equal(rulebook.get("rulebook_version"), "SAU_MASTER_V0.2.0", "rulebook version")

    stop_payload = {
        "year": 2008,
        "make": "Toyota",
        "model": "Corolla",
    }
    stop_response = request_json("POST", "/underwrite", stop_payload)
    assert_equal(stop_response.get("status"), "STOP", "gate stop status")
    assert_equal(stop_response.get("gate"), "Gate 2 - Specs", "gate stop location")
    assert_equal(stop_response.get("missing_field"), "trim", "next missing field")

    full_payload = {
        "mode": "FULL_UNDERWRITE",
        "year": 2008,
        "make": "Toyota",
        "model": "Corolla",
        "trim": "CE/LE/S",
        "engine": "unspecified",
        "drivetrain": "FWD",
        "transmission": "automatic",
        "body_style": "sedan",
        "miles": 150000,
        "condition": "good",
        "title": "clean",
        "channel": "auction",
        "known_mechanical_issues": [],
        "known_cosmetic_issues": ["roof rust"],
        "listing_notes": [],
        "unseen_risk": False,
        "market_72hr_value": 6500,
        "current_bid_or_ask": 1600,
    }
    full_response = request_json("POST", "/underwrite", full_payload)
    assert_equal(full_response.get("status"), "PASSED", "completed status")
    assert_equal(full_response.get("output_format"), "A-F", "output format")
    assert_equal(full_response.get("verdict"), "BUY", "verdict")

    deal_math = full_response.get("deal_math") or {}
    assert_equal(deal_math.get("max_buy"), 3700, "max buy")

    saved_response = request_json("POST", "/underwrite/save", full_payload)
    assert_equal(saved_response.get("saved"), True, "saved run flag")
    run_id = saved_response.get("run_id")
    assert_true(isinstance(run_id, int) and run_id > 0, "run id created")

    runs = request_json("GET", "/runs?limit=5")
    assert_true(isinstance(runs, list), "runs endpoint returns a list")
    assert_true(any(run.get("id") == run_id for run in runs), "saved run appears in recent runs")

    run_detail = request_json("GET", f"/runs/{run_id}")
    assert_equal(run_detail.get("id"), run_id, "saved run detail id")
    assert_equal(run_detail.get("rulebook_version"), "SAU_MASTER_V0.2.0", "saved rulebook version")
    assert_equal(run_detail.get("max_buy"), 3700, "saved max buy")

    print("\nSmoke test passed. Gates, underwrite path, and SQLite saved runs are working.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # noqa: BLE001 - smoke test should print clear local error
        print(f"❌ Smoke test failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
