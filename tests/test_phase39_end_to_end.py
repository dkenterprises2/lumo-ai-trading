import pytest
import time
from backend.models.domain import UserModel
from backend.portfolio_risk import portfolio_risk_orchestrator
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine
from backend.arbitrage import (
    CrossExchangeArbitrageEngine,
    ArbitrageShadowRouter,
    ArbitrageMetricsTracker
)
from backend.execution import execution_job_manager
from backend.news_intelligence import (
    EventReasoningEngine,
    EventSignalEngine,
    NewsGovernanceEngine,
    ImpactForecaster
)
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.shadow_trading.shadow_safety_guard import shadow_guard, ShadowTradingViolation

class MockTrader:
    def __init__(self, positions=None):
        self.user_id = "test-user-123"
        self.usdt_balance = 10000.0
        self.initial_balance = 10000.0
        self.positions = positions or {}
        self.trade_history = []
        self.peak_equity = 10000.0
        self.max_open_positions = 10
        self.default_leverage = 10
        self.risk_mode = "BALANCED"

    def get_portfolio_summary(self, prices=None):
        return {
            "total_portfolio_value": 10000.0,
            "total_unrealized_pnl_usd": 0.0,
            "daily_pnl_usd": 0.0
        }

    def _sync_save_portfolio(self):
        pass

def test_risk_score_no_positions():
    engine = InstitutionalPortfolioRiskEngine()
    trader = MockTrader(positions={})
    p_state = engine.evaluate_portfolio_state("test-user-123", trader)
    
    assert p_state.open_positions == 0
    assert p_state.risk_score is None
    assert p_state.metadata["risk_drivers"]["has_active_positions"] is False
    assert p_state.metadata["risk_drivers"]["total_risk_score"] == "N/A"

def test_risk_score_with_positions():
    engine = InstitutionalPortfolioRiskEngine()
    positions = {
        "BTC/USDT": {"symbol": "BTC/USDT", "amount": 0.1, "entry_price": 50000.0},
        "ETH/USDT": {"symbol": "ETH/USDT", "amount": 1.0, "entry_price": 3000.0}
    }
    trader = MockTrader(positions=positions)
    p_state = engine.evaluate_portfolio_state("test-user-123", trader)
    
    assert p_state.open_positions == 2
    assert p_state.risk_score is not None
    assert p_state.risk_score >= 0.0
    assert p_state.metadata["risk_drivers"]["has_active_positions"] is True

def test_risk_score_explainability():
    engine = InstitutionalPortfolioRiskEngine()
    positions = {"BTC/USDT": {"symbol": "BTC/USDT", "amount": 0.1, "entry_price": 50000.0}}
    trader = MockTrader(positions=positions)
    p_state = engine.evaluate_portfolio_state("test-user-123", trader)
    
    drivers = p_state.metadata["risk_drivers"]
    assert "factors" in drivers
    assert "portfolio_heat" in drivers["factors"]
    assert "drawdown" in drivers["factors"]
    assert drivers["factors"]["portfolio_heat"]["weight"] == 0.25

def test_cross_exchange_opportunity_detection():
    arb_engine = CrossExchangeArbitrageEngine()
    opps = arb_engine.scan_opportunities(symbol="BTC/USDT")
    assert isinstance(opps, list)

def test_arbitrage_rejection_statistics():
    tracker = ArbitrageMetricsTracker()
    summary = tracker.get_summary()
    
    assert summary.scanned_routes_count > 0
    assert summary.rejected_by_fees_count >= 0
    assert summary.executable_opportunities >= 0

def test_shadow_arbitrage_execution():
    router = ArbitrageShadowRouter()
    res = router.route_arbitrage_opportunity(
        symbol="BTC/USDT",
        buy_exchange="BINANCE",
        sell_exchange="BYBIT",
        buy_price=118450.0,
        sell_price=118800.0,
        net_spread_pct=0.25,
        amount_usd=10000.0
    )
    
    assert res["status"] == "success"
    assert res["mode"] == "SHADOW"
    assert "execution" in res
    assert res["execution"]["profit_usd"] > 0.0

def test_launch_execution_job():
    mgr = execution_job_manager
    job = mgr.create_job(
        user_id="user-39",
        symbol="BTC/USDT",
        side="BUY",
        algo_type="TWAP",
        total_quantity=1.0,
        num_slices=5
    )
    
    assert job.job_id.startswith("JOB-TWAP-")
    assert job.status in ["RUNNING", "COMPLETED"]
    assert len(job.slices) == 5
    assert job.filled_quantity == 1.0

def test_execution_job_cancel():
    mgr = execution_job_manager
    job = mgr.create_job(
        user_id="user-39",
        symbol="ETH/USDT",
        side="SELL",
        algo_type="VWAP",
        total_quantity=10.0,
        num_slices=5
    )
    job.status = "RUNNING"
    cancelled = mgr.cancel_job(job.job_id, reason="Test cancellation")
    
    assert cancelled.status == "CANCELLED"
    assert cancelled.rejection_reason == "Test cancellation"

def test_news_event_decision():
    reasoning_engine = EventReasoningEngine()
    signal_engine = EventSignalEngine()
    impact_forecaster = ImpactForecaster()
    gov_engine = NewsGovernanceEngine()
    
    title = "SEC Approves Spot Bitcoin ETF Applications"
    source = "CoinDesk"
    symbols = ["BTC/USDT"]
    
    reasoning = reasoning_engine.analyze_event(title, source, symbols)
    sig = signal_engine.generate_signal(reasoning.event_type, symbols[0], reasoning.confidence)
    forecast = impact_forecaster.forecast_impact(symbol=symbols[0], event_type=reasoning.event_type, expected_impact="BULLISH")
    gov = gov_engine.evaluate_news_event(title, source, reasoning.confidence)
    
    assert reasoning.confidence >= 0.80
    assert sig.action == "BUY"
    assert forecast.impact_1h_pct > 0
    assert gov.is_allowed is True

def test_news_shadow_action():
    signal_engine = EventSignalEngine()
    sig = signal_engine.generate_signal("ETF_APPROVAL", "BTC/USDT", 0.95)
    
    assert sig.action == "BUY"
    assert sig.urgency == "HIGH"

def test_arbitrage_real_order_blocked():
    with pytest.raises(ShadowTradingViolation):
        shadow_guard.block_ccxt_create_order("BTC/USDT", "BUY", 1.0)

def test_news_real_order_blocked():
    with pytest.raises(PaperTradingViolation):
        paper_guard.block_live_exchange_order("BINANCE", "BTC/USDT", 1.0)
