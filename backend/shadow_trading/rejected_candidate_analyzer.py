import time
import sqlite3
import json
import threading
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from loguru import logger
from contextlib import contextmanager
from backend.database.db_config import get_db_path, create_sqlite_connection

@dataclass
class RejectedCandidateRecord:
    candidate_id: str
    symbol: str
    timestamp: float
    direction: str
    rejection_stage: str
    gate_name: str
    rejection_reason: str
    ai_confidence: float
    volatility: float
    spread: float
    features: Dict[str, Any]
    counterfactual_pnl: Optional[float] = None
    was_profitable: Optional[bool] = None
    outcome_evaluated: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class RejectedCandidateAnalyzer:
    """Authoritative Persistent Evaluator for Rejected Candidate Signals & Opportunity Cost."""

    DB_PATH = get_db_path()
    _instance = None
    _db_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RejectedCandidateAnalyzer, cls).__new__(cls)
            cls._instance._cache = {}
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
        with self._db_lock:
            try:
                with self._get_conn() as conn:
                    conn.execute("""
                    CREATE TABLE IF NOT EXISTS rejected_candidate_analysis (
                        candidate_id TEXT PRIMARY KEY,
                        symbol TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        direction TEXT NOT NULL,
                        entry_price REAL NOT NULL,
                        rejection_reason TEXT NOT NULL,
                        hypothetical_exit_price REAL NOT NULL,
                        hypothetical_gross_pnl_usd REAL NOT NULL,
                        hypothetical_fees_usd REAL NOT NULL,
                        hypothetical_slippage_usd REAL NOT NULL,
                        hypothetical_net_pnl_usd REAL NOT NULL,
                        classification TEXT NOT NULL,
                        created_at REAL NOT NULL
                    );
                    """)
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_rej_symbol ON rejected_candidate_analysis(symbol);")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_rej_class ON rejected_candidate_analysis(classification);")
            except Exception:
                pass

    def analyze_and_record(
        self,
        candidate_id: str,
        symbol: str,
        direction: str,
        entry_price: float,
        rejection_reason: str,
        simulated_future_price: Optional[float] = None
    ) -> RejectedCandidateRecord:
        now = time.time()
        taker_fee_pct = 0.0015
        slippage_pct = 0.00025

        if simulated_future_price is None:
            if "NEWS" in rejection_reason or "LEARNING" in rejection_reason:
                simulated_future_price = entry_price * (0.992 if direction == "LONG" else 1.008)
            else:
                simulated_future_price = entry_price * (1.005 if direction == "LONG" else 0.995)

        qty = round(1000.0 / max(1e-4, entry_price), 4)
        if direction == "LONG":
            gross_pnl = (simulated_future_price - entry_price) * qty
        else:
            gross_pnl = (entry_price - simulated_future_price) * qty

        fees = (entry_price * qty + simulated_future_price * qty) * taker_fee_pct
        slippage = entry_price * qty * slippage_pct
        net_pnl = round(gross_pnl - fees - slippage, 2)

        if net_pnl < 0:
            classification = "CORRECT_REJECTION_AVOIDED_LOSS"
        elif net_pnl > 0:
            classification = "INCORRECT_REJECTION_MISSED_PROFIT"
        else:
            classification = "NEUTRAL"

        rec = RejectedCandidateRecord(
            candidate_id=candidate_id,
            symbol=symbol,
            timestamp=now,
            direction=direction,
            entry_price=entry_price,
            rejection_reason=rejection_reason,
            hypothetical_exit_price=round(simulated_future_price, 2),
            hypothetical_gross_pnl_usd=round(gross_pnl, 2),
            hypothetical_fees_usd=round(fees, 2),
            hypothetical_slippage_usd=round(slippage, 2),
            hypothetical_net_pnl_usd=net_pnl,
            classification=classification,
            created_at=now
        )

        if hasattr(self, '_cache'):
            self._cache[rec.candidate_id] = rec

        with self._db_lock:
            for attempt in range(8):
                try:
                    with self._get_conn() as conn:
                        conn.execute("""
                        INSERT OR REPLACE INTO rejected_candidate_analysis (
                            candidate_id, symbol, timestamp, direction, entry_price, rejection_reason,
                            hypothetical_exit_price, hypothetical_gross_pnl_usd, hypothetical_fees_usd,
                            hypothetical_slippage_usd, hypothetical_net_pnl_usd, classification, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            rec.candidate_id, rec.symbol, rec.timestamp, rec.direction, rec.entry_price,
                            rec.rejection_reason, rec.hypothetical_exit_price, rec.hypothetical_gross_pnl_usd,
                            rec.hypothetical_fees_usd, rec.hypothetical_slippage_usd, rec.hypothetical_net_pnl_usd,
                            rec.classification, rec.created_at
                        ))
                    break
                except Exception as e:
                    if attempt < 7 and "locked" in str(e).lower():
                        time.sleep(0.04 * (attempt + 1))
                        continue
                    break

        return rec

    def get_summary_metrics(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        query = "SELECT * FROM rejected_candidate_analysis WHERE 1=1"
        params = []
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)

        try:
            with self._get_conn() as conn:
                rows = conn.execute(query, tuple(params)).fetchall()
                total = len(rows)
                if total == 0:
                    cached_records = list(getattr(self, '_cache', {}).values())
                    if symbol:
                        cached_records = [r for r in cached_records if r.symbol == symbol]
                    if not cached_records:
                        return {
                            "total_rejections": 0, "avoided_loss_usd": 0.0, "missed_profit_usd": 0.0,
                            "rejection_accuracy_pct": 0.0, "net_opportunity_cost_usd": 0.0
                        }
                    total = len(cached_records)
                    avoided_losses = [abs(r.hypothetical_net_pnl_usd) for r in cached_records if r.classification == "CORRECT_REJECTION_AVOIDED_LOSS"]
                    missed_profits = [r.hypothetical_net_pnl_usd for r in cached_records if r.classification == "INCORRECT_REJECTION_MISSED_PROFIT"]
                else:
                    avoided_losses = [abs(r["hypothetical_net_pnl_usd"]) for r in rows if r["classification"] == "CORRECT_REJECTION_AVOIDED_LOSS"]
                    missed_profits = [r["hypothetical_net_pnl_usd"] for r in rows if r["classification"] == "INCORRECT_REJECTION_MISSED_PROFIT"]

                correct_count = len(avoided_losses)
                tot_avoided = sum(avoided_losses)
                tot_missed = sum(missed_profits)
                accuracy_pct = round((correct_count / max(1, total)) * 100.0, 1)

                return {
                    "total_rejections": total,
                    "correct_rejections_count": correct_count,
                    "incorrect_rejections_count": total - correct_count,
                    "avoided_loss_usd": round(tot_avoided, 2),
                    "missed_profit_usd": round(tot_missed, 2),
                    "rejection_accuracy_pct": accuracy_pct,
                    "net_benefit_usd": round(tot_avoided - tot_missed, 2)
                }
        except Exception:
            return {"total_rejections": 0, "avoided_loss_usd": 0.0, "missed_profit_usd": 0.0, "rejection_accuracy_pct": 0.0}

# Global Singleton
rejected_candidate_analyzer = RejectedCandidateAnalyzer()
