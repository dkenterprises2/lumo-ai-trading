from typing import Dict, Any, Optional
from .order_models import OMSOrder
from .slippage_engine import SlippageEngine

class PreTradeChecksEngine:
    def __init__(self):
        self.slippage_engine = SlippageEngine()

    def run_pre_trade_checks(
        self,
        order: OMSOrder,
        current_price: float = 50000.0,
        max_slippage_allowed_pct: float = 0.50
    ) -> Dict[str, Any]:
        slip_res = self.slippage_engine.estimate_slippage(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=current_price
        )

        if slip_res.action == "BLOCK" or slip_res.estimated_slippage_pct > max_slippage_allowed_pct:
            return {
                "passed": False,
                "reason": slip_res.reason,
                "slippage": slip_res.to_dict()
            }

        return {
            "passed": True,
            "reason": "Pre-trade checks passed cleanly",
            "slippage": slip_res.to_dict()
        }
