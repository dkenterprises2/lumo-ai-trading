"""
Trade Outcome Collector for Phase 25 Self-Learning Feedback Loop.
Collects and persists outcome metrics for every closed trade.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import AsyncSessionLocal
from backend.models.domain import LearningTradeOutcome
from backend.core.logger import logger


class TradeOutcomeCollector:
    """Collects and stores trade outcome details upon position exit."""

    @staticmethod
    async def record_trade_outcome(trade_data: Dict[str, Any]) -> LearningTradeOutcome:
        """
        Records a completed trade outcome into learning_trade_outcomes database table.
        """
        async with AsyncSessionLocal() as session:
            trade_id = str(trade_data.get("id") or trade_data.get("trade_id") or f"TRADE_{int(datetime.now().timestamp()*1000)}")
            
            # Check if outcome already recorded
            stmt = select(LearningTradeOutcome).where(LearningTradeOutcome.trade_id == trade_id)
            res = await session.execute(stmt)
            existing = res.scalars().first()
            if existing:
                return existing

            entry_p = float(trade_data.get("entry_price", 0.0))
            exit_p = float(trade_data.get("exit_price", entry_p))
            qty = float(trade_data.get("amount", trade_data.get("quantity", 1.0)))
            side = str(trade_data.get("side", "LONG")).upper()
            fees = float(trade_data.get("exit_fee", 0.0)) + float(trade_data.get("entry_fee", 0.0))
            
            # Calculate gross and net PnL if not provided
            if "pnl_usd" in trade_data or "net_pnl" in trade_data:
                net_pnl = float(trade_data.get("net_pnl", trade_data.get("pnl_usd", 0.0)))
                gross_pnl = float(trade_data.get("gross_pnl", net_pnl + fees))
            else:
                if side == "LONG":
                    gross_pnl = (exit_p - entry_p) * qty
                else:
                    gross_pnl = (entry_p - exit_p) * qty
                net_pnl = gross_pnl - fees

            close_reason = str(trade_data.get("close_reason", "")).upper()
            stop_loss_hit = "STOP_LOSS" in close_reason or trade_data.get("stop_loss_hit", False)
            take_profit_hit = "TAKE_PROFIT" in close_reason or trade_data.get("take_profit_hit", False)
            
            holding_minutes = float(trade_data.get("holding_minutes", 15.0))

            outcome = LearningTradeOutcome(
                trade_id=trade_id,
                symbol=str(trade_data.get("symbol", "BTC/USDT")),
                side=side,
                entry_price=entry_p,
                exit_price=exit_p,
                quantity=qty,
                gross_pnl=gross_pnl,
                net_pnl=net_pnl,
                fees=fees,
                holding_minutes=holding_minutes,
                stop_loss_hit=stop_loss_hit,
                take_profit_hit=take_profit_hit,
                timestamp=datetime.now(timezone.utc),
                strategy_name=str(trade_data.get("strategy_name", trade_data.get("strategy", "AI_HYBRID"))),
                market_regime=str(trade_data.get("market_regime", "NEUTRAL"))
            )

            session.add(outcome)
            await session.commit()
            await session.refresh(outcome)
            logger.info(f"[OUTCOME_COLLECTOR] Trade outcome recorded for trade_id={trade_id} NetPnL=${net_pnl:.2f}")
            return outcome

    @staticmethod
    async def get_outcomes(limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieves recent trade outcomes."""
        async with AsyncSessionLocal() as session:
            stmt = select(LearningTradeOutcome).order_by(LearningTradeOutcome.id.desc()).limit(limit)
            res = await session.execute(stmt)
            records = res.scalars().all()
            return [
                {
                    "trade_id": r.trade_id,
                    "symbol": r.symbol,
                    "side": r.side,
                    "entry_price": r.entry_price,
                    "exit_price": r.exit_price,
                    "quantity": r.quantity,
                    "gross_pnl": r.gross_pnl,
                    "net_pnl": r.net_pnl,
                    "fees": r.fees,
                    "holding_minutes": r.holding_minutes,
                    "stop_loss_hit": r.stop_loss_hit,
                    "take_profit_hit": r.take_profit_hit,
                    "timestamp": r.timestamp.isoformat() if r.timestamp else "",
                    "strategy_name": r.strategy_name,
                    "market_regime": r.market_regime
                }
                for r in records
            ]


trade_outcome_collector = TradeOutcomeCollector()
