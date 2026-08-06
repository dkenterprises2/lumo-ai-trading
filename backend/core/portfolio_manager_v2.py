from typing import Dict, Any, List, Optional
from backend.core.logger import logger

class MultiPortfolioManager:
    """Multi-Portfolio Subsystem managing isolated portfolios per user."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MultiPortfolioManager, cls).__new__(cls)
            cls._instance._init_manager()
        return cls._instance

    def _init_manager(self):
        # user_id -> portfolio_id -> dict
        self.portfolios: Dict[int, Dict[str, Dict[str, Any]]] = {}

    def create_portfolio(self, user_id: int, name: str, portfolio_type: str = "SPOT", initial_balance: float = 10000.0) -> Dict[str, Any]:
        p_id = f"PORT_{portfolio_type}_{name.upper().replace(' ', '_')}"
        if user_id not in self.portfolios:
            self.portfolios[user_id] = {}

        p_info = {
            "id": p_id,
            "user_id": user_id,
            "name": name,
            "type": portfolio_type,
            "balance": initial_balance,
            "equity": initial_balance,
            "pnl_usd": 0.0,
            "pnl_pct": 0.0,
            "allocation_pct": 20.0
        }
        self.portfolios[user_id][p_id] = p_info
        logger.info(f"[PORTFOLIO_V2] Created portfolio {p_id} for user {user_id}.")
        return p_info

    def get_user_portfolios(self, user_id: int) -> List[Dict[str, Any]]:
        if user_id not in self.portfolios:
            self.create_portfolio(user_id, "Paper Trading", "PAPER", 10000.0)
            self.create_portfolio(user_id, "Spot Multi-Factor", "SPOT", 25000.0)
        return list(self.portfolios[user_id].values())

    def get_aggregate_summary(self, user_id: int) -> Dict[str, Any]:
        ports = self.get_user_portfolios(user_id)
        total_worth = sum(p["equity"] for p in ports)
        return {
            "user_id": user_id,
            "portfolios": ports,
            "total_net_worth": round(total_worth, 2)
        }

multi_portfolio_manager = MultiPortfolioManager()
