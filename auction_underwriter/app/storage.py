"""SQLite persistence for SAU deal records.

This is intentionally simple and local-first. The goal is stability: every
underwrite can be saved with the exact request, response, rulebook version, and
timestamp used at decision time.
"""

from __future__ import annotations

import json
import os
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from app.models import GateStopResponse, UnderwriteRequest, UnderwriteResponse
from app.rulebook import RULEBOOK_VERSION

DEFAULT_DB_PATH = "sau_deals.sqlite3"


def get_db_path() -> Path:
    """Return active SQLite path.

    Override with SAU_DB_PATH for testing or deployment.
    """
    return Path(os.environ.get("SAU_DB_PATH", DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(get_db_path())
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """Create local tables when missing."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS underwrite_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                rulebook_version TEXT NOT NULL,
                status TEXT NOT NULL,
                verdict TEXT,
                max_buy INTEGER,
                year INTEGER,
                make TEXT,
                model TEXT,
                trim TEXT,
                vin TEXT,
                miles INTEGER,
                request_json TEXT NOT NULL,
                response_json TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_underwrite_runs_created_at
            ON underwrite_runs(created_at)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_underwrite_runs_vehicle
            ON underwrite_runs(year, make, model)
            """
        )


def _to_json_dict(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(mode="json")


def _extract_summary(response: UnderwriteResponse | GateStopResponse) -> dict[str, Any]:
    if isinstance(response, GateStopResponse):
        return {
            "status": response.status,
            "verdict": None,
            "max_buy": None,
        }

    max_buy = None
    if response.deal_math is not None:
        max_buy = response.deal_math.max_buy

    return {
        "status": response.status,
        "verdict": response.verdict,
        "max_buy": max_buy,
    }


def save_underwrite_run(
    request: UnderwriteRequest,
    response: UnderwriteResponse | GateStopResponse,
) -> int:
    """Persist one request/response pair and return record id."""
    init_db()
    created_at = datetime.now(UTC).isoformat()
    summary = _extract_summary(response)
    request_json = json.dumps(_to_json_dict(request), sort_keys=True)
    response_json = json.dumps(_to_json_dict(response), sort_keys=True)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO underwrite_runs (
                created_at,
                rulebook_version,
                status,
                verdict,
                max_buy,
                year,
                make,
                model,
                trim,
                vin,
                miles,
                request_json,
                response_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                created_at,
                RULEBOOK_VERSION,
                summary["status"],
                summary["verdict"],
                summary["max_buy"],
                request.year,
                request.make,
                request.model,
                request.trim,
                request.vin,
                request.miles,
                request_json,
                response_json,
            ),
        )
        return int(cursor.lastrowid)


def list_underwrite_runs(limit: int = 25) -> list[dict[str, Any]]:
    """Return recent saved underwrite runs."""
    init_db()
    safe_limit = max(1, min(limit, 100))
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                id,
                created_at,
                rulebook_version,
                status,
                verdict,
                max_buy,
                year,
                make,
                model,
                trim,
                vin,
                miles
            FROM underwrite_runs
            ORDER BY id DESC
            LIMIT ?
            """,
            (safe_limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_underwrite_run(run_id: int) -> dict[str, Any] | None:
    """Return one saved run including full JSON payloads."""
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM underwrite_runs
            WHERE id = ?
            """,
            (run_id,),
        ).fetchone()

    if row is None:
        return None

    data = dict(row)
    data["request_json"] = json.loads(data["request_json"])
    data["response_json"] = json.loads(data["response_json"])
    return data
