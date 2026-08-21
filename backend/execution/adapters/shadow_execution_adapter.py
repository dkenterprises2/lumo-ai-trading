import time
from typing import Dict, Any
from backend.execution.execution_intent import ExecutionIntent
from .execution_adapter import ExecutionAdapter, ExecutionReceipt

class ShadowExecutionAdapter(ExecutionAdapter):
    """Shadow Execution Adapter for passive evaluation against real market feeds."""

    def get_adapter_type(self) -> str:
        return "SHADOW"

    def validate_intent(self, intent: ExecutionIntent) -> Dict[str, Any]:
        if intent.quantity <= 0.0:
            return {"passed": False, "reason": "Quantity must be greater than 0"}
        return {"passed": True, "reason": "VALIDATED"}

    def execute(self, intent: ExecutionIntent) -> ExecutionReceipt:
        ref_price = intent.target_price if intent.target_price > 0 else (intent.limit_price or 50000.0)
        notional_usd = round(intent.quantity * ref_price, 2)
        fee_usd = round(notional_usd * 0.00075, 4)

        return ExecutionReceipt(
            execution_intent_id=intent.execution_intent_id,
            status="FILLED",
            symbol=intent.symbol,
            side=intent.side.upper(),
            executed_quantity=round(intent.quantity, 6),
            average_fill_price=round(ref_price, 4),
            executed_notional_usd=notional_usd,
            fees_usd=fee_usd,
            slippage_usd=0.0,
            execution_latency_ms=12.5,
            execution_mode="SHADOW",
            exchange="SHADOW_BINANCE",
            exchange_order_id=f"SHADOW-{intent.execution_intent_id}",
            raw_exchange_response={"shadow_recorded": True},
            timestamp=time.time()
        )

    def dry_run(self, intent: ExecutionIntent) -> ExecutionReceipt:
        receipt = self.execute(intent)
        receipt.status = "DRY_RUN_VALIDATED"
        receipt.execution_mode = "DRY_RUN"
        return receipt
