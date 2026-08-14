import pytest
from backend.system.health_aggregator import HealthAggregator
from backend.exchange.market_data_health import MarketDataHealthMonitor

def test_health_aggregator_status():
    agg = HealthAggregator()
    status = agg.get_aggregated_health()
    assert status.db_status == "SYNCED"
    assert status.validation_status == "VERIFIED"
    assert status.governance_ready is True
    assert status.paper_trading_mode is True

def test_module_registry():
    agg = HealthAggregator()
    modules = agg.get_module_registry()
    assert "portfolio_risk_engine" in modules
    assert modules["portfolio_risk_engine"] == "REAL"
    assert modules["agentic_workflow_bus"] == "MOCK"

def test_market_data_health():
    monitor = MarketDataHealthMonitor()
    health = monitor.get_health("BINANCE")
    assert health.exchange == "BINANCE"
    assert health.ticker_latency_ms < 50.0
    assert health.rest_success_rate_pct > 95.0

def test_system_health_model_export():
    agg = HealthAggregator()
    status = agg.get_system_health()
    d = status.model_dump()
    assert d["db_status"] == "SYNCED"
    assert d["validation_status"] == "VERIFIED"

def test_governance_readiness_conditions():
    agg = HealthAggregator()
    agg._override_db_status = "PENDING"
    status = agg.get_aggregated_health()
    assert status.governance_ready is False

def test_all_exchange_health_retrieval():
    monitor = MarketDataHealthMonitor()
    all_h = monitor.get_all_health()
    assert "BINANCE" in all_h
    assert "BYBIT" in all_h
    assert "OKX" in all_h

def test_unknown_exchange_health_fallback():
    monitor = MarketDataHealthMonitor()
    h = monitor.get_health("UNKNOWN_EX")
    assert h.ws_market_data_available is False

