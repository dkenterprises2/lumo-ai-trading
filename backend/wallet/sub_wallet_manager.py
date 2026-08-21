import time
import uuid
import sqlite3
from contextlib import contextmanager
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

class SubWallet(BaseModel):
    wallet_type: str  # funding, spot, arbitrage, shadow
    name: str
    description: str
    usdt_balance: float
    btc_balance: float
    eth_balance: float
    total_usd_value: float
    is_isolated: bool = True

class WalletTransferRecord(BaseModel):
    transfer_id: str
    from_wallet: str
    to_wallet: str
    asset: str
    amount: float
    usd_value: float
    timestamp: float
    status: str = "COMPLETED"

class SubWalletManager:
    """Institutional Multi-Wallet Capital Allocation Engine with SQLite Persistence & Real Market Pricing."""

    DB_PATH = get_db_path()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SubWalletManager, cls).__new__(cls)
            cls._instance.wallets = {
                "funding": SubWallet(
                    wallet_type="funding",
                    name="Primary Treasury Wallet",
                    description="Cold custody and institutional liquidity reserve.",
                    usdt_balance=10000.0,
                    btc_balance=0.15,
                    eth_balance=2.5,
                    total_usd_value=36467.50
                ),
                "spot": SubWallet(
                    wallet_type="spot",
                    name="Spot Trading Portfolio",
                    description="Dedicated capital for AI multi-strategy alpha execution.",
                    usdt_balance=10000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=10000.0
                ),
                "arbitrage": SubWallet(
                    wallet_type="arbitrage",
                    name="Cross-Exchange Arbitrage Pool",
                    description="High-frequency statistical and triangular arbitrage liquidity.",
                    usdt_balance=10000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=10000.0
                ),
                "shadow": SubWallet(
                    wallet_type="shadow",
                    name="Shadow Simulation Wallet",
                    description="Zero-risk paper sandbox capital for microstructure & backtest replay.",
                    usdt_balance=10000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=10000.0
                )
            }
            cls._instance.transfer_history = []
            cls._instance._init_db()
        return cls._instance

    @contextmanager
    def _get_conn(self):
        conn = create_sqlite_connection(self.DB_PATH, timeout=60.0)
        try:
            yield conn
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _init_db(self):
        try:
            with self._get_conn() as conn:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS wallet_transfers (
                    transfer_id TEXT PRIMARY KEY,
                    from_wallet TEXT NOT NULL,
                    to_wallet TEXT NOT NULL,
                    asset TEXT NOT NULL,
                    amount REAL NOT NULL,
                    usd_value REAL NOT NULL,
                    timestamp REAL NOT NULL,
                    status TEXT NOT NULL
                );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_transfer_time ON wallet_transfers(timestamp);")
                conn.commit()

            self._load_transfers_from_db()
        except Exception as e:
            logger.error(f"[SubWalletManager] DB Init error: {e}")

    def _load_transfers_from_db(self):
        try:
            with self._get_conn() as conn:
                cursor = conn.execute("SELECT * FROM wallet_transfers ORDER BY timestamp ASC;")
                rows = cursor.fetchall()
                self.transfer_history = [
                    WalletTransferRecord(
                        transfer_id=r["transfer_id"],
                        from_wallet=r["from_wallet"],
                        to_wallet=r["to_wallet"],
                        asset=r["asset"],
                        amount=r["amount"],
                        usd_value=r["usd_value"],
                        timestamp=r["timestamp"],
                        status=r["status"]
                    ) for r in rows
                ]
        except Exception as e:
            logger.error(f"[SubWalletManager] Error loading transfers: {e}")

    def _save_transfer_to_db(self, record: WalletTransferRecord):
        try:
            with self._get_conn() as conn:
                conn.execute("""
                INSERT INTO wallet_transfers (
                    transfer_id, from_wallet, to_wallet, asset, amount, usd_value, timestamp, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(transfer_id) DO NOTHING;
                """, (
                    record.transfer_id, record.from_wallet, record.to_wallet,
                    record.asset, record.amount, record.usd_value, record.timestamp, record.status
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"[SubWalletManager] DB Save error for transfer {record.transfer_id}: {e}")

    def _get_live_prices(self) -> Dict[str, float]:
        """Fetch latest live prices from candle archive or fallback to latest market price."""
        prices = {"USDT": 1.0, "BTC": 60000.0, "ETH": 3000.0}
        try:
            from backend.marketdata.historical_candle_archive import historical_candle_archive
            btc_candles = historical_candle_archive.get_candles("BTC/USDT", limit=1)
            if btc_candles:
                prices["BTC"] = btc_candles[-1].close
            eth_candles = historical_candle_archive.get_candles("ETH/USDT", limit=1)
            if eth_candles:
                prices["ETH"] = eth_candles[-1].close
        except Exception:
            pass
        return prices

    def _get_db_trading_stats(self) -> Dict[str, float]:
        """Fetch actual realized PnL and active margin used from SQLite database."""
        realized_pnl = 0.0
        margin_used = 0.0
        unrealized_pnl = 0.0
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                row = cursor.execute("SELECT SUM(pnl_usd) FROM trades WHERE pnl_usd IS NOT NULL").fetchone()
                if row and row[0] is not None:
                    realized_pnl = float(row[0])
                
                row_pos = cursor.execute("SELECT SUM(margin_usd) FROM positions WHERE margin_usd IS NOT NULL").fetchone()
                if row_pos and row_pos[0] is not None:
                    margin_used = float(row_pos[0])
        except Exception:
            pass

        return {
            "realized_pnl": realized_pnl,
            "margin_used": margin_used,
            "unrealized_pnl": unrealized_pnl
        }

    def get_summary(self, spot_unrealized: float = 0.0) -> Dict[str, Any]:
        """Returns overview of all 4 isolated sub-wallets synchronized with database."""
        self._recalculate_usd_values()
        stats = self._get_db_trading_stats()

        # Dynamic Spot Bot Wallet calculation
        spot_net_transfers = sum(
            t.amount if t.to_wallet == "spot" and t.asset == "USDT" else
            -t.amount if t.from_wallet == "spot" and t.asset == "USDT" else 0.0
            for t in self.transfer_history if t.status == "COMPLETED"
        )
        spot_base = 3000.0 + spot_net_transfers
        spot_realized = stats["realized_pnl"]
        spot_margin = stats["margin_used"]
        
        spot_usdt = round(max(0.0, spot_base + spot_realized - spot_margin), 2)
        self.wallets["spot"].usdt_balance = spot_usdt
        self.wallets["spot"].total_usd_value = round(max(0.0, spot_base + spot_realized + spot_unrealized), 2)

        # Dynamic Arbitrage Engine Wallet calculation strictly from SQLite ledger
        from backend.arbitrage.arbitrage_ledger import arbitrage_ledger
        arb_profit = arbitrage_ledger.get_realized_pnl()
        
        arb_net_transfers = sum(
            t.amount if t.to_wallet == "arbitrage" and t.asset == "USDT" else
            -t.amount if t.from_wallet == "arbitrage" and t.asset == "USDT" else 0.0
            for t in self.transfer_history if t.status == "COMPLETED"
        )
        arb_base = 2000.0 + arb_net_transfers
        self.wallets["arbitrage"].usdt_balance = round(arb_base + arb_profit, 2)
        self.wallets["arbitrage"].total_usd_value = self.wallets["arbitrage"].usdt_balance

        # Funding Wallet Net
        funding_net_transfers = sum(
            t.amount if t.to_wallet == "funding" and t.asset == "USDT" else
            -t.amount if t.from_wallet == "funding" and t.asset == "USDT" else 0.0
            for t in self.transfer_history if t.status == "COMPLETED"
        )
        self.wallets["funding"].usdt_balance = round(max(0.0, 5000.0 + funding_net_transfers), 2)
        self.wallets["funding"].total_usd_value = self.wallets["funding"].usdt_balance

        total_portfolio = sum(w.total_usd_value for k, w in self.wallets.items() if k != "shadow")
        return {
            "wallets": {k: w.model_dump() for k, w in self.wallets.items()},
            "total_real_capital_usd": round(total_portfolio, 2),
            "total_system_equity_usd": round(total_portfolio, 2),
            "shadow_sandbox_capital_usd": round(self.wallets["shadow"].total_usd_value, 2),
            "spot_margin_in_trades": round(spot_margin, 2),
            "spot_realized_pnl": round(spot_realized, 2),
            "arbitrage_realized_profit": round(arb_profit, 2),
            "transfers_count": len(self.transfer_history),
            "recent_transfers": [t.model_dump() for t in sorted(self.transfer_history, key=lambda x: x.timestamp, reverse=True)[:10]]
        }

    def get_wallets_summary(self, spot_unrealized: float = 0.0) -> Dict[str, Any]:
        """Alias for get_summary for backwards compatibility across all routers and services."""
        return self.get_summary(spot_unrealized=spot_unrealized)

    def reset(self):
        """Reset sub-wallets and clear non-initial transfer records upon account reset."""
        try:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM wallet_transfers WHERE transfer_id NOT LIKE 'TX-INIT-%';")
                conn.commit()
            self._load_transfers_from_db()
            self.wallets = {
                "funding": SubWallet(
                    wallet_type="funding",
                    name="Main Funding Wallet",
                    description="Master capital repository for deposits, withdrawals, and treasury.",
                    usdt_balance=5000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=5000.0
                ),
                "spot": SubWallet(
                    wallet_type="spot",
                    name="Spot Trading Bot Wallet",
                    description="Isolated capital allocated for AI Hybrid Spot bot & execution gateway.",
                    usdt_balance=3000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=3000.0
                ),
                "arbitrage": SubWallet(
                    wallet_type="arbitrage",
                    name="Arbitrage Engine Wallet",
                    description="Dedicated liquidity for cross-exchange spatial & triangular arbitrage.",
                    usdt_balance=2000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=2000.0
                ),
                "shadow": SubWallet(
                    wallet_type="shadow",
                    name="Shadow Simulation Wallet",
                    description="Zero-risk paper sandbox capital for microstructure & backtest replay.",
                    usdt_balance=10000.0,
                    btc_balance=0.0,
                    eth_balance=0.0,
                    total_usd_value=10000.0
                )
            }
            self._recalculate_usd_values()
        except Exception as e:
            logger.error(f"[SubWalletManager] Reset error: {e}")

    def transfer_funds(self, from_wallet: str, to_wallet: str, asset: str, amount: float) -> Dict[str, Any]:
        """Transfers funds instantly between sub-wallets without fees."""
        from_w = from_wallet.lower().strip()
        to_w = to_wallet.lower().strip()
        asset_norm = asset.upper().strip()

        if from_w not in self.wallets or to_w not in self.wallets:
            raise ValueError(f"Invalid wallet types: {from_w} -> {to_w}")
        if from_w == to_w:
            raise ValueError("Source and destination wallet cannot be identical.")
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than 0.")

        src = self.wallets[from_w]
        dst = self.wallets[to_w]
        prices = self._get_live_prices()

        # Check balance
        if asset_norm == "USDT":
            if src.usdt_balance < amount:
                raise ValueError(f"Insufficient USDT in {src.name}. Available: ${src.usdt_balance:,.2f}")
            src.usdt_balance -= amount
            dst.usdt_balance += amount
            usd_val = amount
        elif asset_norm == "BTC":
            if src.btc_balance < amount:
                raise ValueError(f"Insufficient BTC in {src.name}. Available: {src.btc_balance:.4f} BTC")
            src.btc_balance -= amount
            dst.btc_balance += amount
            usd_val = amount * prices["BTC"]
        elif asset_norm == "ETH":
            if src.eth_balance < amount:
                raise ValueError(f"Insufficient ETH in {src.name}. Available: {src.eth_balance:.4f} ETH")
            src.eth_balance -= amount
            dst.eth_balance += amount
            usd_val = amount * prices["ETH"]
        else:
            raise ValueError(f"Unsupported transfer asset: {asset_norm}")

        self._recalculate_usd_values()

        record = WalletTransferRecord(
            transfer_id=f"TX-{uuid.uuid4().hex[:8].upper()}",
            from_wallet=from_w,
            to_wallet=to_w,
            asset=asset_norm,
            amount=round(amount, 4),
            usd_value=round(usd_val, 2),
            timestamp=time.time()
        )
        self.transfer_history.append(record)
        self._save_transfer_to_db(record)

        return {
            "status": "success",
            "message": f"Successfully transferred {amount} {asset_norm} from {src.name} to {dst.name}.",
            "transfer": record.model_dump(),
            "updated_wallets": {
                from_w: src.model_dump(),
                to_w: dst.model_dump()
            }
        }

    def _recalculate_usd_values(self):
        prices = self._get_live_prices()
        for w in self.wallets.values():
            val = (w.usdt_balance * prices["USDT"]) + (w.btc_balance * prices["BTC"]) + (w.eth_balance * prices["ETH"])
            w.total_usd_value = round(val, 2)

sub_wallet_manager = SubWalletManager()
