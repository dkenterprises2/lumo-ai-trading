from enum import Enum
from typing import Dict, Any, Optional
import time

class TradingMode(str, Enum):
    PAPER = "PAPER"
    SHADOW = "SHADOW"
    LIVE = "LIVE"

class ShadowTradingViolation(Exception):
    """Raised when a live exchange execution or unauthorized live API call is attempted in SHADOW mode."""
    pass

class ShadowSafetyGuard:
    """Absolute live-order prevention guard for Shadow Trading mode."""

    def __init__(self, mode: TradingMode = TradingMode.SHADOW):
        self.mode = mode
        self.blocked_attempts_log = []

    def assert_shadow_safety(self, action_name: str = "Live Exchange Order"):
        """Raise exception if real exchange order or withdrawal is attempted in SHADOW mode."""
        if self.mode == TradingMode.SHADOW:
            event = {
                "action": action_name,
                "timestamp": time.time(),
                "blocked": True,
                "mode": self.mode.value
            }
            self.blocked_attempts_log.append(event)
            raise ShadowTradingViolation(
                f"SHADOW SAFETY GUARD: Real exchange order submission ({action_name}) is strictly FORBIDDEN in {self.mode.value} mode!"
            )

    def block_ccxt_create_order(self, symbol: str, side: str, amount: float):
        self.assert_shadow_safety(f"CCXT create_order for {symbol} {side} {amount}")

    def block_withdrawal(self, currency: str, amount: float):
        self.assert_shadow_safety(f"Exchange Withdrawal of {amount} {currency}")

    def block_leverage_change(self, symbol: str, leverage: int):
        self.assert_shadow_safety(f"Margin leverage modification ({leverage}x for {symbol})")

    def block_authenticated_ws(self):
        self.assert_shadow_safety("Authenticated Exchange Trading WebSocket Channel")

# Global Singleton Guard
shadow_guard = ShadowSafetyGuard(mode=TradingMode.SHADOW)
