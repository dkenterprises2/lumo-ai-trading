import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class PortfolioV2Schema(BaseModel):
    """Multi-Portfolio Instance Schema."""
    portfolio_id: str
    user_id: int
    name: str
    type: str = "PAPER"  # PAPER, SPOT, FUTURES, MOMENTUM, SWING, AI_QUANT
    exchange_id: str = "PAPER"
    wallet_balance: float = 10000.0
    initial_capital: float = 10000.0
    default_allocation_usd: float = 1000.0
    default_leverage: int = 1
    is_active: bool = True
    created_at: float = Field(default_factory=time.time)

class MultiPortfolioSummary(BaseModel):
    total_portfolios: int
    aggregate_net_worth_usd: float
    portfolios: List[Dict[str, Any]]
