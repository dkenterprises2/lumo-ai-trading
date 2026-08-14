import time
from typing import Dict, Any, Optional

class SignalRateLimiter:
    """Enforces cooldown intervals and rate limits per symbol for AI signal generation."""

    MIN_SIGNAL_INTERVAL_SECONDS = 30.0

    def __init__(self):
        self._last_execution_time: Dict[str, float] = {}

    def is_rate_limited(self, symbol: str) -> bool:
        """Return True if signal generation is currently rate-limited for symbol."""
        sym = symbol.upper()
        last_t = self._last_execution_time.get(sym, 0.0)
        return (time.time() - last_t) < self.MIN_SIGNAL_INTERVAL_SECONDS

    def record_signal_execution(self, symbol: str):
        self._last_execution_time[symbol.upper()] = time.time()

# Global Singleton Limiter
signal_rate_limiter = SignalRateLimiter()
