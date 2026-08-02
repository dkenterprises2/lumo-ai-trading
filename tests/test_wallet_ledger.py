import pytest
import asyncio
from sqlalchemy import delete
from backend.database.session import init_db, AsyncSessionLocal
from backend.repositories.trader_repository import TraderRepository
from backend.models.domain import PositionModel, TradeModel, EquityHistoryModel, PortfolioModel, WalletTransactionModel
from trader import PaperTrader

@pytest.mark.asyncio
async def test_wallet_ledger_double_entry_reconstruction():
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

    trader = PaperTrader(initial_balance=10000.0)
    await trader.initialize_and_restore_state()

    # 1. Verify initial deposit ledger entry
    assert len(trader.ledger) == 1
    assert trader.ledger[0]["tx_type"] == "DEPOSIT"
    assert trader.ledger[0]["amount"] == 10000.0
    assert trader.ledger[0]["balance_after"] == 10000.0

    # 2. Open Long Position -> OPEN_MARGIN transaction
    res_open = trader.open_position("BTC/USDT", "LONG", 60000.0, 2000.0, 58000.0, 65000.0, leverage=2)
    assert res_open["status"] == "success"
    # Margin = 1000.0. Wallet balance = 9000.0
    assert len(trader.ledger) == 2
    open_tx = trader.ledger[1]
    assert open_tx["tx_type"] == "OPEN_MARGIN"
    assert open_tx["amount"] == -1000.0
    assert open_tx["balance_after"] == 9000.0

    # 3. Close Position with Profit -> RELEASE_MARGIN + REALIZED_PNL transactions
    res_close = trader.close_position("BTC/USDT", 63000.0, reason="Take Profit")
    assert res_close["status"] == "success"
    # Margin release +1000.0, Realized PnL +200.0. Wallet balance = 10200.0
    assert len(trader.ledger) == 4
    rel_tx = trader.ledger[2]
    assert rel_tx["tx_type"] == "RELEASE_MARGIN"
    assert rel_tx["amount"] == 1000.0

    pnl_tx = trader.ledger[3]
    assert pnl_tx["tx_type"] == "REALIZED_PNL"
    assert pnl_tx["amount"] == 200.0
    assert pnl_tx["balance_after"] == 10200.0

    # 4. Verify wallet balance is 100% reconstructable from sum of ledger entries
    reconstructed_balance = sum(tx["amount"] for tx in trader.ledger)
    assert abs(trader.usdt_balance - reconstructed_balance) <= 0.01

    # 5. Persisted DB Ledger check
    await asyncio.sleep(0.5)
    db_ledger = await repo.load_wallet_ledger()
    assert len(db_ledger) == 4
    assert sum(tx["amount"] for tx in db_ledger) == 10200.0
