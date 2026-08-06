import time
import asyncio
from typing import Dict, Any, Optional, List
from backend.plugins.strategy_registry import strategy_registry, BaseStrategyPlugin
from backend.core.logger import logger

class StrategyInstance:
    """Represents a scheduled strategy runtime instance."""
    def __init__(self, strategy_id: str, priority: int = 1, allocation_pct: float = 12.5):
        self.strategy_id = strategy_id
        self.plugin: Optional[BaseStrategyPlugin] = strategy_registry.get_strategy(strategy_id)
        self.priority = priority
        self.allocation_pct = allocation_pct
        self.state = "RUNNING"  # INITIALIZED, RUNNING, PAUSED, STOPPED, ERROR
        self.last_run_time = time.time()
        self.error_count = 0

class StrategyOrchestrator:
    """Strategy Manager & Scheduler orchestrating parallel strategy lifecycles."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StrategyOrchestrator, cls).__new__(cls)
            cls._instance._init_orchestrator()
        return cls._instance

    def _init_orchestrator(self):
        # user_id -> strategy_id -> StrategyInstance
        self.user_strategies: Dict[int, Dict[str, StrategyInstance]] = {}

    def get_user_strategies(self, user_id: int) -> List[Dict[str, Any]]:
        if user_id not in self.user_strategies:
            self._initialize_user_default_strategies(user_id)

        instances = self.user_strategies[user_id]
        res = []
        for s_id, inst in instances.items():
            if inst.plugin:
                res.append({
                    "strategy_id": s_id,
                    "name": inst.plugin.name,
                    "state": inst.state,
                    "priority": inst.priority,
                    "allocation_pct": inst.allocation_pct,
                    "risk_level": inst.plugin.risk_level,
                    "health": "HEALTHY" if inst.error_count == 0 else "DEGRADED"
                })
        return res

    def _initialize_user_default_strategies(self, user_id: int):
        self.user_strategies[user_id] = {}
        all_strats = strategy_registry.list_strategies()
        for idx, s in enumerate(all_strats):
            self.user_strategies[user_id][s["id"]] = StrategyInstance(
                strategy_id=s["id"],
                priority=idx + 1,
                allocation_pct=100.0 / len(all_strats)
            )

    def enable_strategy(self, user_id: int, strategy_id: str) -> Dict[str, Any]:
        if user_id not in self.user_strategies:
            self._initialize_user_default_strategies(user_id)
        if strategy_id in self.user_strategies[user_id]:
            self.user_strategies[user_id][strategy_id].state = "RUNNING"
            logger.info(f"[ORCHESTRATOR] User {user_id} ENABLED strategy {strategy_id}.")
            return {"status": "success", "message": f"Strategy {strategy_id} enabled.", "state": "RUNNING"}
        return {"status": "error", "message": "Strategy not found."}

    def disable_strategy(self, user_id: int, strategy_id: str) -> Dict[str, Any]:
        if user_id not in self.user_strategies:
            self._initialize_user_default_strategies(user_id)
        if strategy_id in self.user_strategies[user_id]:
            self.user_strategies[user_id][strategy_id].state = "PAUSED"
            logger.info(f"[ORCHESTRATOR] User {user_id} PAUSED strategy {strategy_id}.")
            return {"status": "success", "message": f"Strategy {strategy_id} paused.", "state": "PAUSED"}
        return {"status": "error", "message": "Strategy not found."}

    def execute_all_strategies(self, user_id: int, symbol: str, market_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Run all active enabled strategies in priority order."""
        if user_id not in self.user_strategies:
            self._initialize_user_default_strategies(user_id)

        signals = []
        active_insts = sorted(
            [i for i in self.user_strategies[user_id].values() if i.state == "RUNNING"],
            key=lambda x: x.priority
        )

        for inst in active_insts:
            if inst.plugin:
                try:
                    sig = inst.plugin.generate_signal(symbol, market_data)
                    sig["allocation_pct"] = inst.allocation_pct
                    signals.append(sig)
                    inst.last_run_time = time.time()
                except Exception as e:
                    inst.error_count += 1
                    logger.error(f"Error evaluating strategy {inst.strategy_id}: {e}")

        return signals

strategy_orchestrator = StrategyOrchestrator()
