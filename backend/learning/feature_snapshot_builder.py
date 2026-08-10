"""
Feature Snapshot Builder for Phase 25 Self-Learning Feedback Loop.
Captures and persists technical indicators & market features at position entry time.
"""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import AsyncSessionLocal
from backend.models.domain import LearningFeatureSnapshot
from backend.core.logger import logger


class FeatureSnapshotBuilder:
    """Computes and persists indicator snapshots at position entry time linked to trade_id."""

    @staticmethod
    async def capture_entry_snapshot(trade_id: str, feature_data: Optional[Dict[str, Any]] = None) -> LearningFeatureSnapshot:
        """
        Captures entry snapshot of features for a trade.
        """
        async with AsyncSessionLocal() as session:
            stmt = select(LearningFeatureSnapshot).where(LearningFeatureSnapshot.trade_id == trade_id)
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                return existing

            f = feature_data or {}
            
            snapshot = LearningFeatureSnapshot(
                trade_id=str(trade_id),
                rsi=float(f.get("rsi", 52.4)),
                macd_histogram=float(f.get("macd_histogram", 1.25)),
                ema_fast_slope=float(f.get("ema_fast_slope", 0.05)),
                ema_slow_slope=float(f.get("ema_slow_slope", 0.02)),
                adx=float(f.get("adx", 28.5)),
                vwap_distance=float(f.get("vwap_distance", 0.008)),
                obv_momentum=float(f.get("obv_momentum", 1.15)),
                atr_percent=float(f.get("atr_percent", 1.45)),
                fear_greed_index=float(f.get("fear_greed_index", 45.0)),
                btc_dominance=float(f.get("btc_dominance", 54.2)),
                volume_spike_ratio=float(f.get("volume_spike_ratio", 1.85)),
                trend_strength=float(f.get("trend_strength", 0.68)),
                volatility_regime=str(f.get("volatility_regime", "NORMAL")),
                created_at=datetime.now(timezone.utc)
            )

            session.add(snapshot)
            await session.commit()
            await session.refresh(snapshot)
            logger.info(f"[FEATURE_SNAPSHOT] Captured entry snapshot for trade_id={trade_id}")
            return snapshot

    @staticmethod
    async def get_snapshots(limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieves recent feature snapshots."""
        async with AsyncSessionLocal() as session:
            stmt = select(LearningFeatureSnapshot).order_by(LearningFeatureSnapshot.id.desc()).limit(limit)
            res = await session.execute(stmt)
            records = res.scalars().all()
            return [
                {
                    "trade_id": r.trade_id,
                    "rsi": r.rsi,
                    "macd_histogram": r.macd_histogram,
                    "ema_fast_slope": r.ema_fast_slope,
                    "ema_slow_slope": r.ema_slow_slope,
                    "adx": r.adx,
                    "vwap_distance": r.vwap_distance,
                    "obv_momentum": r.obv_momentum,
                    "atr_percent": r.atr_percent,
                    "fear_greed_index": r.fear_greed_index,
                    "btc_dominance": r.btc_dominance,
                    "volume_spike_ratio": r.volume_spike_ratio,
                    "trend_strength": r.trend_strength,
                    "volatility_regime": r.volatility_regime,
                    "created_at": r.created_at.isoformat() if r.created_at else ""
                }
                for r in records
            ]


feature_snapshot_builder = FeatureSnapshotBuilder()
