import time
from typing import Dict, Any, Optional

class ExchangeFailoverManager:
    """Exchange Failover Manager handling outage detection & fallback exchange routing."""

    def __init__(self):
        self._exchange_health: Dict[str, bool] = {
            "binance_spot": True,
            "binance_futures": True,
            "bybit_spot": True,
            "bybit_perp": True,
            "okx_spot": True,
            "okx_swap": True,
            "paper": True
        }

    def report_health(self, exchange: str, is_healthy: bool):
        self._exchange_health[exchange] = is_healthy

    def get_fallback_exchange(self, primary_exchange: str) -> str:
        """Return operational fallback exchange if primary is down."""
        if self._exchange_health.get(primary_exchange, True):
            return primary_exchange

        fallbacks = ["bybit_spot", "okx_spot", "binance_spot", "paper"]
        for f in fallbacks:
            if f != primary_exchange and self._exchange_health.get(f, True):
                return f

        return "paper"

failover_manager = ExchangeFailoverManager()
