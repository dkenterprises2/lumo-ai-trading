import time
import pytest
from unittest.mock import patch, MagicMock

from backend.arbitrage.background_scanner import ArbitrageBackgroundScanner, arbitrage_background_scanner
from backend.arbitrage.cross_exchange_arbitrage_engine import CrossExchangeArbitrageEngine, CrossExchangeOpportunity
from backend.arbitrage.exchange_price_collector import ExchangePriceCollector, ExchangeQuote
from backend.arbitrage.spread_detector import SpreadDetector, ArbitrageSpread
from backend.arbitrage.arbitrage_metrics import ArbitrageMetricsTracker, arbitrage_metrics_tracker
from backend.arbitrage.arbitrage_ledger import arbitrage_ledger
from backend.arbitrage.arbitrage_shadow_router import ArbitrageShadowRouter

@pytest.fixture(autouse=True)
def reset_arbitrage_state():
    """Reset tracker counters before each test."""
    ArbitrageMetricsTracker.reset()
    yield
    ArbitrageMetricsTracker.reset()

# 1. Background scanner starts and stops cleanly
def test_background_scanner_starts_and_stops_cleanly():
    scanner = ArbitrageBackgroundScanner()
    scanner.stop()
    time.sleep(0.1)
    assert scanner.scanner_running is False
    
    scanner.start()
    assert scanner.scanner_running is True
    assert scanner._thread is not None and scanner._thread.is_alive()
    
    scanner.stop()
    time.sleep(0.3)
    assert scanner.scanner_running is False

# 2. Background scanner continuous execution without HTTP calls
def test_background_scanner_continuous_execution_without_http():
    scanner = ArbitrageBackgroundScanner()
    scanner.stop()
    time.sleep(0.1)
    scanner.interval_seconds = 0.1  # Fast test interval
    scanner.symbols = ["BTC/USDT"]
    
    scanner.start()
    time.sleep(0.5)  # Wait for at least 2 cycles
    
    telemetry = scanner.get_telemetry()
    scanner.stop()
    time.sleep(0.1)
    
    assert telemetry["total_scans"] >= 1
    assert telemetry["last_scan_timestamp"] > 0.0

# 3. Scanner restart prevents duplicate threads
def test_scanner_restart_prevents_duplicate_threads():
    scanner = ArbitrageBackgroundScanner()
    scanner.stop()
    time.sleep(0.1)
    scanner.start()
    t1 = scanner._thread
    
    scanner.start()
    t2 = scanner._thread
    
    assert t1 == t2  # Same thread instance, no duplicates
    scanner.stop()
    time.sleep(0.1)

# 4. All 20 directed routes counted per symbol
def test_all_20_directed_routes_counted():
    engine = CrossExchangeArbitrageEngine()
    ArbitrageMetricsTracker.reset()
    
    # Mock collector returning 5 venues
    mock_quotes = {
        ex: ExchangeQuote(
            exchange=ex,
            symbol="BTC/USDT",
            bid_price=64000.0,
            ask_price=64005.0,
            mid_price=64002.5,
            spread_bps=0.8,
            bid_size=1.0,
            ask_size=1.0,
            data_age_ms=50.0,
            is_live_quote=True,
            status="FRESH"
        ) for ex in ["BINANCE", "BYBIT", "OKX", "KRAKEN", "COINBASE"]
    }
    
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        
        summary = ArbitrageMetricsTracker.get_summary()
        assert summary.scanned_routes_count == 20  # 5 * 4 = 20 routes evaluated

