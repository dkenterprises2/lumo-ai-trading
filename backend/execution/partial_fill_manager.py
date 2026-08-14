import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional

@dataclass
class PartialFillTracker:
    order_id: str
    original_qty: float
    filled_qty: float
    remaining_qty: float
    average_fill_price: float
    fill_count: int
    last_fill_timestamp: float
    status: str  # PARTIAL, STALED, COMPLETED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class PartialFillManager:
    """Manages partial fills, weighted average price calculations, and stalled fill escalations."""

    def process_fill(
        self,
        tracker: PartialFillTracker,
        fill_qty: float,
        fill_price: float
    ) -> PartialFillTracker:
        """Update tracker state with new partial fill."""
        new_filled = tracker.filled_qty + fill_qty
        new_rem = max(0.0, tracker.original_qty - new_filled)

        # Weighted average price calculation
        total_val = (tracker.filled_qty * tracker.average_fill_price) + (fill_qty * fill_price)
        avg_price = (total_val / new_filled) if new_filled > 0 else fill_price

        tracker.filled_qty = round(new_filled, 6)
        tracker.remaining_qty = round(new_rem, 6)
        tracker.average_fill_price = round(avg_price, 4)
        tracker.fill_count += 1
        tracker.last_fill_timestamp = time.time()
        tracker.status = "COMPLETED" if new_rem <= 0.0 else "PARTIAL"

        return tracker

    def check_stalled_fill(self, tracker: PartialFillTracker, stall_timeout_seconds: float = 60.0) -> bool:
        """Return True if fill execution has stalled beyond timeout threshold."""
        if tracker.remaining_qty <= 0.0 or tracker.fill_count == 0:
            return False
        return (time.time() - tracker.last_fill_timestamp) >= stall_timeout_seconds
