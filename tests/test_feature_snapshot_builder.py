import pytest
import asyncio
from main import app  # noqa: F401
from backend.learning.feature_snapshot_builder import feature_snapshot_builder
from backend.database.session import init_db


@pytest.mark.asyncio
async def test_feature_snapshot_builder():
    await init_db()


    f_data = {
        "rsi": 58.5,
        "macd_histogram": 2.4,
        "adx": 32.0,
        "vwap_distance": 0.015,
        "volatility_regime": "HIGH_VOLATILITY"
    }

    snapshot = await feature_snapshot_builder.capture_entry_snapshot("TEST_TRADE_101", f_data)
    assert snapshot.trade_id == "TEST_TRADE_101"
    assert snapshot.rsi == 58.5
    assert snapshot.macd_histogram == 2.4
    assert snapshot.adx == 32.0
    assert snapshot.volatility_regime == "HIGH_VOLATILITY"

    snapshots = await feature_snapshot_builder.get_snapshots(limit=10)
    assert len(snapshots) > 0
    assert any(s["trade_id"] == "TEST_TRADE_101" for s in snapshots)
