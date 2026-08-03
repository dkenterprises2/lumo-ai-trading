import pytest
import asyncio
from sqlalchemy import delete
from backend.database.session import init_db, AsyncSessionLocal
from backend.repositories.trader_repository import TraderRepository
from backend.models.domain import PositionModel, TradeModel, EquityHistoryModel, PortfolioModel, WalletTransactionModel
from trader import PaperTrader

@pytest.mark.asyncio
async def test_server_restart_recovery():
    await init_db()

    # Clean DB isolation
    async with AsyncSessionLocal() as session:
        await session.execute(delete(PositionModel))
        await session.execute(delete(TradeModel))
        await session.execute(delete(EquityHistoryModel))
        await session.execute(delete(PortfolioModel))
        await session.execute(delete(WalletTransactionModel))
        await session.commit()

    repo = TraderRepository()
    await repo.initialize_repository()

    # 1. Execute initial trading sequence
    trader1 = PaperTrader(initial_balance=10000.0)
    await trader1.initialize_and_restore_state()
    await asyncio.sleep(0.3)

    trader1.open_position("BTC/USDT", "LONG", 60000.0, 2000.0, 58000.0, 65000.0, leverage=2)
    trader1.open_position("ETH/USDT", "SHORT", 3000.0, 1500.0, 3150.0, 2700.0, leverage=3)
    await asyncio.sleep(0.3)

    prices1 = {"BTC/USDT": 62000.0, "ETH/USDT": 2900.0}
    pf1 = trader1.get_portfolio_summary(prices1)

    trader1.close_position("BTC/USDT", 62000.0, reason="Take Profit Met")
    await asyncio.sleep(0.3)

    prices2 = {"ETH/USDT": 2950.0}
    pf2 = trader1.get_portfolio_summary(prices2)

    # Allow async DB persistence tasks to complete fully
    await asyncio.sleep(1.0)


    # 2. Simulate complete server restart
    trader2 = PaperTrader(initial_balance=10000.0)
    await trader2.initialize_and_restore_state()

    pf_restored = trader2.get_portfolio_summary(prices2)

    # 3. Verify exact 1:1 match across all metrics
    assert pf_restored["usdt_balance"] == pf2["usdt_balance"]
    assert pf_restored["margin_used"] == pf2["margin_used"]
    assert pf_restored["total_portfolio_value"] == pf2["total_portfolio_value"]
    assert pf_restored["total_pnl_usd"] == pf2["total_pnl_usd"]
    assert pf_restored["accounting_status"] == "PASS"

    # Verify positions, trade history, ledger, and equity history records
    assert len(pf_restored["active_positions"]) == len(pf2["active_positions"])
    assert len(pf_restored["trade_history"]) == len(pf2["trade_history"])
    assert len(pf_restored["ledger"]) == len(pf2["ledger"])
    assert len(pf_restored["pnl_history"]) == len(pf2["pnl_history"])

    # Verify reconstructed ledger sum matches wallet balance
    reconstructed_sum = sum(tx["amount"] for tx in pf_restored["ledger"])
    assert abs(pf_restored["usdt_balance"] - reconstructed_sum) <= 0.01