# 5. Negative spread routes counted in rejections
def test_negative_spread_routes_counted_in_rejections():
    engine = CrossExchangeArbitrageEngine()
    ArbitrageMetricsTracker.reset()
    
    # All venues have identical bid/ask -> no positive spread possible
    mock_quotes = {
        ex: ExchangeQuote(
            exchange=ex,
            symbol="BTC/USDT",
            bid_price=64000.0,
            ask_price=64005.0,
            mid_price=64002.5,
            spread_bps=0.8,
            bid_size=1.0,
            ask_size=1.0,
            data_age_ms=50.0,
            is_live_quote=True,
            status="FRESH"
        ) for ex in ["BINANCE", "BYBIT", "OKX", "KRAKEN", "COINBASE"]
    }
    
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        
        summary = ArbitrageMetricsTracker.get_summary()
        assert summary.scanned_routes_count == 20
        assert summary.rejected_by_negative_spread_count == 20
        assert summary.executable_opportunities == 0

# 6. Stale quote rejection counted
def test_stale_quote_rejection_counted():
    engine = CrossExchangeArbitrageEngine()
    ArbitrageMetricsTracker.reset()
    
    # Quotes with stale age > 1500ms
    mock_quotes = {
        "BINANCE": ExchangeQuote("BINANCE", "BTC/USDT", 64000.0, 64005.0, 64002.5, 0.8, 1.0, 1.0, data_age_ms=3000.0, is_live_quote=False, status="STALE"),
        "BYBIT": ExchangeQuote("BYBIT", "BTC/USDT", 64500.0, 64505.0, 64502.5, 0.8, 1.0, 1.0, data_age_ms=3000.0, is_live_quote=False, status="STALE"),
    }
    
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        
        summary = ArbitrageMetricsTracker.get_summary()
        assert summary.scanned_routes_count == 2
        assert summary.rejected_by_stale_count >= 1

# 7. Fallback quote rejection counted
def test_fallback_quote_rejection_counted():
    engine = CrossExchangeArbitrageEngine()
    ArbitrageMetricsTracker.reset()
    
    mock_quotes = {
        "BINANCE": ExchangeQuote("BINANCE", "BTC/USDT", 64000.0, 64005.0, 64002.5, 0.8, 1.0, 1.0, data_age_ms=50.0, is_live_quote=False, is_fallback=True, status="FALLBACK"),
        "BYBIT": ExchangeQuote("BYBIT", "BTC/USDT", 64500.0, 64505.0, 64502.5, 0.8, 1.0, 1.0, data_age_ms=50.0, is_live_quote=False, is_fallback=True, status="FALLBACK"),
    }
    
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        
        summary = ArbitrageMetricsTracker.get_summary()
        assert summary.scanned_routes_count == 2
        assert summary.rejected_by_cached_fallback_count >= 1
        assert len(opps) == 0

# 8. Fee drag rejection counted
def test_fee_drag_rejection_counted():
    engine = CrossExchangeArbitrageEngine()
    ArbitrageMetricsTracker.reset()
    
    # Tiny gross edge (e.g. +$2 on $64,000 = +0.0031%) consumed by 15 bps fees
    mock_quotes = {
        "BINANCE": ExchangeQuote("BINANCE", "BTC/USDT", 64000.0, 64001.0, 64000.5, 0.1, 1.0, 1.0, data_age_ms=50.0, is_live_quote=True, status="FRESH"),
        "BYBIT": ExchangeQuote("BYBIT", "BTC/USDT", 64003.0, 64004.0, 64003.5, 0.1, 1.0, 1.0, data_age_ms=50.0, is_live_quote=True, status="FRESH"),
    }
    
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        
        summary = ArbitrageMetricsTracker.get_summary()
        assert summary.scanned_routes_count == 2
        assert summary.rejected_by_fees_count >= 1
        assert len(opps) == 0

# 9. Liquidity rejection counted
def test_insufficient_liquidity_rejection_counted():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=63000.0,
        sell_bid_price=64000.0,
        buy_ask_size=0.001,  # Only $63 depth (< $1,000 min)
        sell_bid_size=1.0,
        is_live_buy=True,
        is_live_sell=True,
        buy_fee_bps=7.5,
        sell_fee_bps=7.5,
        latency_ms=25.0,
        data_age_ms=50.0
    )
    assert spread.is_executable is False
    assert "LIQUIDITY" in spread.rejection_reason

