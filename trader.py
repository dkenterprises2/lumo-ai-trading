import time
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional
from config import settings
from backend.repositories.trader_repository import TraderRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("trader")

class TraderState(str, Enum):
    BOOTING = "BOOTING"
    RESTORING_DATABASE = "RESTORING_DATABASE"
    VERIFYING_STATE = "VERIFYING_STATE"
    START_BACKGROUND_WORKERS = "START_BACKGROUND_WORKERS"
    READY = "READY"

class PaperTrader:
    def __init__(self, initial_balance: float = settings.PAPER_TRADING_INITIAL_BALANCE):
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
        self.max_open_positions = 10
        self.daily_start_balance = float(initial_balance)
        
        self.accounting_status = "PASS"
        self.database_sync_status = "SYNCED"
        self.last_validation_time = time.strftime("%Y-%m-%d %H:%M:%S")

        self.repo = TraderRepository()
        self.is_loaded = False
        self.persistence_lock = asyncio.Lock()
        self.background_tasks: set = set()



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
        portfolio_state = await self.repo.load_portfolio_state()
        if portfolio_state:
            self.usdt_balance = portfolio_state["usdt_balance"]
            self.initial_balance = portfolio_state["initial_balance"]
            self.auto_bot_enabled = portfolio_state["auto_bot_enabled"]
            self.active_strategy = portfolio_state["active_strategy"]
            self.risk_mode = portfolio_state["risk_mode"]
            logger.info(f"[RESTORE_PORTFOLIO] Restored portfolio state: ${self.usdt_balance:.2f} USDT | Strategy: {self.active_strategy}")
        else:
            logger.info("[RESTORE_PORTFOLIO] No portfolio state found in DB, using defaults.")

        # 2. Restore Open Positions (will raise RuntimeError on retry exhaustion)
        db_positions = await self.repo.load_open_positions()
        if db_positions:
            self.positions = db_positions
            logger.info(f"[RESTORE_POSITIONS] Restored {len(self.positions)} positions: {list(self.positions.keys())}")
        else:
            logger.info("[RESTORE_POSITIONS] 0 open positions loaded from DB.")

        # 3. Restore Trade History
        db_trades = await self.repo.load_trade_history()
        if db_trades:
            self.trade_history = db_trades
            logger.info(f"[RESTORE_TRADES] Restored {len(self.trade_history)} trade records.")

        # 4. Restore Equity History
        db_equity = await self.repo.load_equity_history()
        if db_equity:
            self.equity_history = db_equity
            logger.info(f"[RESTORE_EQUITY] Restored {len(self.equity_history)} equity snapshots.")

        # 5. Restore Wallet Ledger
        db_ledger = await self.repo.load_wallet_ledger()
        if db_ledger:
            self.ledger = db_ledger
            logger.info(f"[RESTORE_LEDGER] Restored {len(self.ledger)} ledger entries.")
        else:
            logger.info("[RESTORE_LEDGER] Ledger empty. Creating initial DEPOSIT entry...")
            self.usdt_balance = 0.0
            self._execute_ledger_transaction(
                tx_type="DEPOSIT",
                amount=self.initial_balance,
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
            await asyncio.gather(*tasks, return_exceptions=True)
        async with self.persistence_lock:
            logger.info("[PERSISTENCE_FLUSH] All queued persistence tasks committed successfully.")


    def _run_serialized_db_task(self, coro):
        """Serialize all database writes under self.persistence_lock in sequence with strong task references."""
        async def _serialized_runner():
            async with self.persistence_lock:
                try:
                    await coro() if callable(coro) else await coro
                except Exception as e:
                    logger.error(f"[SERIALIZED_PERSISTENCE_ERROR] {e}")

        try:
            loop = asyncio.get_running_loop()
            if loop.is_running() and not loop.is_closed():
                task = loop.create_task(_serialized_runner())
                self.background_tasks.add(task)
                task.add_done_callback(self.background_tasks.discard)
        except RuntimeError:
            pass


    async def save_portfolio_async(self):
        """Awaited serialized save of portfolio state to DB."""
        await self.repo.save_portfolio_state(
            usdt_balance=self.usdt_balance,
            initial_balance=self.initial_balance,
            margin_used=sum(p['margin_usd'] for p in self.positions.values()),
            total_value=self.usdt_balance + sum(p['margin_usd'] for p in self.positions.values()),
            auto_bot_enabled=self.auto_bot_enabled,
            active_strategy=self.active_strategy,
            risk_mode=self.risk_mode
        )

    async def save_position_async(self, pos: Dict[str, Any]):
        """Awaited serialized save of position to DB."""
        await self.repo.save_position(pos)

    def _sync_save_portfolio(self):
        """Serialized save of portfolio state."""
        self._run_serialized_db_task(lambda: self.save_portfolio_async())

    def _sync_save_position(self, pos: Dict[str, Any]):
        """Serialized save of open position."""
        self._run_serialized_db_task(lambda: self.save_position_async(pos))

    def _sync_record_trade(self, trade_record: Dict[str, Any]):
        """Serialized trade record write."""
        self._run_serialized_db_task(lambda: self.repo.record_trade(trade_record))

    def _sync_record_wallet_tx(self, tx: Dict[str, Any]):
        """Serialized wallet transaction write."""
        self._run_serialized_db_task(lambda: self.repo.record_wallet_transaction(tx))

    def _sync_save_equity_point(self, snapshot: Dict[str, Any]):
        """Serialized equity point write."""
        self._run_serialized_db_task(lambda: self.repo.save_equity_point(snapshot))

    def _sync_log_audit_event(self, event_type: str, details: str):
        """Serialized audit log write."""
        self._run_serialized_db_task(lambda: self.repo.log_audit_event(event_type, details))




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
            price = current_prices.get(symbol, pos['entry_price'])
            side = pos['side']
            amount = pos['amount']
            entry_price = pos['entry_price']
            leverage = pos.get('leverage', 1)
            margin = pos.get('margin_usd', (amount * entry_price) / leverage)

            if side == "LONG":
                pnl_usd = (price - entry_price) * amount * leverage
            else: # SHORT
                pnl_usd = (entry_price - price) * amount * leverage

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

        # Formula 4: Daily PnL = Today's Closed PnL + Today's Unrealized PnL
        today_str = time.strftime("%Y-%m-%d")
        today_closed_pnl = sum(t.get("pnl_usd", 0.0) for t in closed_trades if t.get("exit_time", "").startswith(today_str))
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
        if symbol in self.positions:
            return {"status": "error", "message": f"Position already active for {symbol}"}

        if len(self.positions) >= self.max_open_positions:
            return {"status": "error", "message": f"Maximum open position limit ({self.max_open_positions}) reached"}

        margin_required = allocation_usd / leverage
        if margin_required > self.usdt_balance:
            margin_required = self.usdt_balance
            allocation_usd = margin_required * leverage

        if margin_required < 5.0:
            return {"status": "error", "message": "Insufficient USDT balance to open position"}

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
            pnl_usd = (price - pos['entry_price']) * amount_to_close * pos['leverage']
        else:
            pnl_usd = (pos['entry_price'] - price) * amount_to_close * pos['leverage']

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
            self._run_serialized_db_task(lambda: self.repo.delete_position(pos['id']))
        else:


            pos['amount'] -= amount_to_close
            pos['margin_usd'] -= margin_to_release
            self._sync_save_position(pos)

        trade_record = {
            "id": pos['id'],
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
