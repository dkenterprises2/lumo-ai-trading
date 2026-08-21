import time
from typing import Dict, Any
from loguru import logger

from backend.arbitrage.arbitrage_intent import ArbitrageExecutionIntent
from backend.exchange.credential_manager import credential_manager
from backend.safety.paper_mode_guard import paper_guard, PaperTradingViolation
from backend.execution.kill_switch import emergency_kill_switch

class LiveArbitrageAdapter:
    """Live Cross-Exchange Arbitrage Execution Adapter with Dry-Run support."""

    def format_dual_leg_payloads(self, intent: ArbitrageExecutionIntent) -> Dict[str, Any]:
        """Format simultaneous dual-leg REST order payloads for both exchanges."""
        symbol_clean = intent.symbol.replace("/", "").upper()
        now_ts = int(time.time() * 1000)

        leg1_buy = {
            "exchange": intent.buy_exchange.upper(),
            "symbol": symbol_clean,
            "side": "BUY",
            "type": "MARKET",
            "quantity": f"{intent.executable_quantity:.6f}",
            "newClientOrderId": f"LIVE-ARB-LEG1-{intent.arbitrage_intent_id}",
            "timestamp": now_ts
        }

        leg2_sell = {
            "exchange": intent.sell_exchange.upper(),
            "symbol": symbol_clean,
            "side": "SELL",
            "type": "MARKET",
            "quantity": f"{intent.executable_quantity:.6f}",
            "newClientOrderId": f"LIVE-ARB-LEG2-{intent.arbitrage_intent_id}",
            "timestamp": now_ts
        }

        return {
            "leg1_buy": leg1_buy,
            "leg2_sell": leg2_sell
        }

    def dry_run(self, intent: ArbitrageExecutionIntent) -> Dict[str, Any]:
        """Deterministic Dry-Run Validation of Dual-Leg Arbitrage Orders."""
        if intent.executable_quantity <= 0.0 or intent.executable_capacity_usd < 10.0:
            return {
                "status": "rejected",
                "reason": "Executable capacity < $10.00 min notional",
                "execution_mode": "DRY_RUN"
            }

        payloads = self.format_dual_leg_payloads(intent)
        return {
            "status": "success",
            "intent_id": intent.arbitrage_intent_id,
            "execution_mode": "DRY_RUN",
            "dry_run_validation": "SUCCESS",
            "simulated_network_calls": "SUPPRESSED_DRY_RUN",
            "payloads": payloads,
            "estimated_profit_usd": intent.expected_profit_usd,
            "timestamp": time.time()
        }

    def execute(self, intent: ArbitrageExecutionIntent, user_id: str = "1") -> Dict[str, Any]:
        """Executes dual-leg live arbitrage only when live mode is fully authorized."""
        # 1. Kill switch check
        if emergency_kill_switch.is_active:
            return {
                "status": "rejected",
                "reason": f"Emergency Kill Switch is ACTIVE: {emergency_kill_switch.activation_reason}",
                "execution_mode": "LIVE"
            }

        # 2. Immutable paper mode guard
        if paper_guard.paper_mode:
            logger.warning(f"[LIVE_ARB_BLOCKED] Attempted Live Arbitrage execution under Paper Sandbox Guard.")
            return {
                "status": "rejected",
                "reason": "LIVE_DISABLED: System is running under Paper Sandbox Guard.",
                "execution_mode": "LIVE"
            }

        # 3. Credential Activation check
        if not credential_manager.is_live_executable(user_id):
            return {
                "status": "rejected",
                "reason": "LIVE_INELIGIBLE: API credentials not configured or live trading not activated.",
                "execution_mode": "LIVE"
            }

        return self.dry_run(intent)
