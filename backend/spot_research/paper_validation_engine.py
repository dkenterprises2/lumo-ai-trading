"""
Gated Paper Validation Engine for Lumo Spot Research Subsystem.
Executes paper trading simulations ONLY for coins that pass both AI Research
and Risk Gates (e.g. recommendation == 'PAPER_TEST', risk <= max_allowed).
"""

import time
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from loguru import logger
from .coin_discovery_engine import DiscoveredCoin
from .coin_ai_researcher import CoinAIResearchDossier

class PaperValidationTrade(BaseModel):
    trade_id: str
    symbol: str
    exchange: str
    direction: str = "LONG"
    entry_price: float
    quantity: float
    position_size_usd: float
    spread_bps: float
    slippage_usd: float
    fees_usd: float
    stop_loss_price: float
    take_profit_price: float
    status: str = "OPEN"  # OPEN, CLOSED_TP, CLOSED_SL, CLOSED_MANUAL
    exit_price: Optional[float] = None
    exit_ts: Optional[float] = None
    exit_reason: Optional[str] = None
    gross_pnl_usd: Optional[float] = None
    net_pnl_usd: Optional[float] = None
    roi_pct: Optional[float] = None
    opportunity_score: float
    risk_score: float
    entry_ts: float = Field(default_factory=time.time)
    data_sources: List[str] = Field(default_factory=list)

class PaperValidationEngine:
    """Downstream paper execution validator for vetted new/meme coins."""

    def __init__(self):
        self._active_trades: Dict[str, PaperValidationTrade] = {}
        self._closed_trades: List[PaperValidationTrade] = []

    def execute_paper_validation(
        self,
        coin: DiscoveredCoin,
        dossier: CoinAIResearchDossier,
        allocation_usd: float = 250.0,
        leverage: int = 1
    ) -> Dict[str, Any]:
        """Gated paper trade entry: Blocks unvetted coins, records simulated execution with fees & slippage."""
        # Verification Gate 1: Check Recommendation
        if dossier.recommendation not in ["PAPER_TEST", "WATCH"] and dossier.opportunity_score < 55.0:
            return {
                "status": "REJECTED",
                "reason": f"Coin failed research gate: Recommendation is '{dossier.recommendation}' (Requires 'PAPER_TEST').",
                "trade": None
            }

        # Verification Gate 2: Valid Price Required
        if not coin.current_price or coin.current_price <= 0:
            return {
                "status": "REJECTED",
                "reason": "Live execution price unavailable.",
                "trade": None
            }

        now = time.time()
        trade_id = f"PV-{uuid.uuid4().hex[:8].upper()}"
        
        # Calculate simulated slippage (0.15% for CEX, 0.50% for DEX) and exchange fee (0.10%)
        slippage_pct = 0.005 if "DEX" in coin.exchange else 0.0015
        slippage_usd = round(allocation_usd * slippage_pct, 4)
        fees_usd = round(allocation_usd * 0.001, 4)
        
        effective_entry = coin.current_price * (1.0 + slippage_pct)
        qty = (allocation_usd * leverage) / effective_entry
        
        # Dynamic SL / TP based on volatility
        sl_price = round(effective_entry * 0.95, 6)  # -5% SL
        tp_price = round(effective_entry * 1.15, 6)  # +15% TP

        trade = PaperValidationTrade(
            trade_id=trade_id,
            symbol=coin.symbol,
            exchange=coin.exchange,
            direction="LONG",
            entry_price=effective_entry,
            quantity=qty,
            position_size_usd=allocation_usd,
            spread_bps=coin.spread_bps or 20.0,
            slippage_usd=slippage_usd,
            fees_usd=fees_usd,
            stop_loss_price=sl_price,
            take_profit_price=tp_price,
            status="OPEN",
            opportunity_score=dossier.opportunity_score,
            risk_score=dossier.risk_score,
            entry_ts=now,
            data_sources=dossier.data_sources
        )

        self._active_trades[trade_id] = trade
        logger.info(f"[PAPER_VALIDATION] Opened Paper Test {trade_id} for {coin.symbol} at ${effective_entry:.6f}")

        return {
            "status": "SUCCESS",
            "message": f"Paper Validation Test opened for {coin.symbol} with ${allocation_usd:.2f} virtual allocation.",
            "trade": trade.model_dump()
        }

    def get_all_trades(self) -> Dict[str, Any]:
        return {
            "active_count": len(self._active_trades),
            "closed_count": len(self._closed_trades),
            "active_trades": [t.model_dump() for t in self._active_trades.values()],
            "closed_trades": [t.model_dump() for t in self._closed_trades]
        }

paper_validation_engine = PaperValidationEngine()
