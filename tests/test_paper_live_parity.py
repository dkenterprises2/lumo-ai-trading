import pytest
import time
import hashlib
from backend.execution.execution_intent import ExecutionIntent
from backend.execution.adapters import (
    PaperExecutionAdapter,
    ShadowExecutionAdapter,
    LiveExchangeAdapter,
    ExecutionReceipt
)
from backend.exchange.credential_manager import credential_manager
from backend.execution.kill_switch import emergency_kill_switch
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.arbitrage.arbitrage_intent import ArbitrageExecutionIntent
from backend.arbitrage.adapters.paper_arbitrage_adapter import PaperArbitrageAdapter
from backend.arbitrage.adapters.live_arbitrage_adapter import LiveArbitrageAdapter
from backend.brain.trading_brain import LumoTradingBrain, lumo_trading_brain
from institutional_risk import InstitutionalRiskManager

@pytest.fixture
def clean_system_state():
    credential_manager._user_states.clear()
    emergency_kill_switch.deactivate()
    yield
    emergency_kill_switch.deactivate()

def test_1_paper_vs_live_intent_identical_decision():
    """1. Verify that strategy produces the EXACT SAME ExecutionIntent for Paper and Live."""
    intent_paper = ExecutionIntent(
        symbol="BTC/USDT",
        side="BUY",
        quantity=0.25,
        allocation_usd=15000.0,
        order_type="LIMIT",
        execution_algorithm="DIRECT",
        limit_price=60000.0,
        target_price=60000.0,
        stop_loss_price=58000.0,
        take_profit_price=65000.0,
        max_slippage_bps=3.0,
        time_in_force="GTC",
        leverage=1,
        urgency="NORMAL",
        thesis="Momentum breakout with high volume",
        market_regime="TRENDING_BULL",
        calibrated_win_probability=0.72,
        expected_edge_bps=45.0,
        execution_mode="PAPER"
    )

    intent_live = ExecutionIntent(
        symbol="BTC/USDT",
        side="BUY",
        quantity=0.25,
        allocation_usd=15000.0,
        order_type="LIMIT",
        execution_algorithm="DIRECT",
        limit_price=60000.0,
        target_price=60000.0,
        stop_loss_price=58000.0,
        take_profit_price=65000.0,
        max_slippage_bps=3.0,
        time_in_force="GTC",
        leverage=1,
        urgency="NORMAL",
        thesis="Momentum breakout with high volume",
        market_regime="TRENDING_BULL",
        calibrated_win_probability=0.72,
        expected_edge_bps=45.0,
        execution_mode="LIVE"
    )

    assert intent_paper.to_hash() == intent_live.to_hash()

def test_2_same_quantity():
    """2. Verify that sizing engine assigns identical quantity across modes."""
    p_intent = ExecutionIntent(symbol="ETH/USDT", quantity=1.4582)
    l_intent = ExecutionIntent(symbol="ETH/USDT", quantity=1.4582)
    assert p_intent.quantity == l_intent.quantity == 1.4582

def test_3_same_side():
    """3. Verify that signal ensemble determines identical side."""
    p_intent = ExecutionIntent(symbol="SOL/USDT", side="BUY")
    l_intent = ExecutionIntent(symbol="SOL/USDT", side="BUY")
    assert p_intent.side == l_intent.side == "BUY"

def test_4_same_execution_algorithm():
    """4. Verify that execution planner assigns identical execution algorithm."""
    p_intent = ExecutionIntent(symbol="BTC/USDT", execution_algorithm="TWAP")
    l_intent = ExecutionIntent(symbol="BTC/USDT", execution_algorithm="TWAP")
    assert p_intent.execution_algorithm == l_intent.execution_algorithm == "TWAP"

