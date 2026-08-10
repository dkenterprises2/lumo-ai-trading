"""
Strategy Weight Loader for Phase 25 Self-Learning Feedback Loop.
Manages in-memory TTL cached strategy weights, hot reloading every 60 seconds,
and instant 1-second rollbacks across the last 10 weight versions.
"""

import time
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select, update

from backend.database.session import AsyncSessionLocal
from backend.models.domain import ActiveStrategyWeights, AuditLogModel
from backend.core.logger import logger


DEFAULT_STRATEGY_WEIGHTS = {
    "ema_weight": 0.25,
    "rsi_weight": 0.15,
    "macd_weight": 0.25,
    "adx_weight": 0.10,
    "vwap_weight": 0.10,
    "obv_weight": 0.08,
    "sentiment_weight": 0.07
}


class StrategyWeightLoader:
    """Dynamic weight loader with 60s TTL cache and instant rollback."""

    def __init__(self, cache_ttl_seconds: float = 60.0):
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp: Dict[str, float] = {}

    async def get_active_weights(self, strategy_name: str = "AI_HYBRID", market_regime: str = "NEUTRAL") -> Dict[str, float]:
        """
        Retrieves active strategy weights with 60-second TTL in-memory caching.
        """
        cache_key = f"{strategy_name}_{market_regime}"
        now = time.time()

        if cache_key in self._cache and (now - self._cache_timestamp.get(cache_key, 0)) < self.cache_ttl_seconds:
            return self._cache[cache_key]

        weights = await self._load_from_db(strategy_name, market_regime)
        self._cache[cache_key] = weights
        self._cache_timestamp[cache_key] = now
        return weights

    def get_active_weights_sync(self, strategy_name: str = "AI_HYBRID", market_regime: str = "NEUTRAL") -> Dict[str, float]:
        """Synchronous cache accessor for active strategy weights."""
        cache_key = f"{strategy_name}_{market_regime}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        return DEFAULT_STRATEGY_WEIGHTS.copy()


    async def _load_from_db(self, strategy_name: str, market_regime: str) -> Dict[str, float]:
        """Loads active weights from database or returns defaults."""
        try:
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(ActiveStrategyWeights)
                    .where(
                        ActiveStrategyWeights.strategy_name == strategy_name,
                        ActiveStrategyWeights.is_active == True
                    )
                    .order_by(ActiveStrategyWeights.version.desc())
                )
                res = await session.execute(stmt)
                active = res.scalars().first()

                if active and active.weights_json:
                    parsed = json.loads(active.weights_json)
                    return {k: float(v) for k, v in parsed.items()}
        except Exception as e:
            logger.warning(f"[WEIGHT_LOADER] Error loading weights from DB: {e}. Falling back to default weights.")

        return DEFAULT_STRATEGY_WEIGHTS.copy()

    async def reload_weights(self, strategy_name: str = "AI_HYBRID", market_regime: str = "NEUTRAL") -> Dict[str, float]:
        """Forces an immediate hot-reload of weights into cache."""
        cache_key = f"{strategy_name}_{market_regime}"
        weights = await self._load_from_db(strategy_name, market_regime)
        self._cache[cache_key] = weights
        self._cache_timestamp[cache_key] = time.time()
        logger.info(f"[WEIGHT_LOADER] Hot-reloaded weights for {cache_key}: {weights}")
        return weights

    async def rollback_to_version(self, version: int, strategy_name: str = "AI_HYBRID", market_regime: str = "NEUTRAL") -> Dict[str, Any]:
        """
        Instantly rolls back active weights to a target historical version (< 1 second execution).
        """
        async with AsyncSessionLocal() as session:
            stmt = select(ActiveStrategyWeights).where(
                ActiveStrategyWeights.strategy_name == strategy_name,
                ActiveStrategyWeights.version == version
            )
            res = await session.execute(stmt)
            target_weights = res.scalars().first()

            if not target_weights:
                return {"status": "error", "message": f"Version {version} not found for strategy {strategy_name}"}

            # Deactivate all versions for this strategy & regime
            await session.execute(
                update(ActiveStrategyWeights)
                .where(ActiveStrategyWeights.strategy_name == strategy_name)
                .values(is_active=False)
            )

            # Activate target version
            target_weights.is_active = True

            # Add to audit log
            audit = AuditLogModel(
                event_type="STRATEGY_WEIGHT_ROLLBACK",
                details=f"Rolled back strategy {strategy_name} to version {version}. Deployed by System Rollback."
            )
            session.add(audit)

            await session.commit()

        # Force immediate hot reload
        reloaded = await self.reload_weights(strategy_name, market_regime)

        logger.info(f"[WEIGHT_ROLLBACK] Successfully rolled back strategy {strategy_name} to version {version}")
        return {
            "status": "success",
            "strategy_name": strategy_name,
            "version": version,
            "weights": reloaded,
            "message": f"Strategy weights instantly rolled back to version {version}"
        }

    async def get_version_history(self, strategy_name: str = "AI_HYBRID", limit: int = 10) -> List[Dict[str, Any]]:
        """Gets last 10 weight versions for instant rollback selection."""
        async with AsyncSessionLocal() as session:
            stmt = (
                select(ActiveStrategyWeights)
                .where(ActiveStrategyWeights.strategy_name == strategy_name)
                .order_by(ActiveStrategyWeights.version.desc())
                .limit(limit)
            )
            res = await session.execute(stmt)
            records = res.scalars().all()
            return [
                {
                    "version": r.version,
                    "strategy_name": r.strategy_name,
                    "market_regime": r.market_regime,
                    "is_active": r.is_active,
                    "weights": json.loads(r.weights_json) if r.weights_json else {},
                    "deployed_by": r.deployed_by,
                    "created_at": r.created_at.isoformat() if r.created_at else ""
                }
                for r in records
            ]


strategy_weight_loader = StrategyWeightLoader()
