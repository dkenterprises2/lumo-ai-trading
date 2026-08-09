import time
from typing import Dict, Any, List

class OrderManagementSystemEngine:
    """Institutional Order Management System (OMS) Engine."""

    def __init__(self):
        self._orders: List[Dict[str, Any]] = [
            {
                "order_id": "OMS-PARENT-101",
                "symbol": "BTCUSDT",
                "asset_class": "CRYPTO",
                "total_quantity": 10.0,
                "allocated_quantity": 10.0,
                "child_orders_count": 2,
                "status": "ALLOCATED"
            }
        ]

    def create_order(self, symbol: str, asset_class: str, quantity: float, side: str) -> Dict[str, Any]:
        order = {
            "order_id": f"OMS-PARENT-{int(time.time())}",
            "symbol": symbol,
            "asset_class": asset_class,
            "total_quantity": quantity,
            "allocated_quantity": quantity,
            "side": side,
            "status": "CREATED"
        }
        self._orders.append(order)
        return order

    def get_order(self, order_id: str) -> Dict[str, Any]:
        for o in self._orders:
            if o["order_id"] == order_id:
                return o
        return {"order_id": order_id, "status": "NOT_FOUND"}

oms_engine = OrderManagementSystemEngine()
