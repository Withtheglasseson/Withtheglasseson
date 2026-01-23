"""Database connectivity helpers."""
from __future__ import annotations

import sqlite3
from typing import Any


class Database:
    """Lightweight wrapper around SQLite for the SUA hybrid system."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to the configured SQLite database."""
        path = self._config.get("path", "sua.db")
        self._connection = sqlite3.connect(path)

    def record_decision(self, decision: dict[str, Any]) -> None:
        """Persist a triage decision payload."""
        if self._connection is None:
            raise RuntimeError("Database connection is not initialized.")
        cursor = self._connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        cursor.execute("INSERT INTO decisions (payload) VALUES (?)", (str(decision),))
        self._connection.commit()

    def close(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
