"""
Isolated Virtual Sub-Wallet for Spot Research & Meme Coin Paper Trading.
Completely isolated from CEX directional spot, arbitrage flashloans, and funding wallets.
"""

import time
import uuid
import sqlite3
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

class SpotWalletState(BaseModel):
    wallet_id: str = "SPOT_RESEARCH_VIRTUAL_WALLET"
    name: str = "Spot Research Sub-Wallet"
    initial_balance_usd: float = 10000.0
    usdt_available_balance: float = 10000.0
    allocated_margin_usd: float = 0.0
    realized_pnl_usd: float = 0.0
    unrealized_pnl_usd: float = 0.0
    total_trades_count: int = 0
    winning_trades_count: int = 0
    losing_trades_count: int = 0
    total_equity_usd: float = 10000.0
    last_updated_ts: float = Field(default_factory=time.time)

class SpotSubWalletManager:
    """Institutional isolated virtual sub-wallet manager with SQLite persistence."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        self._init_db()
        self._load_or_create_wallet()

    def _init_db(self):
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_research_sub_wallet (
                    wallet_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    initial_balance_usd REAL NOT NULL,
                    usdt_available_balance REAL NOT NULL,
                    allocated_margin_usd REAL NOT NULL,
                    realized_pnl_usd REAL NOT NULL,
                    total_trades_count INTEGER NOT NULL,
                    winning_trades_count INTEGER NOT NULL,
                    losing_trades_count INTEGER NOT NULL,
                    last_updated_ts REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_research_wallet_transfers (
                    transfer_id TEXT PRIMARY KEY,
                    transfer_type TEXT NOT NULL,
                    amount_usd REAL NOT NULL,
                    reason TEXT NOT NULL,
                    balance_after_usd REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS spot_bot_learned_lessons (
                    lesson_id TEXT PRIMARY KEY,
                    trade_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    category TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    pnl_usd REAL NOT NULL,
                    pnl_pct REAL NOT NULL,
                    lesson_text TEXT NOT NULL,
                    weight_adjustments TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()

    def _load_or_create_wallet(self):
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM spot_research_sub_wallet WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'")
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                    INSERT INTO spot_research_sub_wallet (
                        wallet_id, name, initial_balance_usd, usdt_available_balance,
                        allocated_margin_usd, realized_pnl_usd, total_trades_count,
                        winning_trades_count, losing_trades_count, last_updated_ts
                    ) VALUES ('SPOT_RESEARCH_VIRTUAL_WALLET', 'Spot Research Sub-Wallet', 10000.0, 10000.0, 0.0, 0.0, 0, 0, 0, ?)
                """, (time.time(),))
                conn.commit()

    def get_wallet_state(self, unrealized_pnl_usd: float = 0.0) -> SpotWalletState:
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM spot_research_sub_wallet WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'")
            row = cursor.fetchone()
            if not row:
                return SpotWalletState()
            
            avail = float(row["usdt_available_balance"])
            margin = float(row["allocated_margin_usd"])
            realized = float(row["realized_pnl_usd"])
            total_eq = avail + margin + unrealized_pnl_usd

            return SpotWalletState(
                wallet_id=row["wallet_id"],
                name=row["name"],
                initial_balance_usd=float(row["initial_balance_usd"]),
                usdt_available_balance=avail,
                allocated_margin_usd=margin,
                realized_pnl_usd=realized,
                unrealized_pnl_usd=unrealized_pnl_usd,
                total_trades_count=int(row["total_trades_count"]),
                winning_trades_count=int(row["winning_trades_count"]),
                losing_trades_count=int(row["losing_trades_count"]),
                total_equity_usd=round(total_eq, 2),
                last_updated_ts=float(row["last_updated_ts"])
            )

    def reserve_margin(self, amount_usd: float) -> bool:
        """Lock margin for opening a new paper position."""
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT usdt_available_balance, allocated_margin_usd FROM spot_research_sub_wallet WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'")
            row = cursor.fetchone()
            if not row:
                return False
            
            avail = float(row["usdt_available_balance"])
            margin = float(row["allocated_margin_usd"])
            
            if avail < amount_usd:
                logger.warning(f"[SPOT_WALLET] Insufficient funds: Required ${amount_usd:.2f}, Available ${avail:.2f}")
                return False
            
            new_avail = avail - amount_usd
            new_margin = margin + amount_usd

            cursor.execute("""
                UPDATE spot_research_sub_wallet
                SET usdt_available_balance = ?, allocated_margin_usd = ?, last_updated_ts = ?
                WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'
            """, (new_avail, new_margin, time.time()))
            conn.commit()
            return True

    def release_margin(self, margin_usd: float, net_pnl_usd: float, is_win: bool):
        """Release margin upon closing position and credit/debit realized PnL."""
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT usdt_available_balance, allocated_margin_usd, realized_pnl_usd,
                       total_trades_count, winning_trades_count, losing_trades_count
                FROM spot_research_sub_wallet WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'
            """)
            row = cursor.fetchone()
            if not row:
                return
            
            avail = float(row["usdt_available_balance"])
            margin = float(row["allocated_margin_usd"])
            realized = float(row["realized_pnl_usd"])
            total_trades = int(row["total_trades_count"]) + 1
            win_trades = int(row["winning_trades_count"]) + (1 if is_win else 0)
            loss_trades = int(row["losing_trades_count"]) + (0 if is_win else 1)

            # Release locked margin and add net PnL (which can be negative)
            new_avail = max(0.0, avail + margin_usd + net_pnl_usd)
            new_margin = max(0.0, margin - margin_usd)
            new_realized = realized + net_pnl_usd

            cursor.execute("""
                UPDATE spot_research_sub_wallet
                SET usdt_available_balance = ?, allocated_margin_usd = ?, realized_pnl_usd = ?,
                    total_trades_count = ?, winning_trades_count = ?, losing_trades_count = ?,
                    last_updated_ts = ?
                WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'
            """, (new_avail, new_margin, new_realized, total_trades, win_trades, loss_trades, time.time()))
            conn.commit()

    def reset_wallet(self, initial_capital_usd: float = 10000.0):
        """Reset sub-wallet to fresh starting capital."""
        with create_sqlite_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE spot_research_sub_wallet
                SET initial_balance_usd = ?, usdt_available_balance = ?, allocated_margin_usd = 0.0,
                    realized_pnl_usd = 0.0, total_trades_count = 0, winning_trades_count = 0,
                    losing_trades_count = 0, last_updated_ts = ?
                WHERE wallet_id = 'SPOT_RESEARCH_VIRTUAL_WALLET'
            """, (initial_capital_usd, initial_capital_usd, time.time()))
            conn.commit()
            logger.info(f"[SPOT_WALLET] Reset virtual sub-wallet with ${initial_capital_usd:,.2f} USDT")
