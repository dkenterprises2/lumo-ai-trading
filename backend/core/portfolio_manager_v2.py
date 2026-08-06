import time
from typing import Dict, Any, List, Optional
from backend.models.portfolio_v2 import PortfolioV2Schema, MultiPortfolioSummary
from backend.core.logger import logger

class MultiPortfolioManager:
    """Manager supporting multi-portfolio creation, isolated accounting, and risk profiles per user."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultiPortfolioManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        # user_id -> portfolio_id -> PortfolioV2Schema
        self.user_portfolios: Dict[int, Dict[str, PortfolioV2Schema]] = {}

    def get_portfolios_for_user(self, user_id: int) -> List[PortfolioV2Schema]:
        """Fetch all portfolios configured for user_id."""
        if user_id not in self.user_portfolios:
            # Seed default PAPER portfolio for user
            default_p = PortfolioV2Schema(
                portfolio_id=f"PORT_{user_id}_PAPER",
                user_id=user_id,
                name="Default Paper Portfolio",
                type="PAPER",
                exchange_id="PAPER",
                wallet_balance=10000.0,
                initial_capital=10000.0
            )
            self.user_portfolios[user_id] = {default_p.portfolio_id: default_p}
        return list(self.user_portfolios[user_id].values())

    def create_portfolio(
        self,
        user_id: int,
        name: str,
        portfolio_type: str = "SPOT",
        exchange_id: str = "BINANCE_SPOT",
        initial_capital: float = 10000.0,
        allocation_usd: float = 1000.0,
        leverage: int = 1
    ) -> PortfolioV2Schema:
        """Create and register new isolated portfolio for user."""
        portfolios = self.get_portfolios_for_user(user_id)
        p_id = f"PORT_{user_id}_{portfolio_type.upper()}_{int(time.time())}"

        new_p = PortfolioV2Schema(
            portfolio_id=p_id,
            user_id=user_id,
            name=name,
            type=portfolio_type.upper(),
            exchange_id=exchange_id.upper(),
            wallet_balance=initial_capital,
            initial_capital=initial_capital,
            default_allocation_usd=allocation_usd,
            default_leverage=leverage
        )

        self.user_portfolios[user_id][p_id] = new_p
        logger.info(f"[MULTI_PORTFOLIO] User {user_id} created new portfolio {p_id} ({name}).")
        return new_p

    def get_aggregate_summary(self, user_id: int) -> Dict[str, Any]:
        """Compute aggregate multi-portfolio net worth and breakdown."""
        portfolios = self.get_portfolios_for_user(user_id)
        total_balance = sum(p.wallet_balance for p in portfolios)

        return {
            "total_portfolios": len(portfolios),
            "aggregate_net_worth_usd": round(total_balance, 2),
            "portfolios": [p.dict() for p in portfolios]
        }

multi_portfolio_manager = MultiPortfolioManager()
