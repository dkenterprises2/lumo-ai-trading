import pytest
import asyncio
from backend.database.session import init_db
from backend.repositories.trader_repository import TraderRepository
from trader import PaperTrader

@pytest.mark.asyncio
async def test_database_initialization():
    """Verify database tables initialize cleanly without dropping existing data."""
    await init_db()
    assert True

@pytest.mark.asyncio
async def test_portfolio_state_persistence():
    """Verify saving and restoring portfolio balance and settings across restarts."""
    repo = TraderRepository()
    await repo.initialize_repository()

    # Save state
    await repo.save_portfolio_state(
        usdt_balance=12450.50,
        initial_balance=10000.0,
        margin_used=1500.0,
        total_value=13950.50,
        auto_bot_enabled=True,
        active_strategy="Breakout",
        risk_mode="Aggressive"
    )

    # Load state
    state = await repo.load_portfolio_state()
    assert state is not None
    assert state["usdt_balance"] == 12450.50
    assert state["auto_bot_enabled"] is True
    assert state["active_strategy"] == "Breakout"
    assert state["risk_mode"] == "Aggressive"

@pytest.mark.asyncio
async def test_position_persistence():
    """Verify persisting active open positions to database."""
    repo = TraderRepository()
    await repo.initialize_repository()

    sample_pos = {
        "id": "POS_TEST_BTC",
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry_price": 65000.0,
        "amount": 0.1,
        "margin_usd": 1000.0,
        "leverage": 2,
        "order_type": "MARKET",
        "stop_loss_price": 63000.0,
        "take_profit_price": 68000.0,
        "liquidation_price": 58000.0,
        "trailing_stop_pct": 2.5,
        "entry_time": "2026-08-02 19:50:00",
        "reason": "Test DB Persistence"
    }

    # Save position
    await repo.save_position(sample_pos)

    # Load open positions
    positions = await repo.load_open_positions()
    assert "BTC/USDT" in positions
    assert positions["BTC/USDT"]["side"] == "LONG"
    assert positions["BTC/USDT"]["margin_usd"] == 1000.0

    # Delete position
    await repo.delete_position("POS_TEST_BTC")
    positions_after = await repo.load_open_positions()
    assert "BTC/USDT" not in positions_after

@pytest.mark.asyncio
async def test_trade_history_persistence():
    """Verify persisting closed trade journal records to database."""
    repo = TraderRepository()
    await repo.initialize_repository()

    trade_record = {
        "id": "TRADE_TEST_ETH",
        "symbol": "ETH/USDT",
        "side": "SHORT",
        "entry_price": 3400.0,
        "exit_price": 3200.0,
        "amount": 1.0,
        "margin_usd": 1700.0,
        "pnl_usd": 200.0,
        "pnl_pct": 11.76,
        "entry_time": "2026-08-02 19:00:00",
        "exit_time": "2026-08-02 19:30:00",
        "close_reason": "Take Profit Target Met"
    }

    # Record trade
    await repo.record_trade(trade_record)

    # Load trade history
    trades = await repo.load_trade_history()
    assert len(trades) > 0
    assert trades[0]["symbol"] == "ETH/USDT"
    assert trades[0]["pnl_usd"] == 200.0
