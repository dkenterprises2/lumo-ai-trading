from typing import Dict, Any, Optional
from .order_models import OMSOrder
from .smart_order_router import SmartOrderRouter, VenueScore

class ExecutionRouter:
    """Inter-Module Execution Router interfacing between OMS and Venue Adapters."""

    def __init__(self):
        self.sor = SmartOrderRouter()

    def route(self, order: OMSOrder, current_price: float = 50000.0) -> VenueScore:
        return self.sor.route_order(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            order_type=order.order_type,
            requested_exchange=order.exchange,
            price=current_price
        )
