import time
from typing import Dict, Any, List

class OrderManagementSystem:
    """Institutional OMS Order Lifecycle Engine."""

    VALID_STATES = [
        "CREATED", "VALIDATED", "RISK_APPROVED", "ROUTED",
        "PARTIALLY_FILLED", "FILLED", "CANCELLED", "REJECTED", "EXPIRED"
    ]

    def __init__(self):
        self._orders: List[Dict[str, Any]] = [
            {
                "order_id": "ord_p23_101",
                "symbol": "BTCUSDT",
                "side": "BUY",
                "quantity": 2.5,
                "price": 64800.0,
                "status": "FILLED",
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
            }
        ]

    def create_order(self, symbol: str, side: str, quantity: float, price: float) -> Dict[str, Any]:
        order = {
            "order_id": f"ord_{int(time.time())}",
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "price": price,
            "status": "CREATED",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        }
        self._orders.append(order)
        return order

    def list_orders(self) -> List[Dict[str, Any]]:
        return self._orders

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        return {"order_id": order_id, "status": "CANCELLED"}

oms_engine = OrderManagementSystem()
