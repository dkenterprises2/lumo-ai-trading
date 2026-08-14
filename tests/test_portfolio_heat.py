import pytest
from backend.portfolio_risk.portfolio_heat import PortfolioHeatEngine

def test_portfolio_heat_calculation():
    engine = PortfolioHeatEngine(default_risk_budget_pct=5.0)
    positions = {
        "BTC/USDT": {
            "entry_price": 50000.0,
            "stop_loss_price": 48000.0, # 4% stop loss
            "amount": 0.1,             # $5,000 notional, $200 risk
            "margin_usd": 1000.0
        }
    }
    res = engine.compute_heat(positions, 10000.0, correlation_risk_score=0.2)
    assert res.gross_heat_pct == 2.0
    assert res.net_heat_pct >= 2.0
    assert res.status == "NORMAL"
