import time
import asyncio
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Any, Optional
from config import settings
from backend.repositories.trader_repository import TraderRepository
from institutional_risk import InstitutionalRiskManager, InstitutionalRiskConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trader")


class TraderState(str, Enum):
    BOOTING = "BOOTING"
    RESTORING_DATABASE = "RESTORING_DATABASE"
    VERIFYING_STATE = "VERIFYING_STATE"
    START_BACKGROUND_WORKERS = "START_BACKGROUND_WORKERS"
    READY = "READY"

class PaperTrader:
    def __init__(self, initial_balance: float = settings.PAPER_TRADING_INITIAL_BALANCE, user_id: Optional[int] = None):
        self.user_id = user_id
        self.state = TraderState.BOOTING
        self.usdt_balance = float(initial_balance)
        self.initial_balance = float(initial_balance)
        self.positions: Dict[str, Dict[str, Any]] = {}
        self.orders: List[Dict[str, Any]] = []
        self.trade_history: List[Dict[str, Any]] = []
        self.equity_history: List[Dict[str, Any]] = []
        self.ledger: List[Dict[str, Any]] = []
        self.last_equity_save_time = 0.0
        self.auto_bot_enabled = False
        self.risk_mode = getattr(settings, "DEFAULT_RISK_MODE", "Moderate")
        self.active_strategy = "AI Hybrid"
        self.default_allocation_usd: float = 1000.0
        self.default_leverage: int = 1
        self.max_open_positions = 10
        self.daily_start_balance = float(initial_balance)
        self.peak_equity = float(initial_balance)

        self.risk_manager = InstitutionalRiskManager()


        
        self.accounting_status = "PASS"
        self.database_sync_status = "SYNCED"
        self.last_validation_time = time.strftime("%Y-%m-%d %H:%M:%S")

        self.repo = TraderRepository()
        self.is_loaded = False
        self._persistence_lock: Optional[asyncio.Lock] = None
        self.background_tasks: set = set()
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    @property
    def persistence_lock(self) -> asyncio.Lock:
        """Get or lazily instantiate persistence Lock for current event loop."""
        current_loop = None
        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if self._persistence_lock is None:
            self._persistence_lock = asyncio.Lock()
        elif current_loop and getattr(self._persistence_lock, '_loop', None) and getattr(self._persistence_lock, '_loop') is not current_loop:
            self._persistence_lock = asyncio.Lock()
        return self._persistence_lock


    def set_main_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set main application event loop for thread-safe cross-thread coroutine scheduling."""
        self.main_loop = loop





    def _execute_ledger_transaction(
        self,
        tx_type: str,
        amount: float,
        reference_id: str = "",
        description: str = ""
    ) -> Dict[str, Any]:
        """Execute double-entry wallet balance modification and record ledger entry."""
        self.usdt_balance = round(self.usdt_balance + amount, 4)
        tx_id = f"TX_{int(time.time() * 1000)}_{len(self.ledger) + 1}"
        tx = {
            "tx_id": tx_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tx_type": tx_type.upper(),
            "amount": round(amount, 4),
            "balance_after": round(self.usdt_balance, 4),
            "reference_id": reference_id,
            "description": description
        }
        self.ledger.append(tx)
        self._sync_record_wallet_tx(tx)
        return tx

    async def initialize_and_restore_state(self):
        """Restore trader state from database on startup following strict state machine transitions."""
        logger.info(f"[STATE_TRANSITION] Current state: {self.state} -> Changing to RESTORING_DATABASE")
        if self.is_loaded and self.state == TraderState.READY:
            logger.info("[STARTUP] Already in READY state, skipping restore.")
            return

        self.state = TraderState.RESTORING_DATABASE
        await self.repo.initialize_repository()

        # 1. Restore Portfolio State
        portfolio_state = await self.repo.load_portfolio_state(user_id=self.user_id)
        if portfolio_state:
            self.usdt_balance = portfolio_state["usdt_balance"]
            self.initial_balance = portfolio_state["initial_balance"]
            self.auto_bot_enabled = portfolio_state["auto_bot_enabled"]
            self.active_strategy = portfolio_state["active_strategy"]
            self.risk_mode = portfolio_state["risk_mode"]
            self.default_allocation_usd = portfolio_state.get("default_allocation_usd", 1000.0)
            self.default_leverage = portfolio_state.get("default_leverage", 1)
            logger.info(f"[RESTORE_PORTFOLIO] Restored portfolio state for user_id={self.user_id}: ${self.usdt_balance:.2f} USDT | Strategy: {self.active_strategy} | Alloc: ${self.default_allocation_usd} | Leverage: {self.default_leverage}x")
        else:
            logger.info(f"[RESTORE_PORTFOLIO] No portfolio state found in DB for user_id={self.user_id}, using defaults.")

        # 2. Restore Open Positions (will raise RuntimeError on retry exhaustion)
        db_positions = await self.repo.load_open_positions(user_id=self.user_id)
        if db_positions:
            self.positions = db_positions
            logger.info(f"[RESTORE_POSITIONS] Restored {len(self.positions)} positions for user_id={self.user_id}: {list(self.positions.keys())}")
        else:
            logger.info(f"[RESTORE_POSITIONS] 0 open positions loaded from DB for user_id={self.user_id}.")

        # 3. Restore Trade History
        db_trades = await self.repo.load_trade_history(user_id=self.user_id)
        if db_trades:
            self.trade_history = db_trades
            logger.info(f"[RESTORE_TRADES] Restored {len(self.trade_history)} trade records for user_id={self.user_id}.")

        # 4. Restore Equity History
        db_equity = await self.repo.load_equity_history(user_id=self.user_id)
        if db_equity:
            self.equity_history = db_equity
            logger.info(f"[RESTORE_EQUITY] Restored {len(self.equity_history)} equity snapshots for user_id={self.user_id}.")

        # 5. Restore Wallet Ledger
        db_ledger = await self.repo.load_wallet_ledger(user_id=self.user_id)
        if db_ledger:
            # Deduplicate any duplicate initial deposits if multiple existed from previous restarts
            seen_init = False
            filtered_ledger = []
            for tx in db_ledger:
                if tx.get("reference_id") == "INIT_DEPOSIT" or tx.get("description") == "Initial Capital Deposit":
                    if not seen_init:
                        seen_init = True
                        tx["amount"] = self.initial_balance
                        tx["balance_after"] = self.initial_balance
                        filtered_ledger.append(tx)
                else:
                    filtered_ledger.append(tx)
            self.ledger = filtered_ledger
            logger.info(f"[RESTORE_LEDGER] Restored {len(self.ledger)} ledger entries for user_id={self.user_id}.")
        else:
            logger.info(f"[RESTORE_LEDGER] Ledger empty for user_id={self.user_id}. Creating single initial DEPOSIT entry...")
            target_balance = self.initial_balance if (not portfolio_state or self.usdt_balance <= 0) else self.usdt_balance
            self.usdt_balance = 0.0
            self.ledger = []
            self._execute_ledger_transaction(
                tx_type="DEPOSIT",
                amount=target_balance,
                reference_id="INIT_DEPOSIT",
                description="Initial Capital Deposit"
            )

        # 6. State Verification Step
        logger.info(f"[STATE_TRANSITION] Changing to VERIFYING_STATE...")
        self.state = TraderState.VERIFYING_STATE

        # Verify wallet balance against ledger reconstruction
        reconstructed = sum(tx["amount"] for tx in self.ledger)
        if abs(self.usdt_balance - reconstructed) > 0.01:
            logger.warning(f"[RESTORE_LEDGER_MISMATCH] Ledger mismatch on restore: USDT={self.usdt_balance}, LedgerSum={reconstructed}")
            self.usdt_balance = round(reconstructed, 4)


        # 7. Start Workers Transition
        logger.info(f"[STATE_TRANSITION] Changing to START_BACKGROUND_WORKERS...")
        self.state = TraderState.START_BACKGROUND_WORKERS

        self.last_equity_save_time = time.time()
        self.is_loaded = True

        # 8. Ready Transition
        logger.info(f"[STATE_TRANSITION] Changing to READY!")
        self.state = TraderState.READY
        logger.info(f"[STARTUP_COMPLETE] Trader is READY. Positions count: {len(self.positions)}, USDT balance: ${self.usdt_balance:.2f}")




    async def flush_persistence(self):
        """Await until all background persistence tasks in queue finish committing to disk."""
        while self.background_tasks:
            tasks = list(self.background_tasks)
            for item in tasks:
                if isinstance(item, asyncio.Task):
                    await item
                elif hasattr(item, "result"):  # concurrent.futures.Future
                    await asyncio.wrap_future(item)
                self.background_tasks.discard(item)

        async with self.persistence_lock:
            logger.info("[PERSISTENCE_FLUSH] All queued persistence tasks committed successfully.")


    def _run_serialized_db_task(self, coro):
        """Serialize all database writes under self.persistence_lock in sequence with thread-safe execution."""
        async def _serialized_runner():
            async with self.persistence_lock:
                try:
                    res = await coro() if callable(coro) else await coro
                    logger.info("[SERIALIZED_RUNNER_SUCCESS] DB task executed successfully under persistence lock.")
                    return res
                except Exception as e:
                    logger.error(f"[SERIALIZED_PERSISTENCE_ERROR] {e}", exc_info=True)
                    raise


        target_loop = None
        try:
            target_loop = asyncio.get_running_loop()
        except RuntimeError:
            pass

        if target_loop is None and self.main_loop and self.main_loop.is_running():
            target_loop = self.main_loop

        if target_loop is not None and target_loop.is_running():
            try:
                current_loop = None
                try:
                    current_loop = asyncio.get_running_loop()
                except RuntimeError:
                    pass

                if current_loop is target_loop:
                    task = target_loop.create_task(_serialized_runner())
                    self.background_tasks.add(task)
                    task.add_done_callback(lambda t: self.background_tasks.discard(t))
                else:
                    fut = asyncio.run_coroutine_threadsafe(_serialized_runner(), target_loop)
                    self.background_tasks.add(fut)
                    fut.add_done_callback(lambda f: self.background_tasks.discard(f))
            except Exception as e:
                logger.error(f"[PERSISTENCE_SCHEDULING_ERROR] Failed to schedule DB task: {e}", exc_info=True)
                raise RuntimeError(f"CRITICAL: Failed to schedule database task thread-safely: {e}")
        else:
            try:
                asyncio.run(_serialized_runner())
            except Exception as e:
                logger.error(f"[PERSISTENCE_SYNC_FALLBACK_ERROR] {e}", exc_info=True)
                raise RuntimeError(f"CRITICAL: Failed to execute database task synchronously: {e}")




    async def save_portfolio_async(self):
        """Awaited serialized save of portfolio state to DB."""
        await self.repo.save_portfolio_state(
            usdt_balance=self.usdt_balance,
            initial_balance=self.initial_balance,
            margin_used=sum(p.get('margin_usd', 0.0) for p in self.positions.values()),
            total_value=self.usdt_balance + sum(p.get('margin_usd', 0.0) for p in self.positions.values()),
            auto_bot_enabled=self.auto_bot_enabled,
            active_strategy=self.active_strategy,
            risk_mode=self.risk_mode,
            default_allocation_usd=self.default_allocation_usd,
            default_leverage=self.default_leverage,
            user_id=self.user_id
        )


    async def save_position_async(self, pos: Dict[str, Any]):
        """Awaited serialized save of position to DB."""
        await self.repo.save_position(pos, user_id=self.user_id)

    async def record_trade_async(self, trade_record: Dict[str, Any]):
        """Awaited serialized record of trade to DB."""
        await self.repo.record_trade(trade_record, user_id=self.user_id)

    async def record_wallet_tx_async(self, tx: Dict[str, Any]):
        """Awaited serialized record of wallet transaction to DB."""
        await self.repo.record_wallet_transaction(tx, user_id=self.user_id)

    async def save_equity_point_async(self, snapshot: Dict[str, Any]):
        """Awaited serialized save of equity point to DB."""
        await self.repo.save_equity_point(snapshot, user_id=self.user_id)

    async def log_audit_event_async(self, event_type: str, details: str):
        """Awaited serialized audit event log to DB."""
        await self.repo.log_audit_event(event_type, details, user_id=self.user_id)

    def _sync_save_portfolio(self):
        """Serialized save of portfolio state."""
        self._run_serialized_db_task(lambda: self.save_portfolio_async())

    def _sync_save_position(self, pos: Dict[str, Any]):
        """Serialized save of open position."""
        self._run_serialized_db_task(lambda: self.save_position_async(pos))

    def _sync_record_trade(self, trade_record: Dict[str, Any]):
        """Serialized trade record write."""
        self._run_serialized_db_task(lambda: self.record_trade_async(trade_record))

    def _sync_record_wallet_tx(self, tx: Dict[str, Any]):
        """Serialized wallet transaction write."""
        self._run_serialized_db_task(lambda: self.record_wallet_tx_async(tx))

    def _sync_save_equity_point(self, snapshot: Dict[str, Any]):
        """Serialized equity point write."""
        self._run_serialized_db_task(lambda: self.save_equity_point_async(snapshot))

    def _sync_log_audit_event(self, event_type: str, details: str):
        """Serialized audit log write."""
        self._run_serialized_db_task(lambda: self.log_audit_event_async(event_type, details))






    def validate_accounting(self, total_portfolio_value: float, total_open_margin: float, total_unrealized_pnl: float) -> Dict[str, Any]:
        """Perform accounting formula check within 0.01 USDT tolerance."""
        calculated_portfolio = self.usdt_balance + total_open_margin + total_unrealized_pnl
        mismatch_usdt = abs(total_portfolio_value - calculated_portfolio)

        reconstructed_ledger = sum(tx["amount"] for tx in self.ledger)
        ledger_mismatch = abs(self.usdt_balance - reconstructed_ledger)

        within_tolerance = (mismatch_usdt <= 0.01) and (ledger_mismatch <= 0.01)
        self.accounting_status = "PASS" if within_tolerance else "FAIL"
        self.last_validation_time = time.strftime("%Y-%m-%d %H:%M:%S")

        if not within_tolerance:
            msg = f"ACCOUNTING MISMATCH DETECTED: Formula Diff = {mismatch_usdt:.4f} USDT, Ledger Diff = {ledger_mismatch:.4f} USDT"
            logger.error(msg)
            self._sync_log_audit_event("ACCOUNTING_MISMATCH", msg)

        return {
            "calculated_portfolio": round(calculated_portfolio, 4),
            "mismatch_usdt": round(mismatch_usdt, 4),
            "ledger_mismatch": round(ledger_mismatch, 4),
            "reconstructed_ledger": round(reconstructed_ledger, 4),
            "within_tolerance": within_tolerance,
            "accounting_status": self.accounting_status
        }

    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Calculate real-time portfolio metrics according to single source of truth database formulas."""
        total_open_margin = 0.0
        total_unrealized_pnl = 0.0

        active_positions_list = []
        for symbol, pos in self.positions.items():
            from market_data import is_valid_price
            price = current_prices.get(symbol, pos['entry_price'])
            if not is_valid_price(price):
                logger.warning(f"[PNL_PROTECTION] Symbol={symbol} Candidate price ${price} is invalid. Retaining entry price ${pos['entry_price']}.")
                price = pos['entry_price']

            side = pos['side']
            amount = pos['amount']
            entry_price = pos['entry_price']
            leverage = pos.get('leverage', 1)
            margin = pos.get('margin_usd', (amount * entry_price) / leverage)


            if side == "LONG":
                pnl_usd = (price - entry_price) * amount
            else: # SHORT
                pnl_usd = (entry_price - price) * amount


            pnl_pct = (pnl_usd / margin) * 100.0 if margin > 0 else 0.0

            # Dynamic Trailing Stop check
            if pos.get('trailing_stop_pct'):
                trail_pct = pos['trailing_stop_pct'] / 100.0
                if side == "LONG":
                    new_sl = price * (1.0 - trail_pct)
                    if new_sl > pos['stop_loss_price']:
                        pos['stop_loss_price'] = round(new_sl, 4)
                        self._sync_save_position(pos)
                else:
                    new_sl = price * (1.0 + trail_pct)
                    if new_sl < pos['stop_loss_price']:
                        pos['stop_loss_price'] = round(new_sl, 4)
                        self._sync_save_position(pos)

            total_open_margin += margin
            total_unrealized_pnl += pnl_usd

            active_positions_list.append({
                "id": pos['id'],
                "symbol": symbol,
                "side": side,
                "amount": round(amount, 4),
                "leverage": leverage,
                "margin_usd": round(margin, 2),
                "entry_price": entry_price,
                "current_price": price,
                "unrealized_pnl_usd": round(pnl_usd, 2),
                "unrealized_pnl_pct": round(pnl_pct, 2),
                "stop_loss_price": pos['stop_loss_price'],
                "take_profit_price": pos['take_profit_price'],
                "liquidation_price": pos.get('liquidation_price', 0.0),
                "entry_time": pos['entry_time']
            })

        # Formula 1: Portfolio Value = Wallet Balance + Sum(Unrealized PnL) + Margin Value
        total_portfolio_value = self.usdt_balance + total_unrealized_pnl + total_open_margin

        # Accounting validation check
        audit_res = self.validate_accounting(total_portfolio_value, total_open_margin, total_unrealized_pnl)

        # Closed trades analysis
        closed_trades = [t for t in self.trade_history if t.get("status") == "CLOSED" or (t.get("exit_time") and t.get("exit_time") != "")]
        total_closed_pnl = sum(t.get("pnl_usd", 0.0) for t in closed_trades)

        # Formula 2: Total Profit = Sum(Closed Trade PnL) + Sum(Unrealized PnL)
        total_pnl_usd = total_closed_pnl + total_unrealized_pnl
        total_pnl_pct = (total_pnl_usd / self.initial_balance) * 100.0 if self.initial_balance > 0 else 0.0

        # Formula 3: Win Rate = Closed Winning Trades / Closed Trades
        closed_winning_trades = sum(1 for t in closed_trades if t.get("pnl_usd", 0.0) > 0)
        total_closed_count = len(closed_trades)
        win_rate = round((closed_winning_trades / total_closed_count) * 100.0, 1) if total_closed_count > 0 else 0.0

        # Formula 4: Daily PnL = Today's Closed PnL + Today's Unrealized PnL (Timezone Robust)
        today_local = time.strftime("%Y-%m-%d")
        today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        def _is_today(exit_time_str: str) -> bool:
            if not exit_time_str:
                return False
            s = str(exit_time_str).strip()
            if s.startswith(today_local) or s.startswith(today_utc):
                return True
            date_part = s.split("T")[0].split(" ")[0]
            return date_part == today_local or date_part == today_utc

        today_closed_pnl = sum(t.get("pnl_usd", 0.0) for t in closed_trades if _is_today(t.get("exit_time", "")))
        daily_pnl_usd = today_closed_pnl + total_unrealized_pnl
        daily_pnl_pct = (daily_pnl_usd / self.initial_balance) * 100.0 if self.initial_balance > 0 else 0.0


        # Equity history point snapshot
        now_ts = time.time()
        curr_equity = round(total_portfolio_value, 2)
        if not self.equity_history or (now_ts - self.last_equity_save_time) >= 5.0 or self.equity_history[-1]["equity"] != curr_equity:
            self.last_equity_save_time = now_ts
            snapshot = {
                "timestamp": time.strftime("%H:%M:%S"),
                "equity": curr_equity,
                "wallet": round(self.usdt_balance, 2),
                "margin": round(total_open_margin, 2),
                "unrealized_pnl": round(total_unrealized_pnl, 2),
                "realized_pnl": round(total_closed_pnl, 2)
            }
            self.equity_history.append(snapshot)
            if len(self.equity_history) > 100:
                self.equity_history.pop(0)
            self._sync_save_equity_point(snapshot)

        return {
            "usdt_balance": round(self.usdt_balance, 2),
            "available_balance": round(self.usdt_balance, 2),
            "margin_used": round(total_open_margin, 2),
            "total_portfolio_value": round(total_portfolio_value, 2),
            "total_unrealized_pnl_usd": round(total_unrealized_pnl, 2),
            "closed_pnl_usd": round(total_closed_pnl, 2),
            "daily_pnl_usd": round(daily_pnl_usd, 2),
            "daily_pnl_pct": round(daily_pnl_pct, 2),
            "total_pnl_usd": round(total_pnl_usd, 2),
            "total_pnl_pct": round(total_pnl_pct, 2),
            "win_rate": win_rate,
            "total_closed_trades": total_closed_count,
            "auto_bot_enabled": self.auto_bot_enabled,
            "risk_mode": self.risk_mode,
            "active_strategy": self.active_strategy,
            "active_positions": active_positions_list,
            "trade_history": self.trade_history,
            "pnl_history": self.equity_history,
            "ledger": self.ledger,
            "accounting_status": self.accounting_status,
            "database_sync_status": self.database_sync_status,
            "last_validation_time": self.last_validation_time,
            "open_orders": self.orders
        }



    def open_position(
        self,
        symbol: str,
        side: str,
        price: float,
        allocation_usd: float,
        stop_loss_price: float,
        take_profit_price: float,
        leverage: int = 1,
        order_type: str = "MARKET",
        trailing_stop_pct: Optional[float] = None,
        reason: str = "Signal Execution"
    ) -> Dict[str, Any]:
        logger.info(f"[RISK_VALIDATION] UserID={self.user_id} | Symbol={symbol} | Side={side} | Price=${price:.2f} | Alloc=${allocation_usd:.2f} | Leverage={leverage}x | MaxOpenPos={self.max_open_positions}")

        if symbol in self.positions:
            logger.info(f"[RISK_REJECTION] UserID={self.user_id} | Symbol={symbol} rejected: Position already active.")
            return {"status": "error", "message": f"Position already active for {symbol}"}

        # Institutional Risk Manager 2.0 Assessment
        risk_res = self.risk_manager.evaluate_order_risk(
            user_trader=self,
            symbol=symbol,
            side=side,
            price=price,
            allocation_usd=allocation_usd,
            leverage=leverage,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )

        if not risk_res["passed"]:
            logger.warning(f"[INSTITUTIONAL_RISK_REJECTION] UserID={self.user_id} | Symbol={symbol} rejected by Rule={risk_res.get('rule')}: {risk_res.get('message')}")
            return {"status": "error", "message": risk_res.get("message"), "rule": risk_res.get("rule")}

        allocation_usd = risk_res.get("adjusted_allocation_usd", allocation_usd)
        stop_loss_price = risk_res.get("stop_loss_price", stop_loss_price)
        take_profit_price = risk_res.get("take_profit_price", take_profit_price)

        margin_required = allocation_usd / leverage
        if margin_required > self.usdt_balance:
            logger.info(f"[RISK_ADJUSTMENT] UserID={self.user_id} | Margin required ${margin_required:.2f} > USDT balance ${self.usdt_balance:.2f}. Cap margin to ${self.usdt_balance:.2f}.")
            margin_required = self.usdt_balance
            allocation_usd = margin_required * leverage

        if margin_required < 5.0:
            logger.info(f"[RISK_REJECTION] UserID={self.user_id} | Symbol={symbol} rejected: Margin required ${margin_required:.2f} < $5.0 minimum balance requirement.")
            return {"status": "error", "message": "Insufficient USDT balance to open position"}


        logger.info(f"[RISK_PASSED] UserID={self.user_id} | Risk validations passed. MarginRequired=${margin_required:.2f}, Allocation=${allocation_usd:.2f}")
        amount = allocation_usd / price
        
        pos_id = f"POS_{int(time.time() * 1000)}_{symbol.replace('/', '')}"


        # Execute margin lock through double-entry ledger

        self._execute_ledger_transaction(
            tx_type="OPEN_MARGIN",
            amount=-margin_required,
            reference_id=pos_id,
            description=f"Margin locked for {side} {symbol} ({leverage}x)"
        )

        if side == "LONG":
            liq_price = round(price * (1.0 - (1.0 / leverage) * 0.9), 4)
        else:
            liq_price = round(price * (1.0 + (1.0 / leverage) * 0.9), 4)

        position = {
            "id": pos_id,
            "user_id": self.user_id,
            "symbol": symbol,
            "side": side.upper(),
            "entry_price": price,
            "amount": amount,
            "margin_usd": margin_required,
            "notional_val_usd": allocation_usd,
            "leverage": leverage,
            "order_type": order_type,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "trailing_stop_pct": trailing_stop_pct,
            "liquidation_price": liq_price,
            "entry_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason
        }
        self.positions[symbol] = position

        # Immediately create open trade record with expanded audit fields
        trade_record = {
            "id": pos_id,
            "user_id": self.user_id,
            "symbol": symbol,
            "side": side.upper(),
            "entry_price": price,
            "exit_price": 0.0,
            "amount": round(amount, 4),
            "margin_usd": round(margin_required, 2),
            "pnl_usd": 0.0,
            "pnl_pct": 0.0,
            "entry_time": position["entry_time"],
            "exit_time": "",
            "close_reason": "OPEN",
            "status": "OPEN",
            "strategy": self.active_strategy,
            "confidence": 75.0,
            "reason": reason,
            "exchange": "PAPER_EXCHANGE",
            "order_id": f"ORD_{pos_id}",
            "entry_fee": round(allocation_usd * 0.0005, 4),
            "exit_fee": 0.0,
            "funding_fee": 0.0,
            "slippage": 0.0,
            "latency": 0.005
        }

        self.trade_history.insert(0, trade_record)

        # Persist to DB
        self._sync_save_position(position)
        self._sync_record_trade(trade_record)
        self._sync_save_portfolio()

        logger.info(f"Opened {side} position for {symbol} at ${price}: {position}")
        return {"status": "success", "message": f"Opened {side} position for {symbol} at ${price}", "position": position}

    def close_position(self, symbol: str, price: float, reason: str = "Manual Close", ratio: float = 1.0) -> Dict[str, Any]:
        if symbol not in self.positions:
            return {"status": "error", "message": f"No active position for {symbol}"}

        pos = self.positions[symbol]
        side = pos['side']
        amount_to_close = pos['amount'] * ratio
        margin_to_release = pos['margin_usd'] * ratio

        if side == "LONG":
            pnl_usd = (price - pos['entry_price']) * amount_to_close
        else:
            pnl_usd = (pos['entry_price'] - price) * amount_to_close


        cost_basis = margin_to_release
        pnl_pct = (pnl_usd / cost_basis) * 100.0 if cost_basis > 0 else 0.0

        # Execute margin release & PnL settlement through double-entry ledger
        self._execute_ledger_transaction(
            tx_type="RELEASE_MARGIN",
            amount=margin_to_release,
            reference_id=pos['id'],
            description=f"Margin released for {side} {symbol}"
        )

        if pnl_usd != 0.0:
            tx_type = "LIQUIDATION" if "Liquidation" in reason else "REALIZED_PNL"
            self._execute_ledger_transaction(
                tx_type=tx_type,
                amount=pnl_usd,
                reference_id=pos['id'],
                description=f"{tx_type} for {side} {symbol} ({reason})"
            )

        if ratio >= 0.99:
            self.positions.pop(symbol)
            self._run_serialized_db_task(lambda: self.repo.delete_position(pos['id'], user_id=self.user_id))

        else:


            pos['amount'] -= amount_to_close
            pos['margin_usd'] -= margin_to_release
            self._sync_save_position(pos)

        trade_record = {
            "id": pos['id'],
            "user_id": self.user_id,
            "symbol": symbol,
            "side": side,
            "entry_price": pos['entry_price'],

            "exit_price": price,
            "amount": round(amount_to_close, 4),
            "margin_usd": round(margin_to_release, 2),
            "pnl_usd": round(pnl_usd, 2),
            "pnl_pct": round(pnl_pct, 2),
            "entry_time": pos['entry_time'],
            "exit_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "close_reason": reason,
            "status": "CLOSED",
            "strategy": self.active_strategy,
            "confidence": 75.0,
            "reason": reason,
            "exchange": "PAPER_EXCHANGE",
            "order_id": f"ORD_{pos['id']}",
            "entry_fee": round(pos['margin_usd'] * pos['leverage'] * 0.0005, 4),
            "exit_fee": round(amount_to_close * price * 0.0005, 4),
            "funding_fee": 0.0,
            "slippage": 0.0,
            "latency": 0.005
        }
        
        # Update existing trade record in trade_history or insert
        existing_idx = next((i for i, t in enumerate(self.trade_history) if t['id'] == pos['id']), None)
        if existing_idx is not None:
            self.trade_history[existing_idx] = trade_record
        else:
            self.trade_history.insert(0, trade_record)

        # Persist to DB
        self._sync_record_trade(trade_record)
        self._sync_save_portfolio()

        # Persist to Trade Journal
        journal_entry = {
            **trade_record,
            "market_regime": pos.get("market_regime", "BULL_TREND"),
            "score_breakdown": pos.get("score_breakdown", {}),
            "explainable_reasons": pos.get("explainable_reasons", [reason]),
            "holding_time_seconds": max(1.0, time.time() - float(pos.get("entry_time_ts", time.time() - 300))),
            "execution_latency_ms": 1.2
        }
        self._run_serialized_db_task(lambda: self.repo.save_journal_entry(journal_entry, user_id=self.user_id))

        logger.info(f"Closed {side} {symbol} at ${price}. PnL: ${pnl_usd:.2f} ({pnl_pct:.2f}%)")

        return {"status": "success", "message": f"Closed {side} {symbol} at ${price}. PnL: ${pnl_usd:.2f}", "trade": trade_record}

    def reverse_position(self, symbol: str, price: float) -> Dict[str, Any]:
        if symbol not in self.positions:
            return {"status": "error", "message": f"No active position for {symbol}"}

        pos = self.positions[symbol]
        old_side = pos['side']
        new_side = "SHORT" if old_side == "LONG" else "LONG"
        alloc = pos['margin_usd'] * pos['leverage']

        self.close_position(symbol, price, reason="Reverse Position")
        return self.open_position(
            symbol=symbol,
            side=new_side,
            price=price,
            allocation_usd=alloc,
            stop_loss_price=price * 0.975 if new_side == "LONG" else price * 1.025,
            take_profit_price=price * 1.05 if new_side == "LONG" else price * 0.95,
            leverage=pos.get('leverage', 1),
            reason=f"Reversed from {old_side}"
        )

    def check_stop_loss_take_profit(self, current_prices: Dict[str, float]):
        to_close = []
        for symbol, pos in self.positions.items():
            price = current_prices.get(symbol)
            if not price:
                continue

            side = pos['side']
            if side == "LONG":
                if price <= pos['stop_loss_price']:
                    to_close.append((symbol, price, f"Stop-Loss Triggered (${pos['stop_loss_price']})"))
                elif price >= pos['take_profit_price']:
                    to_close.append((symbol, price, f"Take-Profit Triggered (${pos['take_profit_price']})"))
                elif pos.get('liquidation_price') and price <= pos['liquidation_price']:
                    to_close.append((symbol, price, f"Liquidation Triggered (${pos['liquidation_price']})"))
            else:
                if price >= pos['stop_loss_price']:
                    to_close.append((symbol, price, f"Stop-Loss Triggered (${pos['stop_loss_price']})"))
                elif price <= pos['take_profit_price']:
                    to_close.append((symbol, price, f"Take-Profit Triggered (${pos['take_profit_price']})"))
                elif pos.get('liquidation_price') and price >= pos['liquidation_price']:
                    to_close.append((symbol, price, f"Liquidation Triggered (${pos['liquidation_price']})"))

        for symbol, price, reason in to_close:
            self.close_position(symbol, price, reason=reason)

    async def reset_paper_account_async(self, default_balance: float = 10000.0) -> Dict[str, Any]:
        """Reset paper trading account balance to default $10,000 USDT and completely clear positions, orders, trade history, equity history, and ledger in memory and database."""
        self.usdt_balance = float(default_balance)
        self.initial_balance = float(default_balance)
        self.daily_start_balance = float(default_balance)
        self.positions = {}
        self.orders = []
        self.trade_history = []
        self.equity_history = []
        self.ledger = []
        self.auto_bot_enabled = False

        # Add clean initial ledger entry
        tx_id = f"TX_{int(time.time() * 1000)}_1"
        init_tx = {
            "tx_id": tx_id,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tx_type": "DEPOSIT",
            "amount": float(default_balance),
            "balance_after": float(default_balance),
            "reference_id": "RESET_ACCOUNT",
            "description": "Paper Account Reset to Default $10,000.00 USDT"
        }
        self.ledger.append(init_tx)

        try:
            from backend.database.session import AsyncSessionLocal
            from sqlalchemy import text

            async with AsyncSessionLocal() as session:
                if self.user_id is not None:
                    await session.execute(text("DELETE FROM positions WHERE user_id = :uid OR user_id IS NULL"), {"uid": self.user_id})
                    await session.execute(text("DELETE FROM orders WHERE user_id = :uid OR user_id IS NULL"), {"uid": self.user_id})
                    await session.execute(text("DELETE FROM trades WHERE user_id = :uid OR user_id IS NULL"), {"uid": self.user_id})
                    await session.execute(text("DELETE FROM equity_history WHERE user_id = :uid OR user_id IS NULL"), {"uid": self.user_id})
                    await session.execute(text("DELETE FROM wallet_transactions WHERE user_id = :uid OR user_id IS NULL"), {"uid": self.user_id})
                    await session.execute(
                        text("UPDATE portfolio SET usdt_balance = :bal, initial_balance = :bal, margin_used = 0.0, total_value = :bal, auto_bot_enabled = 0 WHERE user_id = :uid OR user_id IS NULL"),
                        {"bal": default_balance, "uid": self.user_id}
                    )
                else:
                    await session.execute(text("DELETE FROM positions"))
                    await session.execute(text("DELETE FROM orders"))
                    await session.execute(text("DELETE FROM trades"))
                    await session.execute(text("DELETE FROM equity_history"))
                    await session.execute(text("DELETE FROM wallet_transactions"))
                    await session.execute(
                        text("UPDATE portfolio SET usdt_balance = :bal, initial_balance = :bal, margin_used = 0.0, total_value = :bal, auto_bot_enabled = 0"),
                        {"bal": default_balance}
                    )

                await session.commit()
                logger.info(f"[RESET_PAPER_ACCOUNT] Wiped database records & reset balance to ${default_balance:.2f} for user_id={self.user_id}")
        except Exception as e:
            logger.error(f"[RESET_PAPER_ACCOUNT] Async DB wipe error for user_id={self.user_id}: {e}", exc_info=True)

        await self.save_portfolio_async()
        await self.record_wallet_tx_async(init_tx)
        return {"status": "success", "message": f"Paper trading account, open positions, and trade history reset to default ${default_balance:,.2f} USDT."}

    def reset_paper_account(self, default_balance: float = 10000.0) -> Dict[str, Any]:
        """Synchronous wrapper for reset_paper_account_async."""
        self._run_serialized_db_task(lambda: self.reset_paper_account_async(default_balance))
        return {"status": "success", "message": f"Paper trading account reset to default ${default_balance:,.2f} USDT."}



class TraderManager:
    def __init__(self):
        self.traders: Dict[int, PaperTrader] = {}
        self._lock = asyncio.Lock()
        self.main_loop: Optional[asyncio.AbstractEventLoop] = None

    def set_main_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set main application event loop for all existing and future user traders."""
        self.main_loop = loop
        for tr in self.traders.values():
            tr.set_main_event_loop(loop)

    async def get_trader_for_user(self, user_id: int) -> PaperTrader:
        async with self._lock:
            if user_id not in self.traders:
                trader_instance = PaperTrader(user_id=user_id)
                if self.main_loop:
                    trader_instance.set_main_event_loop(self.main_loop)
                await trader_instance.initialize_and_restore_state()
                self.traders[user_id] = trader_instance
            return self.traders[user_id]

trader_manager = TraderManager()
trader = PaperTrader()


