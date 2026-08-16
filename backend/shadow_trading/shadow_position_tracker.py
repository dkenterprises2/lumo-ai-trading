import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class ShadowPosition:
    position_id: str = field(default_factory=lambda: f"SHADOW-POS-{uuid.uuid4().hex[:8].upper()}")
    symbol: str = "BTC/USDT"
    side: str = "BUY"
    quantity: float = 0.0
    average_entry_price: float = 0.0
    mark_price: float = 0.0
    unrealized_pnl_usd: float = 0.0
    realized_pnl_usd: float = 0.0
    fees_paid_usd: float = 0.0
    slippage_cost_usd: float = 0.0
    opened_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ShadowPositionTracker:
    """Independent Position Tracker for Shadow Trading (Isolated from Paper Positions)."""

    def __init__(self):
        self._positions: Dict[str, ShadowPosition] = {}

    def update_position_from_fill(self, fill_event) -> ShadowPosition:
        sym = fill_event.symbol
        pos = self._positions.get(sym)

        if not pos:
            pos = ShadowPosition(
                symbol=sym,
                side=fill_event.side,
                quantity=fill_event.filled_qty,
                average_entry_price=fill_event.execution_price,
                mark_price=fill_event.execution_price,
                fees_paid_usd=fill_event.fee_usd,
                slippage_cost_usd=fill_event.slippage_cost_usd,
                opened_at=time.time()
            )
        else:
            # Aggregate position size and average entry
            new_qty = pos.quantity + fill_event.filled_qty
            if new_qty > 0:
                avg_entry = ((pos.quantity * pos.average_entry_price) + (fill_event.filled_qty * fill_event.execution_price)) / new_qty
            else:
                avg_entry = fill_event.execution_price

            pos.quantity = round(new_qty, 6)
            pos.average_entry_price = round(avg_entry, 4)
            pos.fees_paid_usd += fill_event.fee_usd
            pos.slippage_cost_usd += fill_event.slippage_cost_usd

        self._positions[sym] = pos
        return pos

    def get_position(self, symbol: str) -> Optional[ShadowPosition]:
        return self._positions.get(symbol.upper())

    def get_all_positions(self) -> List[ShadowPosition]:
        return list(self._positions.values())

    def clear_all(self):
        self._positions.clear()
