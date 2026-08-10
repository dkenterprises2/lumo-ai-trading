import pytest
import asyncio
from backend.learning.strategy_weight_loader import strategy_weight_loader
from backend.database.session import init_db

@pytest.mark.asyncio
async def test_strategy_weight_loader_cache_and_rollback():
    await init_db()
    weights = await strategy_weight_loader.get_active_weights("AI_HYBRID", "NEUTRAL")
    assert "ema_weight" in weights
    assert "rsi_weight" in weights
    assert "macd_weight" in weights

    reloaded = await strategy_weight_loader.reload_weights("AI_HYBRID", "NEUTRAL")
    assert "ema_weight" in reloaded

    history = await strategy_weight_loader.get_version_history("AI_HYBRID", limit=10)
    assert isinstance(history, list)

    rb = await strategy_weight_loader.rollback_to_version(1, "AI_HYBRID", "NEUTRAL")
    assert "status" in rb
