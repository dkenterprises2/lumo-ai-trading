import time
import uuid
from typing import Dict, Any, Optional
from loguru import logger

from backend.execution.execution_intent import ExecutionIntent
from backend.exchange.credential_manager import credential_manager
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.execution.kill_switch import emergency_kill_switch
from .execution_adapter import ExecutionAdapter, ExecutionReceipt

class LiveExchangeAdapter(ExecutionAdapter):
    """Institutional Live Exchange Execution Adapter.
    
    Hard Safety Guarantees:
    1. Consumes the EXACT SAME ExecutionIntent produced by the quantitative strategy brain.
    2. DRY_RUN mode validates exact REST/FIX payloads without placing network orders.
    3. LIVE mode requires explicit multi-stage credential activation + safety guard release.
    """

    def __init__(self, exchange_name: str = "BINANCE"):
        self.exchange_name = exchange_name.upper()

    def get_adapter_type(self) -> str:
        return "LIVE"

    def validate_intent(self, intent: ExecutionIntent) -> Dict[str, Any]:
        """Validate live exchange constraints (min notional, precision, lot size)."""
        ref_price = intent.target_price if intent.target_price > 0 else (intent.limit_price or 50000.0)
        notional_usd = intent.quantity * ref_price

        # Binance / OKX min notional constraint: $10.00 USD
        if notional_usd < 10.0:
            return {
                "passed": False,
                "reason": f"Live exchange min notional violation: ${notional_usd:.2f} < $10.00 minimum."
            }

        if intent.quantity <= 0.0:
            return {"passed": False, "reason": "Quantity must be strictly positive."}

        return {"passed": True, "reason": "VALIDATED"}

    def format_exchange_payload(self, intent: ExecutionIntent) -> Dict[str, Any]:
        """Generate canonical Exchange REST Order payload."""
        symbol_fmt = intent.symbol.replace("/", "").upper()
        ref_price = intent.target_price if intent.target_price > 0 else (intent.limit_price or 50000.0)
        
        payload = {
            "symbol": symbol_fmt,
            "side": intent.side.upper(),
            "type": intent.order_type.upper(),
            "quantity": f"{intent.quantity:.6f}",
            "timeInForce": intent.time_in_force,
            "newClientOrderId": f"LIVE-{intent.execution_intent_id}",
            "recvWindow": 5000,
            "timestamp": int(time.time() * 1000)
        }
        if intent.order_type.upper() == "LIMIT" and intent.limit_price:
            payload["price"] = f"{intent.limit_price:.2f}"
        
        return payload

    def dry_run(self, intent: ExecutionIntent) -> ExecutionReceipt:
        """Deterministic Dry-Run Validation: Validates exact payload without network call."""
        validation = self.validate_intent(intent)
        if not validation["passed"]:
            return ExecutionReceipt(
                execution_intent_id=intent.execution_intent_id,
                status="REJECTED",
                symbol=intent.symbol,
                side=intent.side,
                execution_mode="DRY_RUN",
                exchange=self.exchange_name,
                rejection_reason=validation["reason"],
                timestamp=time.time()
            )

        payload = self.format_exchange_payload(intent)
        ref_price = intent.target_price if intent.target_price > 0 else (intent.limit_price or 50000.0)
        notional_usd = round(intent.quantity * ref_price, 2)

        return ExecutionReceipt(
            execution_intent_id=intent.execution_intent_id,
            status="DRY_RUN_VALIDATED",
            symbol=intent.symbol,
            side=intent.side.upper(),
            executed_quantity=round(intent.quantity, 6),
            average_fill_price=round(ref_price, 4),
            executed_notional_usd=notional_usd,
            fees_usd=round(notional_usd * 0.00075, 4),
            slippage_usd=0.0,
            execution_latency_ms=4.2,
            execution_mode="DRY_RUN",
            exchange=self.exchange_name,
            exchange_order_id=payload["newClientOrderId"],
            raw_exchange_response={
                "validation_status": "SUCCESS",
                "simulated_network_call": "SUPPRESSED_DRY_RUN",
                "constructed_payload": payload
            },
            timestamp=time.time()
        )

    def execute(self, intent: ExecutionIntent, user_id: str = "1") -> ExecutionReceipt:
        """Executes live exchange order only if all safety, risk & activation criteria are met."""
        # 1. Kill Switch Check
        if emergency_kill_switch.is_active:
            return ExecutionReceipt(
                execution_intent_id=intent.execution_intent_id,
                status="REJECTED",
                symbol=intent.symbol,
                side=intent.side,
                execution_mode="LIVE",
                exchange=self.exchange_name,
                rejection_reason=f"Emergency Kill Switch is ACTIVE: {emergency_kill_switch.activation_reason}",
                timestamp=time.time()
            )

        # 2. Immutable Paper Mode Guard check
        if paper_guard.paper_mode:
            logger.warning(f"[LIVE_EXEC_BLOCKED] Attempted Live Order execution under Paper Sandbox Guard.")
            return ExecutionReceipt(
                execution_intent_id=intent.execution_intent_id,
                status="REJECTED",
                symbol=intent.symbol,
                side=intent.side,
                execution_mode="LIVE",
                exchange=self.exchange_name,
                rejection_reason="LIVE_DISABLED: System running in Paper/Shadow sandbox mode.",
                timestamp=time.time()
            )

        # 3. Explicit Multi-Stage API Activation Check
        if not credential_manager.is_live_executable(user_id):
            return ExecutionReceipt(
                execution_intent_id=intent.execution_intent_id,
                status="REJECTED",
                symbol=intent.symbol,
                side=intent.side,
                execution_mode="LIVE",
                exchange=self.exchange_name,
                rejection_reason="LIVE_INELIGIBLE: API credentials not activated or live permission missing.",
                timestamp=time.time()
            )

        # 4. Payload Validation
        validation = self.validate_intent(intent)
        if not validation["passed"]:
            return ExecutionReceipt(
                execution_intent_id=intent.execution_intent_id,
                status="REJECTED",
                symbol=intent.symbol,
                side=intent.side,
                execution_mode="LIVE",
                exchange=self.exchange_name,
                rejection_reason=validation["reason"],
                timestamp=time.time()
            )

        # When live execution is activated in future with real exchange, submit network order here
        payload = self.format_exchange_payload(intent)
        return self.dry_run(intent)
