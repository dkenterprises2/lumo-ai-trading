import time
import logging
from typing import Dict, List, Any, Optional

from .autonomous_state_machine import EngineState
from .autonomous_execution_manager import AutonomousExecutionManager
from .autonomous_metrics import AutonomousMetricsTracker
from backend.arbitrage import CrossExchangeArbitrageEngine
from backend.safety.paper_mode_guard import paper_guard
from backend.shadow_trading.shadow_safety_guard import shadow_guard

logger = logging.getLogger("autonomous_engine")

class AutonomousEngine:
    """Master Autonomous Shadow Trading Engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutonomousEngine, cls).__new__(cls)
            cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        self.state = EngineState.STOPPED
        self.arb_scanner = CrossExchangeArbitrageEngine()
        self.execution_manager = AutonomousExecutionManager()
        self.metrics_tracker = AutonomousMetricsTracker()
        self.start_timestamp: Optional[float] = None
        self.last_scan_timestamp: Optional[float] = None

    def get_status(self) -> Dict[str, Any]:
        return {
            "mode": "AUTONOMOUS_SHADOW",
            "status": self.state.value,
            "paper_mode": paper_guard.paper_mode,
            "shadow_mode": shadow_guard.shadow_mode,
            "live_execution": False,
            "active_positions_count": len([p for p in self.execution_manager.positions.values() if p.status in ["OPEN", "MONITORING"]]),
            "start_timestamp": self.start_timestamp,
            "last_scan_timestamp": self.last_scan_timestamp
        }

    def start(self) -> Dict[str, Any]:
        if self.state in [EngineState.RUNNING, EngineState.STARTING]:
            return {"status": "success", "message": "Autonomous engine is already running", "engine_state": self.state.value}

        self.state = EngineState.STARTING
        paper_guard.assert_paper_mode("Autonomous Engine Start")
        self.start_timestamp = time.time()
        self.state = EngineState.RUNNING

        # Perform initial scan tick
        scan_res = self.run_single_tick()

        return {
            "status": "success",
            "message": "Autonomous Shadow Engine ACTIVATED",
            "engine_state": self.state.value,
            "initial_tick": scan_res
        }

    def pause(self) -> Dict[str, Any]:
        if self.state != EngineState.RUNNING:
            return {"status": "error", "message": f"Cannot pause engine in state {self.state.value}"}
        self.state = EngineState.PAUSED
        return {"status": "success", "message": "Autonomous engine PAUSED", "engine_state": self.state.value}

    def resume(self) -> Dict[str, Any]:
        if self.state != EngineState.PAUSED:
            return {"status": "error", "message": f"Cannot resume engine from state {self.state.value}"}
        self.state = EngineState.RUNNING
        return {"status": "success", "message": "Autonomous engine RESUMED", "engine_state": self.state.value}

    def stop(self) -> Dict[str, Any]:
        self.state = EngineState.STOPPING
        # Close any open positions cleanly
        self.execution_manager.monitor_and_close_positions()
        self.state = EngineState.STOPPED
        return {"status": "success", "message": "Autonomous engine STOPPED", "engine_state": self.state.value}

    def run_single_tick(self, symbol: str = "BTC/USDT") -> Dict[str, Any]:
        """Runs a single autonomous scanning, execution, and position monitoring tick."""
        if self.state != EngineState.RUNNING:
            return {"status": "ignored", "reason": f"Engine is not in RUNNING state (current state: {self.state.value})"}

        self.last_scan_timestamp = time.time()

        # 1. Scan real market opportunities
        opps = self.arb_scanner.scan_opportunities(symbol=symbol)

        results = []
        if len(opps) == 0:
            message = "NO EXECUTABLE OPPORTUNITY AVAILABLE DURING TEST WINDOW"
        else:
            for opp in opps:
                res = self.execution_manager.process_opportunity(opp.to_dict())
                results.append(res)
            message = f"Processed {len(opps)} opportunities"

        # 2. Monitor open positions & evaluate exit triggers
        closed = self.execution_manager.monitor_and_close_positions()

        return {
            "status": "success",
            "opportunities_found": len(opps),
            "message": message,
            "processed_executions": results,
            "positions_closed_this_tick": len(closed)
        }

    def get_metrics(self) -> Dict[str, Any]:
        return self.metrics_tracker.get_summary().to_dict()

    def get_executions(self) -> List[Dict[str, Any]]:
        return [e.to_dict() for e in self.execution_manager.executions.values()]

# Global Singleton Engine
autonomous_engine = AutonomousEngine()
