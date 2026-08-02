import pytest
from trader import PaperTrader

def test_paper_trader_initialization():
    trader = PaperTrader(initial_balance=10000.0)
    assert trader.usdt_balance == 10000.0
    assert len(trader.positions) == 0

def test_open_long_position():
    trader = PaperTrader(initial_balance=10000.0)
    res = trader.open_position(
        symbol="BTC/USDT",
        side="LONG",
        price=65000.0,
        allocation_usd=1000.0,
        stop_loss_price=63000.0,
        take_profit_price=68000.0,
        leverage=1
    )

    assert res["status"] == "success"
    assert "BTC/USDT" in trader.positions
    assert trader.usdt_balance == 9000.0

def test_open_short_position():
    trader = PaperTrader(initial_balance=10000.0)
    res = trader.open_position(
        symbol="ETH/USDT",
        side="SHORT",
        price=3400.0,
        allocation_usd=1000.0,
        stop_loss_price=3550.0,
        take_profit_price=3100.0,
        leverage=2
    )

    assert res["status"] == "success"
    assert "ETH/USDT" in trader.positions
    assert trader.positions["ETH/USDT"]["side"] == "SHORT"
    assert trader.usdt_balance == 9500.0 # Margin is 1000 / 2 = 500

def test_close_position():
    trader = PaperTrader(initial_balance=10000.0)
    trader.open_position("BTC/USDT", "LONG", 65000.0, 1000.0, 63000.0, 68000.0, 1)
    
    res = trader.close_position("BTC/USDT", 67000.0, reason="Take profit")
    assert res["status"] == "success"
    assert "BTC/USDT" not in trader.positions
    assert trader.usdt_balance > 10000.0  # Profit made

def test_reverse_position():
    trader = PaperTrader(initial_balance=10000.0)
    trader.open_position("SOL/USDT", "LONG", 180.0, 1000.0, 175.0, 195.0, 1)
    
    res = trader.reverse_position("SOL/USDT", 185.0)
    assert res["status"] == "success"
    assert trader.positions["SOL/USDT"]["side"] == "SHORT"
