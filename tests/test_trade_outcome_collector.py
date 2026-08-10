import pytest
import asyncio
from backend.learning.trade_outcome_collector import trade_outcome_collector
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_trade_outcome_collector_recording():
    await init_db()
    trade_data = {
        "id": "TEST_TRADE_101",
        "symbol": "BTC/USDT",
        "side": "LONG",
        "entry_price": 65000.0,
        "exit_price": 66000.0,
        "amount": 0.1,
        "entry_fee": 1.0,
        "exit_fee": 1.0,
        "close_reason": "TAKE_PROFIT",
        "strategy_name": "AI_HYBRID",
        "market_regime": "BULL_TREND"
    }

    outcome = await trade_outcome_collector.record_trade_outcome(trade_data)
    assert outcome.trade_id == "TEST_TRADE_101"
    assert outcome.symbol == "BTC/USDT"
    assert outcome.gross_pnl == 100.0
    assert outcome.net_pnl == 98.0
    assert outcome.take_profit_hit is True

    outcomes = await trade_outcome_collector.get_outcomes(limit=10)
    assert len(outcomes) > 0
    assert any(o["trade_id"] == "TEST_TRADE_101" for o in outcomes)
