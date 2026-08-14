import time
from typing import Dict, List, Any, Optional

from .shadow_safety_guard import shadow_guard, TradingMode
from .shadow_orderbook import ShadowOrderBook
from .shadow_fill_simulator import ShadowFillSimulator
from .shadow_execution_router import ShadowExecutionRouter
from .shadow_latency_model import ShadowLatencyModel
from .shadow_market_replay import ShadowMarketReplay
from .shadow_position_tracker import ShadowPositionTracker
from .shadow_pnl_engine import ShadowPnLEngine
from .shadow_telemetry import ShadowTelemetry
from .shadow_metrics import ShadowMetricsTracker
from .shadow_governance import ShadowGovernance

class ShadowEngine:
    """Master Institutional Shadow Trading & Market Replay Engine Singleton."""

    def __init__(self):
        self.guard = shadow_guard
        self.orderbook = ShadowOrderBook()
        self.simulator = ShadowFillSimulator()
        self.router = ShadowExecutionRouter()
        self.latency_model = ShadowLatencyModel()
        self.replay_engine = ShadowMarketReplay()
        self.position_tracker = ShadowPositionTracker()
        self.pnl_engine = ShadowPnLEngine()
        self.telemetry = ShadowTelemetry()
        self.metrics_tracker = ShadowMetricsTracker()
        self.governance = ShadowGovernance()
        self.status = "IDLE"  # IDLE, RUNNING, HALTED

    def start_shadow_session(self) -> Dict[str, Any]:
        val = self.governance.validate_shadow_approval()
        if not val.is_approved:
            return {"status": "error", "message": f"Shadow session governance validation failed: {val.reasons}"}

        self.status = "RUNNING"
        return {
            "status": "success",
            "session_status": self.status,
            "trading_mode": "SHADOW",
            "governance": val.to_dict()
        }

    def stop_shadow_session(self) -> Dict[str, Any]:
        self.status = "IDLE"
        return {"status": "success", "session_status": self.status}

    def get_status(self) -> Dict[str, Any]:
        return {
            "trading_mode": "SHADOW",
            "session_status": self.status,
            "feed_status": "LIVE",
            "safety_guard": "ACTIVE",
            "open_shadow_positions_count": len(self.position_tracker.get_all_positions())
        }

# Global Singleton Engine
shadow_engine = ShadowEngine()
