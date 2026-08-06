import sys
import os
import pytest
import asyncio
from sqlalchemy import delete

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database.session import init_db, AsyncSessionLocal
from backend.repositories.trader_repository import TraderRepository
from backend.models.journal import TradeJournalModel

@pytest.mark.asyncio
async def test_trade_journal_persistence_and_retrieval():
    await init_db()

    async with AsyncSessionLocal() as session:
        await session.execute(delete(TradeJournalModel))
        await session.commit()

    repo = TraderRepository()

    journal_data = {
        "id": "JRN_TEST_101",
        "user_id": 999,
        "symbol": "BTC/USDT",
        "side": "LONG",
        "strategy": "AI Hybrid",
        "confidence": 85.5,
        "market_regime": "BULL_TREND",
        "sentiment_score": 65.0,
        "score_breakdown": {"trend": {"points": 24.0, "max": 30}, "total": {"points": 85.0, "max": 100}},
        "explainable_reasons": ["EMA Bullish Alignment", "RSI Mean Reversion"],
        "entry_price": 60000.0,
        "exit_price": 63000.0,
        "pnl_usd": 300.0,
        "pnl_pct": 15.0,
        "holding_time_seconds": 3600.0,
        "execution_latency_ms": 0.04,
        "entry_time": "2026-08-06 10:00:00",
        "exit_time": "2026-08-06 11:00:00",
        "close_reason": "Take Profit Met"
    }

    await repo.save_journal_entry(journal_data, user_id=999)

    user_journal = await repo.get_trade_journal(user_id=999)

    assert len(user_journal) == 1
    rec = user_journal[0]
    assert rec["id"] == "JRN_TEST_101"
    assert rec["market_regime"] == "BULL_TREND"
    assert rec["pnl_usd"] == 300.0
    assert rec["score_breakdown"]["total"]["points"] == 85.0
    assert "EMA Bullish Alignment" in rec["reasons"]
