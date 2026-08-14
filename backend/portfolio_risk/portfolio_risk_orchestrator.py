from typing import Dict, Any, Optional
from .portfolio_risk_engine import InstitutionalPortfolioRiskEngine
from .portfolio_state import PortfolioRiskState

class PortfolioRiskOrchestrator:
    """Master Orchestrator Singleton for Portfolio Risk Systems."""

    def __init__(self):
        self.risk_engine = InstitutionalPortfolioRiskEngine()

    def get_portfolio_risk_state(self, user_trader, market_prices: Optional[Dict[str, float]] = None) -> PortfolioRiskState:
        """Fetch current portfolio risk state snapshot for user_trader."""
        return self.risk_engine.evaluate_portfolio_state(
            user_id=str(getattr(user_trader, 'user_id', 'default')),
            user_trader=user_trader,
            market_prices=market_prices
        )

    def evaluate_order_gate(
        self,
        user_trader,
        symbol: str,
        side: str,
        allocation_usd: float,
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Evaluate trade execution through Phase 34 Risk Gate."""
        return self.risk_engine.evaluate_trade_risk_gate(
            user_trader=user_trader,
            symbol=symbol,
            side=side,
            requested_allocation_usd=allocation_usd,
            requested_leverage=leverage,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )

# Global Orchestrator Singleton
portfolio_risk_orchestrator = PortfolioRiskOrchestrator()
