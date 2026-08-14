import time
from typing import Dict, Any, Optional

class SignalDeduplicator:
    """Suppresses duplicate AI trade signals based on symbol, direction, and confidence delta threshold."""

    MIN_CONFIDENCE_DELTA = 0.05

    def __init__(self):
        self._last_signals: Dict[str, Dict[str, Any]] = {}

    def is_duplicate(self, symbol: str, signal_type: str, confidence: float) -> bool:
        """Return True if incoming signal is a duplicate or lacks significant confidence delta."""
        sym_key = f"{symbol.upper()}:{signal_type.upper()}"
        last = self._last_signals.get(sym_key)

        if not last:
            return False

        conf_diff = abs(confidence - last["confidence"])
        if conf_diff < self.MIN_CONFIDENCE_DELTA:
            return True

        return False

    def record_signal(self, symbol: str, signal_type: str, confidence: float):
        sym_key = f"{symbol.upper()}:{signal_type.upper()}"
        self._last_signals[sym_key] = {
            "confidence": confidence,
            "timestamp": time.time()
        }

# Global Singleton Deduplicator
signal_deduplicator = SignalDeduplicator()
