from typing import Dict, Any, Optional
from .order_models import OMSOrder

class OrderValidationEngine:
    def validate_order(self, order: OMSOrder) -> Dict[str, Any]:
        if order.quantity <= 0:
            return {"valid": False, "reason": "Order quantity must be positive"}
        if order.side.upper() not in ["BUY", "SELL", "LONG", "SHORT"]:
            return {"valid": False, "reason": f"Unsupported order side: {order.side}"}
        return {"valid": True, "reason": "Order validated successfully"}