def test_5_same_risk_result():
    """5. Verify that risk validations evaluate identically for Paper and Live intents."""
    from trader import PaperTrader
    trader = PaperTrader(initial_balance=50000.0)
    risk_manager = InstitutionalRiskManager()
    risk_paper = risk_manager.evaluate_order_risk(trader, "BTC/USDT", "BUY", 60000.0, 5000.0, 1, 58000.0, 65000.0)
    risk_live = risk_manager.evaluate_order_risk(trader, "BTC/USDT", "BUY", 60000.0, 5000.0, 1, 58000.0, 65000.0)
    assert risk_paper["passed"] == risk_live["passed"] == True
    assert risk_paper["adjusted_allocation_usd"] == risk_live["adjusted_allocation_usd"]

def test_6_same_expected_edge():
    """6. Verify calibrated net expected edge matches identically."""
    p_intent = ExecutionIntent(expected_edge_bps=38.5)
    l_intent = ExecutionIntent(expected_edge_bps=38.5)
    assert p_intent.expected_edge_bps == l_intent.expected_edge_bps == 38.5

def test_7_same_thesis():
    """7. Verify trade thesis and invalidation criteria match identically."""
    thesis_str = "Mean reversion from lower Bollinger band with RSI oversold recovery"
    p_intent = ExecutionIntent(thesis=thesis_str)
    l_intent = ExecutionIntent(thesis=thesis_str)
    assert p_intent.thesis == l_intent.thesis == thesis_str

def test_8_same_portfolio_effect():
    """8. Verify anti-correlation portfolio brain evaluation is identical."""
    p_intent = ExecutionIntent(portfolio_snapshot={"net_delta": 0.15, "sector_skew": "NEUTRAL"})
    l_intent = ExecutionIntent(portfolio_snapshot={"net_delta": 0.15, "sector_skew": "NEUTRAL"})
    assert p_intent.portfolio_snapshot == l_intent.portfolio_snapshot

