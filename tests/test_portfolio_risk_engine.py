import pytest
from trader import PaperTrader
from backend.portfolio_risk.portfolio_risk_engine import InstitutionalPortfolioRiskEngine

def test_portfolio_risk_engine_snapshot():
    trader = PaperTrader(user_id=1, initial_balance=10000.0)
    trader.max_open_positions = 10
    if hasattr(trader, 'risk_manager') and hasattr(trader.risk_manager, 'config'):
        trader.risk_manager.config.max_concurrent_trades = 10
    engine = InstitutionalPortfolioRiskEngine()

    state = engine.evaluate_portfolio_state("1", trader)
    assert state.user_id == "1"
    assert state.equity == 10000.0
    assert state.effective_max_positions == 10
    assert state.overall_status == "HEALTHY"