# 10. Risk and governance rejection counted
def test_risk_and_governance_rejection_counted():
    tracker = ArbitrageMetricsTracker()
    tracker.record_rejection("PORTFOLIO_RISK_LIMIT_EXCEEDED")
    tracker.record_rejection("GOVERNANCE_KILL_SWITCH_ACTIVE")
    
    summary = tracker.get_summary()
    assert summary.rejected_by_risk_count == 1
    assert summary.rejected_by_governance_count == 1

# 11. Strict live data policy blocks fallback execution
def test_strict_live_data_policy_blocks_fallback_execution():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=60000.0,
        sell_bid_price=65000.0,  # Massive theoretical spread
        buy_ask_size=10.0,
        sell_bid_size=10.0,
        is_live_buy=False,  # FALLBACK QUOTE
        is_live_sell=True,
        buy_fee_bps=7.5,
        sell_fee_bps=7.5,
        latency_ms=25.0,
        data_age_ms=50.0,
        quote_status="FALLBACK"
    )
    assert spread.is_executable is False
    assert "FALLBACK" in spread.rejection_reason

# 12. No executable route returns empty opportunities
def test_no_executable_route_returns_empty_opportunities():
    engine = CrossExchangeArbitrageEngine()
    mock_quotes = {
        ex: ExchangeQuote(ex, "BTC/USDT", 64000.0, 64005.0, 64002.5, 0.8, 1.0, 1.0, data_age_ms=50.0, is_live_quote=True, status="FRESH")
        for ex in ["BINANCE", "BYBIT", "OKX", "KRAKEN", "COINBASE"]
    }
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        assert len(opps) == 0

# 13. Best executable spread returns 0.0 when empty
def test_best_executable_spread_returns_zero_when_empty():
    tracker = ArbitrageMetricsTracker()
    summary = tracker.get_summary()
    assert summary.average_net_spread_pct == 0.0
    assert summary.executable_opportunities == 0

# 14. Fresh live route produces executable opportunity
def test_fresh_live_route_produces_executable_opportunity():
    engine = CrossExchangeArbitrageEngine()
    mock_quotes = {
        "BINANCE": ExchangeQuote("BINANCE", "BTC/USDT", 63000.0, 63050.0, 63025.0, 0.8, 2.0, 2.0, data_age_ms=45.0, is_live_quote=True, status="FRESH"),
        "BYBIT": ExchangeQuote("BYBIT", "BTC/USDT", 64000.0, 64050.0, 64025.0, 0.8, 2.0, 2.0, data_age_ms=45.0, is_live_quote=True, status="FRESH"),
    }
    with patch.object(engine.collector, "fetch_all_quotes", return_value=mock_quotes):
        opps = engine.scan_opportunities("BTC/USDT")
        assert len(opps) == 1
        assert opps[0].status == "EXECUTABLE"
        assert opps[0].net_spread_pct > 1.0
        assert opps[0].buy_exchange == "BINANCE"
        assert opps[0].sell_exchange == "BYBIT"

# 15. Opportunity revalidation before shadow execution
def test_opportunity_revalidation_before_shadow_execution():
    router = ArbitrageShadowRouter()
    # Mock collector returning quote with negative spread upon pre-trade re-validation
    vanished_sell_quote = ExchangeQuote("BYBIT", "BTC/USDT", 62000.0, 62050.0, 62025.0, 0.8, 1.0, 1.0, data_age_ms=45.0, is_live_quote=True, status="FRESH")
    fresh_buy_quote = ExchangeQuote("BINANCE", "BTC/USDT", 63000.0, 63050.0, 63025.0, 0.8, 1.0, 1.0, data_age_ms=45.0, is_live_quote=True, status="FRESH")

    def mock_fetch(ex, sym):
        return fresh_buy_quote if ex == "BINANCE" else vanished_sell_quote

    with patch.object(router.collector, "fetch_exchange_quote_real", side_effect=mock_fetch):
        res = router.route_arbitrage_opportunity(
            symbol="BTC/USDT",
            buy_exchange="BINANCE",
            sell_exchange="BYBIT",
            buy_price=63000.0,
            sell_price=64000.0,
            net_spread_pct=1.5,
            amount_usd=10000.0,
            revalidate_live=True
        )
        assert res["status"] == "rejected"
        assert "vanished" in res["reason"].lower() or "price" in res["reason"].lower() or "profitable" in res["reason"].lower()

