import asyncio
import time
from datetime import datetime, timezone

from typing import Dict, List, Any, Optional

from sqlalchemy import select, delete, update
from backend.database.session import AsyncSessionLocal, init_db
from backend.models.domain import (
    PortfolioModel,
    PositionModel,
    OrderModel,
    TradeModel,
    SignalModel,
    AuditLogModel,
    EquityHistoryModel,
    WalletTransactionModel
)
from backend.core.logger import logger

class TraderRepository:
    def __init__(self):
        pass

    async def initialize_repository(self):
        """Ensure database tables exist on startup."""
        await init_db()

    async def load_portfolio_state(self, user_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Load portfolio balance and bot settings for specific user_id from database with retries."""
        if user_id is None:
            logger.warning("[DB_LOAD] load_portfolio_state called without user_id, returning None.")
            return None

        logger.info(f"[DB_LOAD] Attempting load_portfolio_state for user_id={user_id}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(PortfolioModel).where(PortfolioModel.user_id == user_id)

                    result = await session.execute(stmt)
                    portfolio = result.scalars().first()

                    if portfolio:
                        data = {
                            "id": portfolio.id,
                            "user_id": portfolio.user_id,
                            "usdt_balance": portfolio.usdt_balance,
                            "initial_balance": portfolio.initial_balance,
                            "margin_used": portfolio.margin_used,
                            "total_value": portfolio.total_value,
                            "auto_bot_enabled": portfolio.auto_bot_enabled,
                            "active_strategy": portfolio.active_strategy,
                            "risk_mode": portfolio.risk_mode,
                            "default_allocation_usd": getattr(portfolio, "default_allocation_usd", 1000.0),
                            "default_leverage": getattr(portfolio, "default_leverage", 1)
                        }
                        logger.info(f"[DB_LOAD] Portfolio state loaded for user_id={user_id}: {data}")
                        return data
                    else:
                        logger.info(f"[DB_LOAD] No portfolio record found in DB for user_id={user_id}.")
                        return None
            except Exception as e:
                logger.warning(f"[DB_LOAD_RETRY {attempt}/{max_retries}] Error loading portfolio state for user_id={user_id}: {e}")
                if attempt == max_retries:
                    raise RuntimeError(f"CRITICAL: Failed to load portfolio state after {max_retries} retries: {e}")
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
        return None

    async def save_portfolio_state(
        self,
        usdt_balance: float,
        initial_balance: float,
        margin_used: float,
        total_value: float,
        auto_bot_enabled: bool,
        active_strategy: str,
        risk_mode: str,
        default_allocation_usd: float = 1000.0,
        default_leverage: int = 1,
        user_id: Optional[int] = None
    ):
        """Persist portfolio balance and bot configuration for user_id to DB."""
        logger.info(f"[DB_WRITE_PORTFOLIO] Attempting save_portfolio_state for user_id={user_id}: balance=${usdt_balance}, margin=${margin_used}, total=${total_value}, default_alloc=${default_allocation_usd}, default_lev={default_leverage}x")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(PortfolioModel)
                    if user_id is not None:
                        stmt = stmt.where(PortfolioModel.user_id == user_id)
                    else:
                        stmt = stmt.limit(1)

                    result = await session.execute(stmt)
                    portfolio = result.scalars().first()
                    if not portfolio:
                        portfolio = PortfolioModel(
                            user_id=user_id,
                            usdt_balance=usdt_balance,
                            initial_balance=initial_balance,
                            margin_used=margin_used,
                            total_value=total_value,
                            auto_bot_enabled=auto_bot_enabled,
                            active_strategy=active_strategy,
                            risk_mode=risk_mode,
                            default_allocation_usd=default_allocation_usd,
                            default_leverage=default_leverage
                        )
                        session.add(portfolio)
                    else:
                        portfolio.usdt_balance = usdt_balance
                        portfolio.initial_balance = initial_balance
                        portfolio.margin_used = margin_used
                        portfolio.total_value = total_value
                        portfolio.auto_bot_enabled = auto_bot_enabled
                        portfolio.active_strategy = active_strategy
                        portfolio.risk_mode = risk_mode
                        if hasattr(portfolio, "default_allocation_usd"):
                            portfolio.default_allocation_usd = default_allocation_usd
                        if hasattr(portfolio, "default_leverage"):
                            portfolio.default_leverage = default_leverage

                    await session.commit()
                    logger.info(f"[DB_COMMIT_PORTFOLIO] Portfolio state committed successfully for user_id={user_id}.")
                    return

            except Exception as e:
                logger.warning(f"[DB_WRITE_PORTFOLIO_RETRY {attempt}/{max_retries}] Exception saving portfolio state for user_id={user_id}: {e}")
                if attempt == max_retries:
                    logger.error(f"[DB_ROLLBACK_PORTFOLIO] Error saving portfolio state after {max_retries} retries: {e}")
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def load_open_positions(self, user_id: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """Load active open positions for user_id from DB on startup."""
        if user_id is None:
            logger.warning("[DB_LOAD_POSITIONS] load_open_positions called without user_id, returning {}.")
            return {}

        logger.info(f"[DB_LOAD_POSITIONS] Attempting load_open_positions for user_id={user_id}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            positions = {}
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(PositionModel).where(PositionModel.user_id == user_id)

                    result = await session.execute(stmt)
                    db_positions = result.scalars().all()
                    for pos in db_positions:
                        positions[pos.symbol] = {
                            "id": pos.id,
                            "user_id": pos.user_id,
                            "symbol": pos.symbol,
                            "side": pos.side,
                            "entry_price": pos.entry_price,
                            "amount": pos.amount,
                            "margin_usd": pos.margin_usd,
                            "leverage": pos.leverage,
                            "order_type": pos.order_type,
                            "stop_loss_price": pos.stop_loss_price,
                            "take_profit_price": pos.take_profit_price,
                            "liquidation_price": pos.liquidation_price,
                            "trailing_stop_pct": pos.trailing_stop_pct,
                            "entry_time": pos.entry_time,
                            "reason": pos.reason
                        }
                    logger.info(f"[DB_LOAD_POSITIONS] Loaded {len(positions)} positions for user_id={user_id}: {list(positions.keys())}")
                    return positions
            except Exception as e:
                logger.warning(f"[DB_LOAD_POSITIONS_RETRY {attempt}/{max_retries}] Exception loading positions for user_id={user_id}: {e}")
                if attempt == max_retries:
                    raise RuntimeError(f"CRITICAL: Failed to load open positions from DB after {max_retries} retries: {e}")
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
        return {}

    async def save_position(self, pos: Dict[str, Any], user_id: Optional[int] = None):
        """Persist or update open position in DB for user_id."""
        effective_user_id = user_id or pos.get("user_id")
        if effective_user_id is None:
            logger.error(f"[DB_SAVE_POSITION] Unable to save position {pos.get('id')}: user_id is None!")
            return

        logger.info(f"[DB_SAVE_POSITION] Attempting save_position for ID={pos.get('id')}, symbol={pos.get('symbol')}, user_id={effective_user_id}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(PositionModel).where(
                        PositionModel.id == pos['id'],
                        PositionModel.user_id == effective_user_id
                    )

                    result = await session.execute(stmt)
                    db_pos = result.scalars().first()
                    if not db_pos:
                        db_pos = PositionModel(
                            id=pos['id'],
                            user_id=effective_user_id,
                            symbol=pos['symbol'],
                            side=pos['side'],
                            entry_price=pos['entry_price'],
                            amount=pos['amount'],
                            margin_usd=pos['margin_usd'],
                            leverage=pos['leverage'],
                            order_type=pos.get('order_type', 'MARKET'),
                            stop_loss_price=pos.get('stop_loss_price'),
                            take_profit_price=pos.get('take_profit_price'),
                            liquidation_price=pos.get('liquidation_price'),
                            trailing_stop_pct=pos.get('trailing_stop_pct'),
                            entry_time=pos.get('entry_time'),
                            reason=pos.get('reason')
                        )
                        session.add(db_pos)
                    else:
                        db_pos.amount = pos['amount']
                        db_pos.margin_usd = pos['margin_usd']
                        db_pos.stop_loss_price = pos.get('stop_loss_price')
                        db_pos.take_profit_price = pos.get('take_profit_price')
                        db_pos.trailing_stop_pct = pos.get('trailing_stop_pct')

                    await session.commit()
                    logger.info(f"[DB_COMMIT_POSITION] Saved position {pos.get('id')} for user_id={effective_user_id}.")
                    return
            except Exception as e:
                logger.warning(f"[DB_SAVE_POSITION_RETRY {attempt}/{max_retries}] Exception saving position for user_id={effective_user_id}: {e}")
                if attempt == max_retries:
                    logger.error(f"[DB_ROLLBACK_POSITION] Error saving position after {max_retries} retries: {e}")
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def delete_position(self, pos_id: str, user_id: Optional[int] = None):
        """Remove closed position from DB for user_id."""
        if user_id is None:
            logger.error(f"[DB_DELETE_POSITION] Cannot delete position {pos_id}: user_id is None!")
            return

        logger.info(f"[DB_DELETE_POSITION] Attempting delete_position for ID={pos_id}, user_id={user_id}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    stmt = select(PositionModel).where(
                        PositionModel.id == pos_id,
                        PositionModel.user_id == user_id
                    )
                    result = await session.execute(stmt)
                    db_pos = result.scalars().first()
                    if db_pos:
                        await session.delete(db_pos)
                        await session.commit()
                        logger.info(f"[DB_DELETE_POSITION] Successfully deleted position {pos_id} for user_id={user_id}.")
                    return
            except Exception as e:
                logger.warning(f"[DB_DELETE_POSITION_RETRY {attempt}/{max_retries}] Exception deleting position for user_id={user_id}: {e}")
                if attempt == max_retries:
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def load_trade_history(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load trade history logs for user_id from DB."""
        if user_id is None:
            logger.warning("[DB_LOAD_TRADES] load_trade_history called without user_id, returning [].")
            return []

        trades = []
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(TradeModel).where(TradeModel.user_id == user_id).limit(100)


                result = await session.execute(stmt)
                db_trades = result.scalars().all()
                for t in db_trades:
                    trades.append({
                        "id": t.id,
                        "user_id": t.user_id,
                        "symbol": t.symbol,
                        "side": t.side,
                        "entry_price": t.entry_price,
                        "exit_price": t.exit_price,
                        "amount": t.amount,
                        "margin_usd": t.margin_usd,
                        "pnl_usd": t.pnl_usd,
                        "pnl_pct": t.pnl_pct,
                        "entry_time": t.entry_time,
                        "exit_time": t.exit_time,
                        "close_reason": t.close_reason,
                        "status": getattr(t, "status", "CLOSED"),
                        "strategy": getattr(t, "strategy", "AI Hybrid"),
                        "confidence": getattr(t, "confidence", 75.0),
                        "reason": getattr(t, "reason", ""),
                        "exchange": getattr(t, "exchange", "PAPER_EXCHANGE"),
                        "order_id": getattr(t, "order_id", f"ORD_{t.id}"),
                        "entry_fee": getattr(t, "entry_fee", 0.0),
                        "exit_fee": getattr(t, "exit_fee", 0.0),
                        "funding_fee": getattr(t, "funding_fee", 0.0),
                        "slippage": getattr(t, "slippage", 0.0),
                        "latency": getattr(t, "latency", 0.005)
                    })
        except Exception as e:
            logger.error(f"Error loading trade history from DB for user_id={user_id}: {e}", exc_info=True)
        return trades


    async def record_trade(self, trade: Dict[str, Any], user_id: Optional[int] = None):
        """Append executed trade log to DB for user_id."""
        effective_user_id = user_id or trade.get("user_id")
        if effective_user_id is None:
            logger.error(f"[DB_RECORD_TRADE] Cannot record trade {trade.get('id')}: user_id is None!")
            return

        try:
            async with AsyncSessionLocal() as session:
                stmt = select(TradeModel).where(
                    TradeModel.id == trade['id'],
                    TradeModel.user_id == effective_user_id
                )
                result = await session.execute(stmt)
                db_trade = result.scalars().first()

                if db_trade:
                    db_trade.exit_price = trade.get('exit_price', db_trade.exit_price)
                    db_trade.pnl_usd = trade.get('pnl_usd', db_trade.pnl_usd)
                    db_trade.pnl_pct = trade.get('pnl_pct', db_trade.pnl_pct)
                    db_trade.exit_time = trade.get('exit_time', db_trade.exit_time)
                    db_trade.close_reason = trade.get('close_reason', db_trade.close_reason)
                    db_trade.exit_fee = trade.get('exit_fee', db_trade.exit_fee)
                else:
                    db_trade = TradeModel(
                        id=trade['id'],
                        user_id=effective_user_id,
                        symbol=trade['symbol'],
                        side=trade['side'],
                        entry_price=trade['entry_price'],
                        exit_price=trade.get('exit_price', 0.0),
                        amount=trade['amount'],
                        margin_usd=trade['margin_usd'],
                        pnl_usd=trade.get('pnl_usd', 0.0),
                        pnl_pct=trade.get('pnl_pct', 0.0),
                        entry_time=trade.get('entry_time') or time.strftime("%Y-%m-%d %H:%M:%S"),
                        exit_time=trade.get('exit_time') or "",

                        close_reason=trade.get('close_reason', 'OPEN'),
                        strategy=trade.get('strategy', 'AI Hybrid'),

                        confidence=trade.get('confidence', 75.0),
                        reason=trade.get('reason', ''),
                        exchange=trade.get('exchange', 'PAPER_EXCHANGE'),
                        order_id=trade.get('order_id', f"ORD_{trade['id']}"),
                        entry_fee=trade.get('entry_fee', 0.0),
                        exit_fee=trade.get('exit_fee', 0.0),
                        funding_fee=trade.get('funding_fee', 0.0),
                        slippage=trade.get('slippage', 0.0),
                        latency=trade.get('latency', 0.005),
                        created_at=datetime.now(timezone.utc)
                    )
                    session.add(db_trade)

                await session.commit()
                logger.info(f"[DB_RECORD_TRADE] Trade record {trade.get('id')} saved for user_id={effective_user_id}.")
        except Exception as e:
            logger.error(f"Error recording trade to DB for user_id={effective_user_id}: {e}", exc_info=True)


    async def load_wallet_ledger(self, limit: int = 100, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load wallet transaction ledger from DB for user_id."""
        if user_id is None:
            logger.warning("[DB_LOAD_LEDGER] load_wallet_ledger called without user_id, returning [].")
            return []

        ledger = []
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(WalletTransactionModel).where(WalletTransactionModel.user_id == user_id).order_by(WalletTransactionModel.id.asc()).limit(limit)

                result = await session.execute(stmt)
                records = result.scalars().all()
                for r in records:
                    ledger.append({
                        "id": r.id,
                        "user_id": r.user_id,
                        "tx_id": r.tx_id,
                        "timestamp": r.timestamp,
                        "tx_type": r.tx_type,
                        "amount": r.amount,
                        "balance_after": r.balance_after,
                        "reference_id": r.reference_id,
                        "description": r.description
                    })
        except Exception as e:
            logger.error(f"Error loading wallet ledger from DB for user_id={user_id}: {e}")
        return ledger

    async def record_wallet_transaction(self, tx: Dict[str, Any], user_id: Optional[int] = None):
        """Append wallet ledger transaction record to DB for user_id."""
        effective_user_id = user_id or tx.get("user_id")
        if effective_user_id is None:
            logger.error(f"[DB_RECORD_WALLET_TX] Cannot record transaction {tx.get('tx_id')}: user_id is None!")
            return

        try:
            async with AsyncSessionLocal() as session:
                record = WalletTransactionModel(
                    user_id=effective_user_id,
                    tx_id=tx["tx_id"],
                    timestamp=tx["timestamp"],
                    tx_type=tx["tx_type"],
                    amount=tx["amount"],
                    balance_after=tx["balance_after"],
                    reference_id=tx.get("reference_id", ""),
                    description=tx.get("description", "")
                )
                session.add(record)
                await session.commit()
                logger.info(f"[DB_RECORD_WALLET_TX] Wallet transaction {tx.get('tx_id')} saved for user_id={effective_user_id}.")
        except Exception as e:
            logger.error(f"Error saving wallet transaction to DB for user_id={effective_user_id}: {e}")

    async def load_equity_history(self, limit: int = 100, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load equity history curve points from DB for user_id."""
        if user_id is None:
            logger.warning("[DB_LOAD_EQUITY] load_equity_history called without user_id, returning [].")
            return []

        history = []
        try:
            async with AsyncSessionLocal() as session:
                stmt = select(EquityHistoryModel).where(EquityHistoryModel.user_id == user_id).order_by(EquityHistoryModel.id.asc()).limit(limit)

                result = await session.execute(stmt)
                records = result.scalars().all()
                for r in records:
                    history.append({
                        "id": r.id,
                        "user_id": r.user_id,
                        "timestamp": r.timestamp,
                        "equity": r.equity,
                        "wallet": r.wallet,
                        "margin": r.margin,
                        "unrealized_pnl": r.unrealized_pnl,
                        "realized_pnl": r.realized_pnl
                    })
        except Exception as e:
            logger.error(f"Error loading equity history from DB for user_id={user_id}: {e}")
        return history

    async def save_equity_point(self, snapshot: Dict[str, Any], user_id: Optional[int] = None):
        """Append equity history snapshot to DB for user_id."""
        effective_user_id = user_id or snapshot.get("user_id")
        try:
            async with AsyncSessionLocal() as session:
                entry = EquityHistoryModel(
                    user_id=effective_user_id,
                    timestamp=snapshot['timestamp'],
                    equity=snapshot['equity'],
                    wallet=snapshot['wallet'],
                    margin=snapshot['margin'],
                    unrealized_pnl=snapshot['unrealized_pnl'],
                    realized_pnl=snapshot['realized_pnl']
                )
                session.add(entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Error saving equity point to DB for user_id={effective_user_id}: {e}")

    async def log_audit_event(self, event_type: str, details: str, user_id: Optional[int] = None):
        """Record audit event log in DB for user_id."""
        try:
            async with AsyncSessionLocal() as session:
                log_entry = AuditLogModel(user_id=user_id, event_type=event_type, details=details)
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Error recording audit log to DB for user_id={user_id}: {e}")
