import asyncio
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

    async def load_portfolio_state(self) -> Optional[Dict[str, Any]]:
        """Load portfolio balance and bot settings from database with retries."""
        logger.info("[DB_LOAD] Attempting load_portfolio_state...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(PortfolioModel).limit(1))
                    portfolio = result.scalars().first()
                    if portfolio:
                        data = {
                            "usdt_balance": portfolio.usdt_balance,
                            "initial_balance": portfolio.initial_balance,
                            "margin_used": portfolio.margin_used,
                            "total_value": portfolio.total_value,
                            "auto_bot_enabled": portfolio.auto_bot_enabled,
                            "active_strategy": portfolio.active_strategy,
                            "risk_mode": portfolio.risk_mode
                        }
                        logger.info(f"[DB_LOAD] Portfolio state loaded: {data}")
                        return data
                    else:
                        logger.info("[DB_LOAD] No portfolio record found in DB.")
                        return None
            except Exception as e:
                logger.warning(f"[DB_LOAD_RETRY {attempt}/{max_retries}] Error loading portfolio state: {e}")
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
        risk_mode: str
    ):
        """Persist portfolio balance and bot configuration to DB."""
        logger.info(f"[DB_WRITE_PORTFOLIO] Attempting save_portfolio_state: balance=${usdt_balance}, margin=${margin_used}, total=${total_value}")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(PortfolioModel).limit(1))
                    portfolio = result.scalars().first()
                    if not portfolio:
                        portfolio = PortfolioModel(
                            usdt_balance=usdt_balance,
                            initial_balance=initial_balance,
                            margin_used=margin_used,
                            total_value=total_value,
                            auto_bot_enabled=auto_bot_enabled,
                            active_strategy=active_strategy,
                            risk_mode=risk_mode
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

                    await session.commit()
                    logger.info(f"[DB_COMMIT_PORTFOLIO] Portfolio state committed successfully.")
                    return
            except Exception as e:
                logger.warning(f"[DB_WRITE_PORTFOLIO_RETRY {attempt}/{max_retries}] Exception saving portfolio state: {e}")
                if attempt == max_retries:
                    logger.error(f"[DB_ROLLBACK_PORTFOLIO] Error saving portfolio state after {max_retries} retries: {e}")
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def load_open_positions(self) -> Dict[str, Dict[str, Any]]:

        """Load active open positions from DB on startup with automatic retries on DB locks."""
        logger.info("[DB_LOAD_POSITIONS] Attempting load_open_positions...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            positions = {}
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(PositionModel))
                    db_positions = result.scalars().all()
                    for pos in db_positions:
                        positions[pos.symbol] = {
                            "id": pos.id,
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
                    logger.info(f"[DB_LOAD_POSITIONS] Successfully loaded {len(positions)} positions: {list(positions.keys())}")
                    return positions
            except Exception as e:
                logger.warning(f"[DB_LOAD_POSITIONS_RETRY {attempt}/{max_retries}] Database exception while loading positions: {e}")
                if attempt == max_retries:
                    raise RuntimeError(f"CRITICAL: Failed to load open positions from DB after {max_retries} retries: {e}")
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))
        return {}


    async def save_position(self, pos: Dict[str, Any]):
        """Persist or update open position in DB with retries."""
        logger.info(f"[DB_SAVE_POSITION] Attempting save_position for ID={pos.get('id')}, symbol={pos.get('symbol')}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    result = await session.execute(select(PositionModel).where(PositionModel.id == pos['id']))
                    db_pos = result.scalars().first()
                    if not db_pos:
                        db_pos = PositionModel(
                            id=pos['id'],
                            symbol=pos['symbol'],
                            side=pos['side'],
                            entry_price=pos['entry_price'],
                            amount=pos['amount'],
                            margin_usd=pos['margin_usd'],
                            leverage=pos['leverage'],
                            order_type=pos.get('order_type', 'MARKET'),
                            stop_loss_price=pos['stop_loss_price'],
                            take_profit_price=pos['take_profit_price'],
                            liquidation_price=pos.get('liquidation_price', 0.0),
                            trailing_stop_pct=pos.get('trailing_stop_pct'),
                            entry_time=pos['entry_time'],
                            reason=pos.get('reason', '')
                        )
                        session.add(db_pos)
                        logger.info(f"[DB_SAVE_POSITION_INSERT] Prepared INSERT for position ID={pos['id']}")
                    else:
                        db_pos.amount = pos['amount']
                        db_pos.margin_usd = pos['margin_usd']
                        db_pos.stop_loss_price = pos['stop_loss_price']
                        db_pos.take_profit_price = pos['take_profit_price']
                        logger.info(f"[DB_SAVE_POSITION_UPDATE] Prepared UPDATE for position ID={pos['id']}")

                    await session.commit()
                    logger.info(f"[DB_COMMIT_POSITION] Position ID={pos['id']} committed successfully.")
                    return
            except Exception as e:
                logger.warning(f"[DB_SAVE_POSITION_RETRY {attempt}/{max_retries}] Exception saving position {pos.get('symbol')}: {e}")
                if attempt == max_retries:
                    logger.error(f"[DB_ROLLBACK_POSITION] Error saving position {pos.get('symbol')} after {max_retries} retries: {e}")
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))

    async def delete_position(self, pos_id: str):
        """Remove closed position from DB with retries."""
        logger.info(f"[DB_DELETE_POSITION] Attempting delete_position for ID={pos_id}...")
        max_retries = 5
        for attempt in range(1, max_retries + 1):
            try:
                async with AsyncSessionLocal() as session:
                    await session.execute(delete(PositionModel).where(PositionModel.id == pos_id))
                    await session.commit()
                    logger.info(f"[DB_COMMIT_DELETE] Position ID={pos_id} deleted successfully.")
                    return
            except Exception as e:
                logger.warning(f"[DB_DELETE_POSITION_RETRY {attempt}/{max_retries}] Exception deleting position ID={pos_id}: {e}")
                if attempt == max_retries:
                    logger.error(f"[DB_ROLLBACK_DELETE] Error deleting position {pos_id} after {max_retries} retries: {e}")
                    raise
                await asyncio.sleep(0.1 * (2 ** (attempt - 1)))



    async def load_trade_history(self) -> List[Dict[str, Any]]:
        """Load trade history logs from DB on startup."""
        trades = []
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(TradeModel).order_by(TradeModel.created_at.desc()).limit(100))
                db_trades = result.scalars().all()
                for t in db_trades:
                    trades.append({
                        "id": t.id,
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
                        "strategy": getattr(t, "strategy", "AI Hybrid"),
                        "confidence": getattr(t, "confidence", 75.0),
                        "reason": getattr(t, "reason", ""),
                        "exchange": getattr(t, "exchange", "PAPER_EXCHANGE"),
                        "order_id": getattr(t, "order_id", t.id),
                        "entry_fee": getattr(t, "entry_fee", 0.0),
                        "exit_fee": getattr(t, "exit_fee", 0.0),
                        "funding_fee": getattr(t, "funding_fee", 0.0),
                        "slippage": getattr(t, "slippage", 0.0),
                        "latency": getattr(t, "latency", 0.0)
                    })
        except Exception as e:
            logger.error(f"Error loading trade history from DB: {e}")
        return trades

    async def record_trade(self, trade: Dict[str, Any]):
        """Persist or update trade record to DB."""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(select(TradeModel).where(TradeModel.id == trade['id']))
                existing_trade = result.scalars().first()
                if existing_trade:
                    existing_trade.symbol = trade['symbol']
                    existing_trade.side = trade['side']
                    existing_trade.entry_price = trade['entry_price']
                    existing_trade.exit_price = trade.get('exit_price', trade['entry_price'])
                    existing_trade.amount = trade['amount']
                    existing_trade.margin_usd = trade['margin_usd']
                    existing_trade.pnl_usd = trade.get('pnl_usd', 0.0)
                    existing_trade.pnl_pct = trade.get('pnl_pct', 0.0)
                    existing_trade.entry_time = trade['entry_time']
                    existing_trade.exit_time = trade.get('exit_time', trade['entry_time'])
                    existing_trade.close_reason = trade.get('close_reason', '')
                    existing_trade.strategy = trade.get('strategy', 'AI Hybrid')
                    existing_trade.confidence = trade.get('confidence', 75.0)
                    existing_trade.reason = trade.get('reason', '')
                    existing_trade.exchange = trade.get('exchange', 'PAPER_EXCHANGE')
                    existing_trade.order_id = trade.get('order_id', trade['id'])
                    existing_trade.entry_fee = trade.get('entry_fee', 0.0)
                    existing_trade.exit_fee = trade.get('exit_fee', 0.0)
                    existing_trade.funding_fee = trade.get('funding_fee', 0.0)
                    existing_trade.slippage = trade.get('slippage', 0.0)
                    existing_trade.latency = trade.get('latency', 0.0)
                else:
                    db_trade = TradeModel(
                        id=trade['id'],
                        symbol=trade['symbol'],
                        side=trade['side'],
                        entry_price=trade['entry_price'],
                        exit_price=trade.get('exit_price', trade['entry_price']),
                        amount=trade['amount'],
                        margin_usd=trade['margin_usd'],
                        pnl_usd=trade.get('pnl_usd', 0.0),
                        pnl_pct=trade.get('pnl_pct', 0.0),
                        entry_time=trade['entry_time'],
                        exit_time=trade.get('exit_time', trade['entry_time']),
                        close_reason=trade.get('close_reason', ''),
                        strategy=trade.get('strategy', 'AI Hybrid'),
                        confidence=trade.get('confidence', 75.0),
                        reason=trade.get('reason', ''),
                        exchange=trade.get('exchange', 'PAPER_EXCHANGE'),
                        order_id=trade.get('order_id', trade['id']),
                        entry_fee=trade.get('entry_fee', 0.0),
                        exit_fee=trade.get('exit_fee', 0.0),
                        funding_fee=trade.get('funding_fee', 0.0),
                        slippage=trade.get('slippage', 0.0),
                        latency=trade.get('latency', 0.0)
                    )
                    session.add(db_trade)
                await session.commit()
        except Exception as e:
            logger.error(f"Error recording trade to DB: {e}")

    async def load_wallet_ledger(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Load wallet transaction ledger from DB."""
        ledger = []
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(WalletTransactionModel).order_by(WalletTransactionModel.id.asc()).limit(limit)
                )
                records = result.scalars().all()
                for r in records:
                    ledger.append({
                        "id": r.id,
                        "tx_id": r.tx_id,
                        "timestamp": r.timestamp,
                        "tx_type": r.tx_type,
                        "amount": r.amount,
                        "balance_after": r.balance_after,
                        "reference_id": r.reference_id,
                        "description": r.description
                    })
        except Exception as e:
            logger.error(f"Error loading wallet ledger from DB: {e}")
        return ledger

    async def record_wallet_transaction(self, tx: Dict[str, Any]):
        """Persist wallet ledger entry to DB."""
        try:
            async with AsyncSessionLocal() as session:
                entry = WalletTransactionModel(
                    tx_id=tx['tx_id'],
                    timestamp=tx['timestamp'],
                    tx_type=tx['tx_type'],
                    amount=tx['amount'],
                    balance_after=tx['balance_after'],
                    reference_id=tx.get('reference_id', ''),
                    description=tx.get('description', '')
                )
                session.add(entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Error saving wallet transaction to DB: {e}")

    async def load_equity_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Load equity history curve points from DB."""
        history = []
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute(
                    select(EquityHistoryModel).order_by(EquityHistoryModel.id.asc()).limit(limit)
                )
                records = result.scalars().all()
                for r in records:
                    history.append({
                        "id": r.id,
                        "timestamp": r.timestamp,
                        "equity": r.equity,
                        "wallet": r.wallet,
                        "margin": r.margin,
                        "unrealized_pnl": r.unrealized_pnl,
                        "realized_pnl": r.realized_pnl
                    })
        except Exception as e:
            logger.error(f"Error loading equity history from DB: {e}")
        return history

    async def save_equity_point(self, snapshot: Dict[str, Any]):
        """Append equity history snapshot to DB."""
        try:
            async with AsyncSessionLocal() as session:
                entry = EquityHistoryModel(
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
            logger.error(f"Error saving equity point to DB: {e}")

    async def log_audit_event(self, event_type: str, details: str):
        """Record audit event log in DB."""
        try:
            async with AsyncSessionLocal() as session:
                log_entry = AuditLogModel(event_type=event_type, details=details)
                session.add(log_entry)
                await session.commit()
        except Exception as e:
            logger.error(f"Error recording audit log to DB: {e}")


