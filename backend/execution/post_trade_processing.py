from typing import Dict, Any, Optional
from .order_models import OMSOrder, OMSFill
from .execution_cost_engine import ExecutionCostEngine

class PostTradeProcessingEngine:
    def __init__(self):
        self.cost_engine = ExecutionCostEngine()

    def process_completed_order(
        self,
        order: OMSOrder,
        expected_price: float,
        total_fee_usd: float = 0.0
    ) -> Dict[str, Any]:
        cost_analysis = self.cost_engine.compute_cost_analysis(
            order_id=order.order_id,
            expected_price=expected_price,
            actual_average_fill=order.average_fill_price,
            quantity=order.filled_quantity,
            side=order.side,
            fee_usd=total_fee_usd
        )
        return {
            "order_id": order.order_id,
            "status": order.status,
            "cost_analysis": cost_analysis.to_dict()
        }
