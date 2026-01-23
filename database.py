"""Database connectivity helpers."""
from __future__ import annotations

import pathlib
import sqlite3
from typing import Any

import yaml

CONFIG_PATH = pathlib.Path(__file__).with_name("config.yaml")


class Database:
    """Lightweight wrapper around SQLite for the SUA hybrid system."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._connection: sqlite3.Connection | None = None

    def connect(self) -> None:
        """Connect to the configured SQLite database."""
        path = self._config.get("path", "sua.db")
        self._connection = sqlite3.connect(path)

    def init_schema(self) -> None:
        """Ensure the database schema exists."""
        if self._connection is None:
            raise RuntimeError("Database connection is not initialized.")
        cursor = self._connection.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS decisions (id INTEGER PRIMARY KEY, payload TEXT)"
        )
        self._connection.commit()

    def record_decision(self, decision: dict[str, Any]) -> None:
        """Persist a triage decision payload."""
        if self._connection is None:
            raise RuntimeError("Database connection is not initialized.")
        cursor = self._connection.cursor()
        cursor.execute("INSERT INTO decisions (payload) VALUES (?)", (str(decision),))
        self._connection.commit()

    def close(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None


def load_config(path: pathlib.Path = CONFIG_PATH) -> dict[str, Any]:
    """Load YAML configuration for the system."""
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def initialize_database() -> None:
    """Initialize the database schema."""
    config = load_config()
    database = Database(config.get("database", {}))
    database.connect()
    database.init_schema()
    database.close()


if __name__ == "__main__":
    initialize_database()
