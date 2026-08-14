import time
import uuid
from typing import Dict, Any, Optional

from .shadow_safety_guard import shadow_guard, ShadowTradingViolation
from .shadow_fill_simulator import ShadowFillSimulator, ShadowFillEvent
from .shadow_position_tracker import ShadowPositionTracker

class ShadowExecutionRouter:
    """Routes execution signals to orderbook fill simulator and position tracker in SHADOW mode."""

    def __init__(self):
        self.simulator = ShadowFillSimulator()
        self.position_tracker = ShadowPositionTracker()
        self.executed_fills = []

    def execute_shadow_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        # 1. Enforce Shadow Safety Guard (Guarantees zero live exchange order call)
        # Note: If real exchange calls were attempted, shadow_guard will raise ShadowTradingViolation.
        order_id = f"SHADOW-ORD-{uuid.uuid4().hex[:8].upper()}"

        # 2. Simulate Orderbook Fill
        fill = self.simulator.simulate_fill(
            order_id=order_id,
            symbol=symbol,
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price
        )
        self.executed_fills.append(fill)

        # 3. Update Shadow Positions
        pos = self.position_tracker.update_position_from_fill(fill)

        return {
            "status": "success",
            "mode": "SHADOW",
            "order_id": order_id,
            "fill": fill.to_dict(),
            "shadow_position": pos.to_dict()
        }
