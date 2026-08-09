import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.execution.failover_manager import failover_manager

def test_exchange_failover_manager():
    # Mark primary exchange as unhealthy
    failover_manager.report_health("binance_spot", is_healthy=False)
    fallback = failover_manager.get_fallback_exchange("binance_spot")
    assert fallback != "binance_spot"
    assert fallback in ["bybit_spot", "okx_spot", "paper"]

    # Restore health
    failover_manager.report_health("binance_spot", is_healthy=True)
    assert failover_manager.get_fallback_exchange("binance_spot") == "binance_spot"
