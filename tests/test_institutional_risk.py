import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from trader import PaperTrader
from institutional_risk import InstitutionalRiskManager, InstitutionalRiskConfig

import time

def test_risk_rule_1_daily_loss_breach():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(max_daily_loss_usd=200.0, max_daily_loss_pct=2.0))
    trader.risk_manager = risk_mgr

    # Simulate $300 daily loss today
    today_str = time.strftime("%Y-%m-%d %H:%M:%S")
    trader.trade_history.append({"status": "CLOSED", "pnl_usd": -300.0, "exit_time": today_str})


    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="BTC/USDT",
        side="LONG",
        price=65000.0,
        allocation_usd=1000.0
    )

    assert res["passed"] is False
    assert res["rule"] == "MAX_DAILY_LOSS"

def test_risk_rule_2_drawdown_breach():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(max_drawdown_pct=10.0))
    trader.risk_manager = risk_mgr
    trader.peak_equity = 10000.0
    trader.usdt_balance = 8500.0  # 15% drawdown

    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="BTC/USDT",
        side="LONG",
        price=65000.0,
        allocation_usd=1000.0
    )

    assert res["passed"] is False
    assert res["rule"] == "MAX_DRAWDOWN"

def test_risk_rule_3_max_concurrent_trades():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(max_concurrent_trades=2))
    trader.risk_manager = risk_mgr

    trader.positions["BTC/USDT"] = {"id": "p1", "symbol": "BTC/USDT", "side": "LONG", "amount": 0.1, "entry_price": 65000.0, "margin_usd": 1000.0, "notional_val_usd": 6500.0, "leverage": 1, "stop_loss_price": 63000.0, "take_profit_price": 68000.0, "entry_time": "2026-08-06"}
    trader.positions["ETH/USDT"] = {"id": "p2", "symbol": "ETH/USDT", "side": "LONG", "amount": 1.0, "entry_price": 3000.0, "margin_usd": 1000.0, "notional_val_usd": 3000.0, "leverage": 1, "stop_loss_price": 2900.0, "take_profit_price": 3200.0, "entry_time": "2026-08-06"}

    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="SOL/USDT",
        side="LONG",
        price=150.0,
        allocation_usd=1000.0
    )

    assert res["passed"] is False
    assert res["rule"] == "MAX_CONCURRENT_TRADES"

def test_risk_rule_4_max_exposure_cap():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(max_exposure_ratio=2.0))
    trader.risk_manager = risk_mgr

    trader.positions["BTC/USDT"] = {"id": "p1", "symbol": "BTC/USDT", "side": "LONG", "amount": 0.3, "entry_price": 60000.0, "margin_usd": 5000.0, "notional_val_usd": 18000.0, "leverage": 1, "stop_loss_price": 58000.0, "take_profit_price": 65000.0, "entry_time": "2026-08-06"}

    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="ETH/USDT",
        side="LONG",
        price=3000.0,
        allocation_usd=15000.0  # 18000 + 15000 = 33000 > 2.0 * 15000 (2.2x exposure)
    )

    assert res["passed"] is False
    assert res["rule"] == "MAX_EXPOSURE"


def test_risk_rule_5_correlation_filter():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(correlation_filter_enabled=True, correlation_group_limit=2))
    trader.risk_manager = risk_mgr

    trader.positions["BTC/USDT"] = {"id": "p1", "symbol": "BTC/USDT", "side": "LONG", "amount": 0.1, "entry_price": 65000.0, "margin_usd": 1000.0, "notional_val_usd": 6500.0, "leverage": 1, "stop_loss_price": 63000.0, "take_profit_price": 68000.0, "entry_time": "2026-08-06"}
    trader.positions["ETH/USDT"] = {"id": "p2", "symbol": "ETH/USDT", "side": "LONG", "amount": 1.0, "entry_price": 3000.0, "margin_usd": 1000.0, "notional_val_usd": 3000.0, "leverage": 1, "stop_loss_price": 2900.0, "take_profit_price": 3200.0, "entry_time": "2026-08-06"}

    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="SOL/USDT",
        side="LONG",
        price=150.0,
        allocation_usd=1000.0
    )

    assert res["passed"] is False
    assert res["rule"] == "CORRELATION_FILTER"


def test_risk_rule_9_dynamic_atr_stops():
    trader = PaperTrader(initial_balance=10000.0)
    risk_mgr = InstitutionalRiskManager(InstitutionalRiskConfig(sl_atr_multiplier=2.0, tp_atr_multiplier=4.0))

    res = risk_mgr.evaluate_order_risk(
        user_trader=trader,
        symbol="BTC/USDT",
        side="LONG",
        price=65000.0,
        allocation_usd=1000.0,
        ta_data={"atr": 500.0}
    )

    assert res["passed"] is True
    assert res["stop_loss_price"] == 64000.0  # 65000 - (500 * 2)
    assert res["take_profit_price"] == 67000.0  # 65000 + (500 * 4)
