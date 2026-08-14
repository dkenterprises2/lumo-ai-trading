import time
from typing import Dict, Any, Optional

class ExecutionTelemetry:
    """Formatter for real-time WebSocket telemetry payloads."""

    def format_execution_update(
        self,
        order_id: str,
        status: str,
        filled_qty: float,
        remaining_qty: float,
        avg_fill_price: float,
        exchange: str
    ) -> Dict[str, Any]:
        """Format real-time execution update payload."""
        return {
            "type": "execution_update",
            "order_id": order_id,
            "status": status,
            "filled_qty": round(filled_qty, 6),
            "remaining_qty": round(remaining_qty, 6),
            "avg_fill_price": round(avg_fill_price, 4),
            "exchange": exchange,
            "timestamp": time.time()
        }

    def format_slippage_warning(self, order_id: str, estimated_slippage_pct: float, action: str) -> Dict[str, Any]:
        return {
            "type": "slippage_warning",
            "order_id": order_id,
            "estimated_slippage_pct": estimated_slippage_pct,
            "action": action,
            "timestamp": time.time()
        }
