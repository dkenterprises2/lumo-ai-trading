import time
from typing import Dict, Any, Optional
from .order_models import OMSOrder, OMSFill

class FillEngine:
    """Core Execution Fill Engine executing order fills."""

    def execute_fill(
        self,
        order: OMSOrder,
        fill_price: float,
        fill_quantity: float,
        liquidity_flag: str = "TAKER"
    ) -> OMSFill:
        """Generate fill event for target order."""
        actual_qty = min(fill_quantity, order.remaining_quantity)
        fee = actual_qty * fill_price * 0.00075  # 7.5 bps default fee

        fill = OMSFill(
            order_id=order.order_id,
            fill_price=fill_price,
            fill_quantity=actual_qty,
            fee=round(fee, 4),
            liquidity_flag=liquidity_flag,
            exchange=order.exchange,
            timestamp=time.time()
        )
        return fill
