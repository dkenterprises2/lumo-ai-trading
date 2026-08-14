import pytest
import time
from backend.signals.signal_deduplicator import SignalDeduplicator
from backend.signals.signal_rate_limiter import SignalRateLimiter

def test_signal_deduplication():
    dedup = SignalDeduplicator()
    dedup.record_signal("BTC/USDT", "BUY", 0.85)

    # Low confidence delta -> duplicate
    assert dedup.is_duplicate("BTC/USDT", "BUY", 0.86) is True

    # High confidence delta -> NOT duplicate
    assert dedup.is_duplicate("BTC/USDT", "BUY", 0.95) is False

def test_signal_rate_limiter():
    limiter = SignalRateLimiter()
    limiter.record_signal_execution("ETH/USDT")

    # Immediate next signal -> rate limited
    assert limiter.is_rate_limited("ETH/USDT") is True
    # Different symbol -> NOT rate limited
    assert limiter.is_rate_limited("SOL/USDT") is False
