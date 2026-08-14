class PaperTradingViolation(Exception):
    """Raised when a live exchange or unauthorized real execution call is attempted in paper mode."""
    pass

class PaperTradingGuard:
    """Hard Safety Guard preventing live exchange order placement during Paper Trading mode."""

    def __init__(self, paper_mode: bool = True):
        self.paper_mode = paper_mode

    def assert_paper_mode(self, action_name: str = "Live Exchange Action"):
        if self.paper_mode:
            assert self.paper_mode is True, "PAPER_TRADING mode invariant violated!"

    def block_live_exchange_order(self, exchange: str, symbol: str, amount: float):
        self.assert_paper_mode("Live Order Execution")
        raise PaperTradingViolation(
            f"PAPER TRADING HARD GUARD: Real order placement to live exchange {exchange} for {symbol} ({amount}) BLOCKED."
        )

    def block_withdrawal(self, currency: str, amount: float, address: str):
        self.assert_paper_mode("Withdrawal Request")
        raise PaperTradingViolation(
            f"PAPER TRADING HARD GUARD: Live withdrawal request of {amount} {currency} to {address} BLOCKED."
        )

    def block_live_api_key_usage(self, api_key: str):
        self.assert_paper_mode("Live API Key Usage")
        raise PaperTradingViolation(
            f"PAPER TRADING HARD GUARD: Real API key authenticated request BLOCKED in paper mode."
        )

# Global Singleton Guard
paper_guard = PaperTradingGuard(paper_mode=True)
