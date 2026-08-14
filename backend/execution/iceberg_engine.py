import time
import random
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class IcebergOrderState:
    iceberg_id: str
    symbol: str
    side: str
    total_quantity: float
    display_quantity: float
    filled_quantity: float
    remaining_quantity: float
    current_visible_slice_qty: float
    num_replenishments: int
    status: str = "ACTIVE"  # ACTIVE, PAUSED, COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class IcebergEngine:
    """Institutional Iceberg Order Execution Engine."""

    def create_iceberg(
        self,
        iceberg_id: str,
        symbol: str,
        side: str,
        total_quantity: float,
        display_quantity_pct: float = 10.0
    ) -> IcebergOrderState:
        """Initialize Iceberg order with hidden quantity reserve."""
        display_pct = max(1.0, min(50.0, display_quantity_pct))
        visible_qty = total_quantity * (display_pct / 100.0)

        return IcebergOrderState(
            iceberg_id=iceberg_id,
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            display_quantity=round(visible_qty, 6),
            filled_quantity=0.0,
            remaining_quantity=total_quantity,
            current_visible_slice_qty=round(visible_qty, 6),
            num_replenishments=0,
            status="ACTIVE"
        )

    def process_slice_fill(
        self,
        state: IcebergOrderState,
        fill_qty: float
    ) -> IcebergOrderState:
        """Process fill of current visible slice and replenish from hidden reserve with randomized timing."""
        f_qty = min(fill_qty, state.remaining_quantity)
        state.filled_quantity += f_qty
        state.remaining_quantity = max(0.0, state.total_quantity - state.filled_quantity)

        if state.remaining_quantity <= 0.0:
            state.status = "COMPLETED"
            state.current_visible_slice_qty = 0.0
        else:
            # Replenish visible slice
            rand_jitter = random.uniform(0.9, 1.1)
            next_visible = min(state.remaining_quantity, state.display_quantity * rand_jitter)
            state.current_visible_slice_qty = round(next_visible, 6)
            state.num_replenishments += 1

        return state
