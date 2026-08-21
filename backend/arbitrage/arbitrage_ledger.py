import sqlite3
import time
import os
from contextlib import contextmanager
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

class ArbitrageLedger:
    """Authoritative Persistent SQLite Ledger for Shadow Arbitrage Executions."""

    DB_PATH = get_db_path()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ArbitrageLedger, cls).__new__(cls)
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
                CREATE TABLE IF NOT EXISTS arbitrage_executions (
                    execution_id TEXT PRIMARY KEY,
                    opportunity_id TEXT,
                    symbol TEXT NOT NULL,
                    buy_exchange TEXT NOT NULL,
                    sell_exchange TEXT NOT NULL,
                    buy_price REAL NOT NULL,
                    sell_price REAL NOT NULL,
                    amount_usd REAL NOT NULL,
                    executed_qty REAL NOT NULL,
                    buy_fill_price REAL NOT NULL,
                    sell_fill_price REAL NOT NULL,
                    gross_pnl REAL NOT NULL,
                    fees_usd REAL NOT NULL,
                    slippage_usd REAL NOT NULL,
                    net_pnl REAL NOT NULL,
                    leg_status TEXT NOT NULL,
                    execution_status TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    rejection_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_arb_exec_symbol ON arbitrage_executions(symbol);
                """)
                conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_arb_exec_created_at ON arbitrage_executions(created_at);
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Error initializing table: {e}")

    def record_execution(self, exec_data: Dict[str, Any]) -> bool:
        """Persist a completed or rejected shadow arbitrage execution to SQLite."""
        try:
            with self._get_conn() as conn:
                conn.execute("""
                INSERT OR REPLACE INTO arbitrage_executions (
                    execution_id, opportunity_id, symbol, buy_exchange, sell_exchange,
                    buy_price, sell_price, amount_usd, executed_qty,
                    buy_fill_price, sell_fill_price, gross_pnl, fees_usd,
                    slippage_usd, net_pnl, leg_status, execution_status,
                    latency_ms, rejection_reason
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                )
                """, (
                    exec_data.get("execution_id") or exec_data.get("route_id") or f"EXEC-{uuid.uuid4().hex[:8].upper()}",
                    exec_data.get("opportunity_id"),
                    exec_data.get("symbol", "BTC/USDT"),
                    exec_data.get("buy_exchange", "BINANCE"),
                    exec_data.get("sell_exchange", "BYBIT"),
                    float(exec_data.get("buy_price", 0.0)),
                    float(exec_data.get("sell_price", 0.0)),
                    float(exec_data.get("amount_usd") or exec_data.get("requested_amount_usd", 10000.0)),
                    float(exec_data.get("executed_qty") or exec_data.get("requested_quantity", 0.0)),
                    float(exec_data.get("buy_fill_price", 0.0)),
                    float(exec_data.get("sell_fill_price", 0.0)),
                    float(exec_data.get("gross_pnl", 0.0)),
                    float(exec_data.get("fees_usd") or exec_data.get("fees", 0.0)),
                    float(exec_data.get("slippage_usd") or exec_data.get("slippage", 0.0)),
                    float(exec_data.get("net_pnl", 0.0)),
                    exec_data.get("leg_status", "BOTH_FILLED"),
                    exec_data.get("execution_status") or exec_data.get("status", "COMPLETED"),
                    float(exec_data.get("latency_ms") or exec_data.get("execution_latency_ms", 24.5)),
                    exec_data.get("rejection_reason")
                ))
                conn.commit()
            return True
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Record execution error: {e}")
            return False

    def get_realized_pnl(self) -> float:
        """Fetch true persisted realized Shadow Arbitrage PnL from SQLite."""
        try:
            with self._get_conn() as conn:
                row = conn.execute("SELECT SUM(net_pnl) FROM arbitrage_executions WHERE execution_status = 'COMPLETED'").fetchone()
                if row and row[0] is not None:
                    return round(float(row[0]), 2)
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Error fetching realized PnL: {e}")
        return 0.0

    def get_recent_executions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch recent executions for UI table display."""
        results = []
        try:
            with self._get_conn() as conn:
                rows = conn.execute("""
                SELECT execution_id as route_id, symbol, buy_exchange, sell_exchange,
                       buy_fill_price as buy_price, sell_fill_price as sell_price,
                       amount_usd as trade_size, net_pnl as profit_usd,
                       fees_usd as fee_deducted_usd, execution_status as status,
                       leg_status, latency_ms, created_at as timestamp
                FROM arbitrage_executions
                ORDER BY created_at DESC
                LIMIT ?
                """, (limit,)).fetchall()
                for r in rows:
                    results.append(dict(r))
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Error fetching recent executions: {e}")
        return results

    def get_ledger_summary(self) -> Dict[str, Any]:
        """Aggregate total count, fees, and realized profit from SQLite."""
        try:
            with self._get_conn() as conn:
                row = conn.execute("""
                SELECT 
                    COUNT(*) as total_executions,
                    SUM(CASE WHEN execution_status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_count,
                    COALESCE(SUM(amount_usd), 0.0) as total_volume_usd,
                    COALESCE(SUM(fees_usd), 0.0) as total_fees_usd,
                    COALESCE(SUM(slippage_usd), 0.0) as total_slippage_usd,
                    COALESCE(SUM(net_pnl), 0.0) as total_net_pnl
                FROM arbitrage_executions
                """).fetchone()
                if row:
                    return {
                        "total_executions": int(row["total_executions"] or 0),
                        "completed_count": int(row["completed_count"] or 0),
                        "total_volume_usd": round(float(row["total_volume_usd"] or 0.0), 2),
                        "total_fees_usd": round(float(row["total_fees_usd"] or 0.0), 2),
                        "total_slippage_usd": round(float(row["total_slippage_usd"] or 0.0), 2),
                        "total_net_pnl": round(float(row["total_net_pnl"] or 0.0), 2)
                    }
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Summary error: {e}")
        return {
            "total_executions": 0,
            "completed_count": 0,
            "total_volume_usd": 0.0,
            "total_fees_usd": 0.0,
            "total_slippage_usd": 0.0,
            "total_net_pnl": 0.0
        }

    def clear(self) -> bool:
        """Clear all test/simulated executions from SQLite ledger."""
        try:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM arbitrage_executions;")
                conn.commit()
            logger.info("[ArbitrageLedger] Cleared all execution records from SQLite.")
            return True
        except Exception as e:
            logger.error(f"[ArbitrageLedger] Error clearing ledger: {e}")
            return False

# Global Singleton
arbitrage_ledger = ArbitrageLedger()
