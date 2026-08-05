import pytest
import asyncio
from sqlalchemy import delete
from backend.database.session import init_db, AsyncSessionLocal
from backend.repositories.trader_repository import TraderRepository
from backend.models.domain import PositionModel, TradeModel, EquityHistoryModel, PortfolioModel, WalletTransactionModel
from trader import PaperTrader

@pytest.mark.asyncio
async def test_portfolio_accounting_and_persistence():
    await init_db()
    
    # Wipe test tables for clean isolation
    async with AsyncSessionLocal() as session:
        await session.execute(delete(PositionModel))
        await session.execute(delete(TradeModel))
        await session.execute(delete(EquityHistoryModel))
        await session.execute(delete(PortfolioModel))
        await session.execute(delete(WalletTransactionModel))
        await session.commit()

    repo = TraderRepository()
    await repo.initialize_repository()

    await repo.save_portfolio_state(
        usdt_balance=10000.0,
        initial_balance=10000.0,
        margin_used=0.0,
        total_value=10000.0,
        auto_bot_enabled=False,
        active_strategy="AI Hybrid",
        risk_mode="Moderate",
        user_id=104
    )

    trader = PaperTrader(initial_balance=10000.0, user_id=104)
    await trader.initialize_and_restore_state()



    # 1. Initial State Check
    summary0 = trader.get_portfolio_summary({"BTC/USDT": 60000.0})
    assert summary0["usdt_balance"] == 10000.0
    assert summary0["margin_used"] == 0.0
    assert summary0["total_unrealized_pnl_usd"] == 0.0
    assert summary0["total_portfolio_value"] == 10000.0
    assert summary0["total_pnl_usd"] == 0.0

    # 2. Open Position (Executed Order)
    res_open = trader.open_position(
        symbol="BTC/USDT",
        side="LONG",
        price=60000.0,
        allocation_usd=2000.0,
        stop_loss_price=58000.0,
        take_profit_price=65000.0,
        leverage=2
    )
    assert res_open["status"] == "success"

    # Margin required = 2000 / 2 = 1000. Wallet balance = 10000 - 1000 = 9000
    assert trader.usdt_balance == 9000.0
    assert len(trader.trade_history) == 1
    assert trader.trade_history[0]["status"] == "OPEN"
    assert trader.trade_history[0]["symbol"] == "BTC/USDT"

    # Price moves to 63000 (+5% price move, 2x leverage => +10% on margin => +200 USD unrealized PnL)
    prices = {"BTC/USDT": 63000.0}
    summary1 = trader.get_portfolio_summary(prices)

    # Formula check:
    # Portfolio Value = Wallet Balance (9000) + Sum(Unrealized PnL) (200) + Margin Value (1000) = 10200.0
    assert summary1["usdt_balance"] == 9000.0
    assert summary1["margin_used"] == 1000.0
    assert summary1["total_unrealized_pnl_usd"] == 200.0
    assert summary1["total_portfolio_value"] == 10200.0
    # Total Profit = Sum(Closed Trade PnL) (0) + Sum(Unrealized PnL) (200) = 200.0
    assert summary1["total_pnl_usd"] == 200.0
    # Daily PnL = Today's Closed PnL (0) + Today's Unrealized PnL (200) = 200.0
    assert summary1["daily_pnl_usd"] == 200.0

    # PnL History snapshot check
    assert len(summary1["pnl_history"]) > 0
    latest_snapshot = summary1["pnl_history"][-1]
    assert latest_snapshot["equity"] == 10200.0
    assert latest_snapshot["wallet"] == 9000.0
    assert latest_snapshot["margin"] == 1000.0

    # Allow async DB tasks to commit
    await trader.flush_persistence()

    # 3. Close Position
    res_close = trader.close_position("BTC/USDT", 63000.0, reason="Take Profit Met")
    assert res_close["status"] == "success"

    # Wallet balance = 9000 + 1000 (margin released) + 200 (realized profit) = 10200.0
    assert trader.usdt_balance == 10200.0

    summary2 = trader.get_portfolio_summary(prices)
    assert summary2["usdt_balance"] == 10200.0
    assert summary2["margin_used"] == 0.0
    assert summary2["total_unrealized_pnl_usd"] == 0.0
    assert summary2["closed_pnl_usd"] == 200.0
    assert summary2["total_portfolio_value"] == 10200.0
    assert summary2["total_pnl_usd"] == 200.0
    assert summary2["win_rate"] == 100.0
    assert summary2["total_closed_trades"] == 1

    # Trade History check
    assert len(summary2["trade_history"]) == 1
    assert summary2["trade_history"][0]["status"] == "CLOSED"
    assert summary2["trade_history"][0]["pnl_usd"] == 200.0

    # Allow async DB tasks to commit
    await trader.flush_persistence()

    # 4. Server Restart Simulation

    new_trader = PaperTrader(initial_balance=10000.0, user_id=104)
    await new_trader.initialize_and_restore_state()


    restored_summary = new_trader.get_portfolio_summary(prices)
    assert restored_summary["usdt_balance"] == 10200.0
    assert restored_summary["margin_used"] == 0.0
    assert restored_summary["total_portfolio_value"] == 10200.0
    assert restored_summary["total_pnl_usd"] == 200.0
    assert len(restored_summary["trade_history"]) >= 1
    assert restored_summary["trade_history"][0]["pnl_usd"] == 200.0
    assert len(restored_summary["pnl_history"]) > 0