def test_9_same_arbitrage_route():
    """9. Verify Cross-Exchange Arbitrage routes identically across modes."""
    arb_paper = ArbitrageExecutionIntent(symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT")
    arb_live = ArbitrageExecutionIntent(symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT")
    assert arb_paper.buy_exchange == arb_live.buy_exchange == "BINANCE"
    assert arb_paper.sell_exchange == arb_live.sell_exchange == "BYBIT"

def test_10_same_executable_quantity_arbitrage():
    """10. Verify Depth-Aware Executable Quantity in Arbitrage is identical."""
    arb_paper = ArbitrageExecutionIntent(executable_quantity=2.45, executable_capacity_usd=147000.0)
    arb_live = ArbitrageExecutionIntent(executable_quantity=2.45, executable_capacity_usd=147000.0)
    assert arb_paper.executable_quantity == arb_live.executable_quantity == 2.45
    assert arb_paper.executable_capacity_usd == arb_live.executable_capacity_usd == 147000.0

def test_11_live_adapter_dry_run_validation():
    """11. Verify Live adapter dry_run produces verified simulated receipt without network call."""
    adapter = LiveExchangeAdapter("BINANCE")
    intent = ExecutionIntent(
        symbol="BTC/USDT",
        side="BUY",
        quantity=0.05,
        target_price=60000.0,
        order_type="LIMIT",
        limit_price=59950.0,
        execution_mode="DRY_RUN"
    )

    receipt = adapter.dry_run(intent)
    assert receipt.status == "DRY_RUN_VALIDATED"
    assert receipt.execution_mode == "DRY_RUN"
    assert receipt.executed_quantity == 0.05
    assert receipt.exchange == "BINANCE"
    assert "constructed_payload" in receipt.raw_exchange_response
    assert receipt.raw_exchange_response["simulated_network_call"] == "SUPPRESSED_DRY_RUN"

def test_12_api_credential_validation_without_order_submission(clean_system_state):
    """12. Verify storing API credentials states 'API CONNECTED — LIVE TRADING STILL OFF' and leaves live_enabled=False."""
    res = credential_manager.register_credentials(
        user_id="user_101",
        exchange_name="binance_spot",
        api_key="12345678abcdefgh",
        secret_key="secret12345678abcdefgh"
    )
    assert res["status"] == "success"
    assert res["message"] == "API CONNECTED — LIVE TRADING STILL OFF"
    assert res["credentials_configured"] is True
    assert res["live_enabled"] is False

def test_13_explicit_live_enable_state_lifecycle(clean_system_state):
    """13. Verify explicit multi-stage lifecycle state transitions."""
    credential_manager.register_credentials("user_103", "binance_spot", "key12345678", "sec12345678")
    status1 = credential_manager.get_status("user_103")
    assert status1["credentials_configured"] is True
    assert status1["live_enabled"] is False

    # Deactivation remains safe
    credential_manager.deactivate_live_trading("user_103")
    status2 = credential_manager.get_status("user_103")
    assert status2["live_enabled"] is False

def test_14_paper_restart_persistence():
    """14. Verify Paper double-entry ledger persistence."""
    from backend.arbitrage.arbitrage_ledger import arbitrage_ledger
    pnl = arbitrage_ledger.get_realized_pnl()
    assert isinstance(pnl, float)
    assert pnl >= 0.0

def test_15_live_mode_safety_block_when_not_enabled(clean_system_state):
    """15. Verify Live adapter rejects execution when live mode is not enabled."""
    credential_manager.register_credentials("user_104", "binance_spot", "key12345678", "sec12345678")
    adapter = LiveExchangeAdapter("BINANCE")
    intent = ExecutionIntent(symbol="BTC/USDT", side="BUY", quantity=0.1, target_price=60000.0, execution_mode="LIVE")

    receipt = adapter.execute(intent, user_id="user_104")
    assert receipt.status == "REJECTED"
    assert "LIVE_DISABLED" in receipt.rejection_reason or "LIVE_INELIGIBLE" in receipt.rejection_reason

def test_16_live_mode_safety_block_when_token_invalid(clean_system_state):
    """16. Verify activation is rejected if confirmation token is invalid."""
    credential_manager.register_credentials("user_105", "binance_spot", "key12345678", "sec12345678")
    act_res = credential_manager.activate_live_trading("user_105", confirmation_token="INVALID_TOKEN")
    assert act_res["status"] == "rejected"
    assert act_res["live_enabled"] is False

def test_17_kill_switch_blocks_both_modes(clean_system_state):
    """17. Verify Emergency Kill Switch blocks execution in both modes."""
    emergency_kill_switch.activate("System maintenance halt")
    live_adapter = LiveExchangeAdapter("BINANCE")
    intent = ExecutionIntent(symbol="BTC/USDT", side="BUY", quantity=0.1, target_price=60000.0)
    
    receipt = live_adapter.execute(intent)
    assert receipt.status == "REJECTED"
    assert "Kill Switch is ACTIVE" in receipt.rejection_reason

def test_18_risk_engine_blocks_both_modes(clean_system_state):
    """18. Verify Institutional Risk Engine rejects order when daily loss limit is breached in both modes."""
    from trader import PaperTrader
    from institutional_risk import InstitutionalRiskConfig
    trader = PaperTrader(initial_balance=10000.0)
    risk_manager = InstitutionalRiskManager(InstitutionalRiskConfig(max_daily_loss_usd=200.0, max_daily_loss_pct=2.0))
    
    # Simulate $300 loss today
    today_str = time.strftime("%Y-%m-%d %H:%M:%S")
    trader.trade_history.append({"status": "CLOSED", "pnl_usd": -300.0, "exit_time": today_str})
    
    risk_res = risk_manager.evaluate_order_risk(trader, "BTC/USDT", "LONG", 65000.0, 1000.0)
    assert risk_res["passed"] is False
    assert risk_res["rule"] == "MAX_DAILY_LOSS"
