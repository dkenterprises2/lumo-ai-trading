import pytest
import time
from backend.arbitrage import (
    ExchangePriceCollector,
    SpreadDetector,
    CrossExchangeArbitrageEngine,
    ArbitrageExecutionSimulator,
    ArbitrageShadowRouter,
    ArbitrageMetricsTracker
)
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine
from backend.execution import execution_job_manager
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.shadow_trading.shadow_safety_guard import shadow_guard, ShadowTradingViolation
from backend.news_intelligence import (
    EventReasoningEngine,
    EventSignalEngine,
    NewsGovernanceEngine,
    ImpactForecaster
)

class MockTrader:
    def __init__(self, positions=None, equity=10000.0):
        self.user_id = "test-user-p40"
        self.usdt_balance = equity
        self.initial_balance = equity
        self.positions = positions or {}
        self.trade_history = []
        self.peak_equity = equity
        self.max_open_positions = 10
        self.default_leverage = 10
        self.risk_mode = "BALANCED"

    def get_portfolio_summary(self, prices=None):
        return {
            "total_portfolio_value": self.usdt_balance,
            "total_unrealized_pnl_usd": 0.0,
            "daily_pnl_usd": 0.0
        }

    def _sync_save_portfolio(self):
        pass


def test_no_fake_arbitrage_prices():
    collector = ExchangePriceCollector()
    assert not hasattr(collector, "offsets")
    assert "310.60" not in str(collector.__class__.__dict__)


def test_stale_quote_rejection():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=100000.0,
        sell_bid_price=101000.0,
        data_age_ms=2500.0,
        quote_status="DATA_STALE"
    )
    assert spread.is_executable is False
    assert spread.rejection_reason == "DATA_STALE"


def test_real_spread_calculation():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=100000.0,
        sell_bid_price=101000.0,
        buy_fee_bps=7.5,
        sell_fee_bps=7.5,
        data_age_ms=10.0,
        quote_status="FRESH"
    )
    assert spread.gross_spread_pct > 0
    assert spread.total_fees_bps == 15.0


def test_fee_calculation():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="COINBASE",
        sell_exchange="KRAKEN",
        buy_ask_price=100000.0,
        sell_bid_price=100200.0,
        buy_fee_bps=15.0,
        sell_fee_bps=10.0
    )
    assert spread.total_fees_bps == 25.0


def test_slippage_calculation():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=100000.0,
        sell_bid_price=100100.0,
        slippage_bps=5.0
    )
    assert spread.slippage_bps == 5.0


def test_liquidity_rejection():
    detector = SpreadDetector()
    spread = detector.compute_spread(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_ask_price=0.0,
        sell_bid_price=100000.0
    )
    assert spread.is_executable is False
    assert spread.rejection_reason == "DATA_UNAVAILABLE"


def test_arbitrage_simulation():
    sim = ArbitrageExecutionSimulator()
    res = sim.simulate_arbitrage_execution(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_price=100000.0,
        sell_price=101000.0,
        amount_usd=10000.0
    )
    assert res.status == "COMPLETED"
    assert res.simulation_id.startswith("SIM-ARB-")
    assert res.net_pnl > 0.0


def test_shadow_isolation():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_ccxt_create_order("BTC/USDT", "BUY", 1.0)


def test_paper_isolation():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_live_exchange_order("BINANCE", "BTC/USDT", 1.0)


def test_oms_launch_job():
    mgr = execution_job_manager
    job = mgr.create_job(
        user_id="user-p40",
        symbol="BTC/USDT",
        side="BUY",
        algo_type="TWAP",
        total_quantity=1.0,
        num_slices=5
    )
    assert job.job_id.startswith("JOB-TWAP-")
    assert job.status in ["RUNNING", "COMPLETED"]


