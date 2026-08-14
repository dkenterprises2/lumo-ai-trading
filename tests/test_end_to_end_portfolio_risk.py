import pytest
from trader import PaperTrader
from backend.portfolio_risk import portfolio_risk_orchestrator

def test_end_to_end_scenarios():
    trader = PaperTrader(user_id=99, initial_balance=10000.0)

    # 1. Normal Trade Execution Gate
    gate_res = portfolio_risk_orchestrator.evaluate_order_gate(
        user_trader=trader,
        symbol="BTC/USDT",
        side="LONG",
        allocation_usd=1000.0,
        leverage=2
    )
    assert gate_res["passed"] is True
    assert gate_res["decision"]["decision"] in ["ALLOWED", "SCALED"]

    # 2. Kill switch activation blocks new entries
    portfolio_risk_orchestrator.risk_engine.kill_switch.activate("Test Halt")
    halt_res = portfolio_risk_orchestrator.evaluate_order_gate(
        user_trader=trader,
        symbol="ETH/USDT",
        side="LONG",
        allocation_usd=1000.0,
        leverage=2
    )
    assert halt_res["passed"] is False
    assert halt_res["decision"]["decision"] == "BLOCKED"

    # Recover kill switch
    portfolio_risk_orchestrator.risk_engine.kill_switch.recover()
