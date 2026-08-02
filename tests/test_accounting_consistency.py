import pytest
import asyncio
from sqlalchemy import delete
from backend.database.session import init_db, AsyncSessionLocal
from backend.repositories.trader_repository import TraderRepository
from backend.models.domain import PositionModel, TradeModel, EquityHistoryModel, PortfolioModel, WalletTransactionModel
from trader import PaperTrader

@pytest.mark.asyncio
async def test_accounting_consistency_scenarios():
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

    # Scenario 1: Open Long
    res_long = trader.open_position("BTC/USDT", "LONG", 60000.0, 2000.0, 58000.0, 65000.0, leverage=2)
    assert res_long["status"] == "success"
    prices = {"BTC/USDT": 61500.0}
    summary_long = trader.get_portfolio_summary(prices)
    assert summary_long["accounting_status"] == "PASS"

    # Verify formula tolerance check
    calc_pf_long = summary_long["usdt_balance"] + summary_long["margin_used"] + summary_long["total_unrealized_pnl_usd"]
    assert abs(summary_long["total_portfolio_value"] - calc_pf_long) <= 0.01

    # Scenario 2: Partial Close
    res_partial = trader.close_position("BTC/USDT", 61500.0, reason="Partial Profit", ratio=0.5)
    assert res_partial["status"] == "success"
    summary_partial = trader.get_portfolio_summary(prices)
    assert summary_partial["accounting_status"] == "PASS"
    calc_pf_partial = summary_partial["usdt_balance"] + summary_partial["margin_used"] + summary_partial["total_unrealized_pnl_usd"]
    assert abs(summary_partial["total_portfolio_value"] - calc_pf_partial) <= 0.01

    # Close remaining long
    trader.close_position("BTC/USDT", 61500.0, reason="Close Remaining")

    # Scenario 3: Open Short
    res_short = trader.open_position("ETH/USDT", "SHORT", 3000.0, 1500.0, 3150.0, 2700.0, leverage=3)
    assert res_short["status"] == "success"
    prices_eth = {"ETH/USDT": 2900.0} # Price down -> profit for SHORT
    summary_short = trader.get_portfolio_summary(prices_eth)
    assert summary_short["accounting_status"] == "PASS"

    # Scenario 4: Reverse Position
    res_reverse = trader.reverse_position("ETH/USDT", 2900.0)
    assert res_reverse["status"] == "success"
    prices_rev = {"ETH/USDT": 2950.0}
    summary_rev = trader.get_portfolio_summary(prices_rev)
    assert summary_rev["accounting_status"] == "PASS"

    # Close reversed position
    trader.close_position("ETH/USDT", 2950.0, reason="Close position")

    # Scenario 5: Liquidation Scenario
    res_liq_pos = trader.open_position("SOL/USDT", "LONG", 150.0, 1000.0, 140.0, 170.0, leverage=10)
    assert res_liq_pos["status"] == "success"
    # Price drops to liquidation price
    prices_liq = {"SOL/USDT": 130.0}
    trader.check_stop_loss_take_profit(prices_liq)
    
    summary_liq = trader.get_portfolio_summary(prices_liq)
    assert summary_liq["accounting_status"] == "PASS"
    calc_pf_liq = summary_liq["usdt_balance"] + summary_liq["margin_used"] + summary_liq["total_unrealized_pnl_usd"]
    assert abs(summary_liq["total_portfolio_value"] - calc_pf_liq) <= 0.01
