"""Market analysis brain logic."""
from __future__ import annotations

from typing import Any

from models import MarketSignal
from utils.api_clients import ApiClient


class MarketBrain:
    """Analyze market data and produce signals."""

    def __init__(self, config: dict[str, Any]) -> None:
        self._config = config
        self._client = ApiClient(config.get("api", {}))

    def analyze(self, context: dict[str, Any] | None = None) -> MarketSignal:
        """Return a summary of the current market conditions."""
        data = self._client.fetch_market_data(context)
        return MarketSignal(summary="No signal generated.", metadata=data)