# 16. Expired opportunity fails execution
def test_expired_opportunity_fails_execution():
    router = ArbitrageShadowRouter()
    stale_quote = ExchangeQuote("BINANCE", "BTC/USDT", 63000.0, 63050.0, 63025.0, 0.8, data_age_ms=4000.0, is_live_quote=False, status="STALE")
    with patch.object(router.collector, "fetch_exchange_quote_real", return_value=stale_quote):
        res = router.route_arbitrage_opportunity(
            symbol="BTC/USDT",
            buy_exchange="BINANCE",
            sell_exchange="BYBIT",
            buy_price=63000.0,
            sell_price=64000.0,
            net_spread_pct=1.5,
            amount_usd=10000.0,
            quote_status="STALE",
            data_age_ms=4000.0
        )
        assert res["status"] == "rejected"

# 17. Shadow execution persists to SQLite ledger
def test_shadow_execution_persists_to_sqlite_ledger():
    import uuid
    import datetime
    route_id = f"TEST-{uuid.uuid4().hex[:6].upper()}"
    detail = {
        "route_id": route_id,
        "symbol": "BTC/USDT",
        "buy_exchange": "BINANCE",
        "sell_exchange": "BYBIT",
        "buy_price": 63000.0,
        "sell_price": 64000.0,
        "net_spread_pct": 1.5,
        "trade_size": 5000.0,
        "profit_usd": 75.0,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "TEST_SHADOW_FILLED",
        "fee_deducted_usd": 7.5
    }
    arbitrage_ledger.record_execution(detail)
    recent = arbitrage_ledger.get_recent_executions(limit=10)
    found = any(r["route_id"] == route_id for r in recent)
    assert found is True

# 18. Wallet unaffected by unexecuted opportunity
def test_wallet_unaffected_by_unexecuted_opportunity():
    from backend.wallet.sub_wallet_manager import sub_wallet_manager
    w_before = sub_wallet_manager.wallets["arbitrage"].usdt_balance
    
    # Generate opportunity
    engine = CrossExchangeArbitrageEngine()
    engine.scan_opportunities("BTC/USDT")
    
    w_after = sub_wallet_manager.wallets["arbitrage"].usdt_balance
    assert w_before == w_after

# 19. Executed routes endpoint has zero mock fallback
def test_executed_routes_endpoint_has_zero_mock_fallback():
    tracker = ArbitrageMetricsTracker()
    routes = tracker.executed_routes
    for r in routes:
        assert r["route_id"] != "ARB-F82A9D01"  # Legacy mock route ID is never present

# 20. Live trading remains permanently blocked
def test_live_trading_permanently_blocked():
    from backend.execution.adapters.live_exchange_adapter import LiveExchangeAdapter
    from backend.execution.execution_intent import ExecutionIntent
    
    adapter = LiveExchangeAdapter("BINANCE")
    intent = ExecutionIntent(
        symbol="BTC/USDT",
        side="BUY",
        order_type="MARKET",
        quantity=0.1,
        target_price=64000.0
    )
    receipt = adapter.execute(intent)
    assert receipt.status == "REJECTED"
    assert "LIVE_DISABLED" in receipt.rejection_reason or "Paper" in receipt.rejection_reason
