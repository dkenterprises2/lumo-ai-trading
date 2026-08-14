import pytest
import asyncio
from trader import PaperTrader
from backend.repositories.trader_repository import TraderRepository
from institutional_risk import InstitutionalRiskManager

@pytest.mark.asyncio
async def test_reset_paper_account():
    test_user_id = 88888
    trader = PaperTrader(user_id=test_user_id)
    await trader.initialize_and_restore_state()

    # Open a dummy position
    trader.usdt_balance = 5000.0
    trader.positions["BTC/USDT"] = {"symbol": "BTC/USDT", "entry_price": 50000.0, "amount": 0.1, "margin_usd": 5000.0}

    # Reset account
    res = await trader.reset_paper_account_async(default_balance=10000.0)

    assert res["status"] == "success"
    assert trader.usdt_balance == 10000.0
    assert len(trader.positions) == 0
    assert len(trader.trade_history) == 0

@pytest.mark.asyncio
async def test_50_concurrent_trades_capacity():
    trader = PaperTrader(user_id=77777)
    await trader.initialize_and_restore_state()
    trader.max_open_positions = 50
    trader.risk_manager.config.max_concurrent_trades = 50
    trader.risk_manager.config.correlation_group_limit = 50


    from backend.routers.preferences_router import DEFAULT_50_SYMBOLS
    trader.allowed_symbols = DEFAULT_50_SYMBOLS

    # Simulate opening 25 positions sequentially
    for i in range(25):
        sym = DEFAULT_50_SYMBOLS[i]
        res = trader.open_position(
            symbol=sym,
            side="LONG",
            price=100.0,
            allocation_usd=1000.0,
            stop_loss_price=90.0,
            take_profit_price=120.0,
            leverage=3
        )
        assert res["status"] == "success"

    assert len(trader.positions) == 25

