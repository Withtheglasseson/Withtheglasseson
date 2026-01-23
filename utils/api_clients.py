"""External API client stubs."""
from __future__ import annotations

from typing import Any


class ApiClient:
    """Placeholder API client for external integrations."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config

    def fetch_market_data(self) -> dict[str, Any]:
        """Return mocked market data payloads."""
        return {"status": "ok", "data": []}
