from typing import Dict, List, Optional, Any
from .order_models import OMSOrder, OMSFill

class OrderRepository:
    """In-Memory and Persistent Repository for OMS Orders and Fills."""

    def __init__(self):
        self._orders: Dict[str, OMSOrder] = {}
        self._fills: Dict[str, List[OMSFill]] = {}

    def save_order(self, order: OMSOrder) -> OMSOrder:
        self._orders[order.order_id] = order
        return order

    def get_order(self, order_id: str) -> Optional[OMSOrder]:
        return self._orders.get(order_id)

    def list_orders(self, user_id: Optional[str] = None, status: Optional[str] = None) -> List[OMSOrder]:
        orders = list(self._orders.values())
        if user_id:
            orders = [o for o in orders if o.user_id == str(user_id)]
        if status:
            orders = [o for o in orders if o.status == status]
        return sorted(orders, key=lambda x: x.created_at, reverse=True)

    def save_fill(self, fill: OMSFill) -> OMSFill:
        if fill.order_id not in self._fills:
            self._fills[fill.order_id] = []
        self._fills[fill.order_id].append(fill)
        return fill

    def get_fills_for_order(self, order_id: str) -> List[OMSFill]:
        return self._fills.get(order_id, [])

    def get_all_fills(self) -> List[OMSFill]:
        result = []
        for fills in self._fills.values():
            result.extend(fills)
        return sorted(result, key=lambda x: x.timestamp, reverse=True)