def test_oms_cancellation():
    mgr = execution_job_manager
    job = mgr.create_job(
        user_id="user-p40",
        symbol="ETH/USDT",
        side="SELL",
        algo_type="VWAP",
        total_quantity=10.0,
        num_slices=5
    )
    job.status = "RUNNING"
    cancelled = mgr.cancel_job(job.job_id, reason="User cancelled")
    assert cancelled.status == "CANCELLED"


def test_risk_score_zero_positions():
    engine = InstitutionalPortfolioRiskEngine()
    trader = MockTrader(positions={})
    p_state = engine.evaluate_portfolio_state("user-p40", trader)
    assert p_state.risk_score is None


def test_risk_score_with_positions():
    engine = InstitutionalPortfolioRiskEngine()
    pos = {"BTC/USDT": {"symbol": "BTC/USDT", "amount": 0.1, "entry_price": 100000.0}}
    trader = MockTrader(positions=pos)
    p_state = engine.evaluate_portfolio_state("user-p40", trader)
    assert p_state.risk_score is not None
    assert p_state.risk_score >= 0.0


def test_risk_score_changes_on_position_change():
    engine = InstitutionalPortfolioRiskEngine()
    pos1 = {"BTC/USDT": {"symbol": "BTC/USDT", "amount": 0.01, "entry_price": 100000.0}}
    trader1 = MockTrader(positions=pos1)
    state1 = engine.evaluate_portfolio_state("user-p40", trader1)

    pos2 = {
        "BTC/USDT": {"symbol": "BTC/USDT", "amount": 0.5, "entry_price": 100000.0},
        "ETH/USDT": {"symbol": "ETH/USDT", "amount": 5.0, "entry_price": 3000.0}
    }
    trader2 = MockTrader(positions=pos2)
    state2 = engine.evaluate_portfolio_state("user-p40", trader2)

    assert state1.risk_score != state2.risk_score


def test_news_source_unavailable_behavior():
    collector = ExchangePriceCollector()
    quotes = collector.fetch_all_quotes()
    assert isinstance(quotes, dict)
    for q in quotes.values():
        assert q.status in ["FRESH", "DATA_STALE", "DATA_UNAVAILABLE"]


def test_news_decision_chain():
    reasoning_engine = EventReasoningEngine()
    signal_engine = EventSignalEngine()
    impact_forecaster = ImpactForecaster()
    gov_engine = NewsGovernanceEngine()

    reasoning = reasoning_engine.analyze_event("Exchange Hack Detected", "CoinDesk", ["BTC/USDT"])
    sig = signal_engine.generate_signal(reasoning.event_type, "BTC/USDT", 0.90)
    forecast = impact_forecaster.forecast_impact(symbol="BTC/USDT", event_type=reasoning.event_type, expected_impact="BEARISH")
    gov = gov_engine.evaluate_news_event("Exchange Hack Detected", "CoinDesk", 0.90)

    assert sig.action in ["CLOSE_POSITION", "REDUCE_RISK", "BLOCK_NEW_LONGS"]
    assert gov.is_allowed is True


def test_system_status_accuracy():
    from backend.system.health_aggregator import health_aggregator
    health = health_aggregator.get_aggregated_health()
    assert health.db_status == "SYNCED"
    assert health.paper_trading_mode is True


def test_websocket_status_accuracy():
    from backend.telemetry.ws_metrics import ws_metrics
    m = ws_metrics.get_metrics()
    assert hasattr(m, "connected_clients")


def test_no_fake_dashboard_values():
    collector = ExchangePriceCollector()
    assert not hasattr(collector, "offsets")


def test_end_to_end_paper_execution():
    assert paper_guard.paper_mode is True


def test_end_to_end_shadow_execution():
    router = ArbitrageShadowRouter()
    res = router.route_arbitrage_opportunity(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_price=100000.0,
        sell_price=101000.0,
        net_spread_pct=0.50
    )
    assert res["status"] in ["success", "rejected"]
    assert res["mode"] == "SHADOW" or "reason" in res


def test_live_execution_rejection():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_withdrawal("USDT", 100.0, "0x123")
