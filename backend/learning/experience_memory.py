import sqlite3
import time
import uuid
import json
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

@dataclass
class TradeExperience:
    """Authoritative Persistent Trade Experience Record.
    
    Stores complete pre-trade observations, decision parameters, execution outcomes,
    and post-trade analysis for closed-loop continuous learning.
    """
    experience_id: str = field(default_factory=lambda: f"EXP-{uuid.uuid4().hex[:8].upper()}")
    timestamp: float = field(default_factory=time.time)
    symbol: str = "BTC/USDT"
    market: str = "SPOT"
    strategy: str = "SUPERINTELLIGENT_BRAIN_V44_3"
    decision: str = "TRADE"  # TRADE, NO_TRADE
    direction: str = "LONG"  # LONG, SHORT, NEUTRAL
    entry_price: float = 0.0
    exit_price: float = 0.0
    quantity: float = 0.0
    allocation_usd: float = 0.0
    execution_mode: str = "PAPER"  # PAPER, SHADOW, LIVE
    market_regime: str = "TRENDING_BULL"
    regime_confidence: float = 0.85
    signal_features: Dict[str, Any] = field(default_factory=dict)
    calibrated_win_probability: float = 0.65
    expected_edge_bps: float = 25.0
    realized_pnl: float = 0.0
    realized_pnl_pct: float = 0.0
    fees_usd: float = 0.0
    slippage_usd: float = 0.0
    market_impact_usd: float = 0.0
    holding_time_seconds: float = 0.0
    max_favorable_excursion_pct: float = 0.0
    max_adverse_excursion_pct: float = 0.0
    drawdown_usd: float = 0.0
    execution_latency_ms: float = 20.0
    portfolio_exposure: float = 0.15
    correlation_exposure: float = 0.10
    thesis: str = "Momentum breakout with high volume confirmation"
    invalidation: str = "Drop below swing low EMA20"
    exit_reason: str = "TAKE_PROFIT"
    decision_hash: str = ""
    model_version: str = "V44.4"
    risk_version: str = "RISK_V2"
    execution_version: str = "OMS_V35"
    error_classification: str = "NONE"
    lesson_extracted: Optional[str] = None
    lesson_confidence: float = 0.0
    evidence_count: int = 1
    status: str = "RECORDED"  # RECORDED, ANALYZED, HYPOTHESIZED, VALIDATED

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class ExperienceMemoryStore:
    """Authoritative Persistent SQLite Storage for Trade Experience Memory."""

    DB_PATH = get_db_path()
    _instance = None
    _db_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExperienceMemoryStore, cls).__new__(cls)
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
                    check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trade_experiences'").fetchone()
                    if not check:
                        conn.execute("""
                        CREATE TABLE IF NOT EXISTS trade_experiences (
                            experience_id TEXT PRIMARY KEY,
                            timestamp REAL NOT NULL,
                            symbol TEXT NOT NULL,
                            market TEXT NOT NULL,
                            strategy TEXT NOT NULL,
                            decision TEXT NOT NULL,
                            direction TEXT NOT NULL,
                            entry_price REAL NOT NULL,
                            exit_price REAL NOT NULL,
                            quantity REAL NOT NULL,
                            allocation_usd REAL NOT NULL,
                            execution_mode TEXT NOT NULL,
                            market_regime TEXT NOT NULL,
                            regime_confidence REAL NOT NULL,
                            signal_features TEXT NOT NULL,
                            calibrated_win_probability REAL NOT NULL,
                            expected_edge_bps REAL NOT NULL,
                            realized_pnl REAL NOT NULL,
                            realized_pnl_pct REAL NOT NULL,
                            fees_usd REAL NOT NULL,
                            slippage_usd REAL NOT NULL,
                            market_impact_usd REAL NOT NULL,
                            holding_time_seconds REAL NOT NULL,
                            max_favorable_excursion_pct REAL NOT NULL,
                            max_adverse_excursion_pct REAL NOT NULL,
                            drawdown_usd REAL NOT NULL,
                            execution_latency_ms REAL NOT NULL,
                            portfolio_exposure REAL NOT NULL,
                            correlation_exposure REAL NOT NULL,
                            thesis TEXT NOT NULL,
                            invalidation TEXT NOT NULL,
                            exit_reason TEXT NOT NULL,
                            decision_hash TEXT NOT NULL,
                            model_version TEXT NOT NULL,
                            risk_version TEXT NOT NULL,
                            execution_version TEXT NOT NULL,
                            error_classification TEXT NOT NULL,
                            lesson_extracted TEXT,
                            lesson_confidence REAL NOT NULL,
                            evidence_count INTEGER NOT NULL,
                            status TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        """)
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_exp_symbol ON trade_experiences(symbol);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_exp_regime ON trade_experiences(market_regime);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_exp_decision ON trade_experiences(decision);")
                        conn.execute("CREATE INDEX IF NOT EXISTS idx_exp_created_at ON trade_experiences(created_at);")
                        conn.commit()
            except Exception:
                pass

    def save_experience(self, exp: TradeExperience) -> bool:
        """Persist a trade or NO_TRADE experience record to SQLite with retry."""
        with self._db_lock:
            for attempt in range(8):
                try:
                    with self._get_conn() as conn:
                        conn.execute("""
                        INSERT OR REPLACE INTO trade_experiences (
                            experience_id, timestamp, symbol, market, strategy, decision, direction,
                            entry_price, exit_price, quantity, allocation_usd, execution_mode,
                            market_regime, regime_confidence, signal_features, calibrated_win_probability,
                            expected_edge_bps, realized_pnl, realized_pnl_pct, fees_usd, slippage_usd,
                            market_impact_usd, holding_time_seconds, max_favorable_excursion_pct,
                            max_adverse_excursion_pct, drawdown_usd, execution_latency_ms,
                            portfolio_exposure, correlation_exposure, thesis, invalidation,
                            exit_reason, decision_hash, model_version, risk_version,
                            execution_version, error_classification, lesson_extracted,
                            lesson_confidence, evidence_count, status
                        ) VALUES (
                            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                        )
                        """, (
                            exp.experience_id, exp.timestamp, exp.symbol, exp.market, exp.strategy,
                            exp.decision, exp.direction, exp.entry_price, exp.exit_price, exp.quantity,
                            exp.allocation_usd, exp.execution_mode, exp.market_regime, exp.regime_confidence,
                            json.dumps(exp.signal_features), exp.calibrated_win_probability, exp.expected_edge_bps,
                            exp.realized_pnl, exp.realized_pnl_pct, exp.fees_usd, exp.slippage_usd,
                            exp.market_impact_usd, exp.holding_time_seconds, exp.max_favorable_excursion_pct,
                            exp.max_adverse_excursion_pct, exp.drawdown_usd, exp.execution_latency_ms,
                            exp.portfolio_exposure, exp.correlation_exposure, exp.thesis, exp.invalidation,
                            exp.exit_reason, exp.decision_hash, exp.model_version, exp.risk_version,
                            exp.execution_version, exp.error_classification, exp.lesson_extracted,
                            exp.lesson_confidence, exp.evidence_count, exp.status
                        ))
                        conn.commit()
                        return True
                except Exception as e:
                    if attempt < 7 and "locked" in str(e).lower():
                        time.sleep(0.04 * (attempt + 1))
                        continue
                    logger.error(f"[ExperienceMemoryStore] Error saving experience: {e}")
                    return False
            return False

    def get_experience(self, experience_id: str) -> Optional[TradeExperience]:
        try:
            with self._get_conn() as conn:
                row = conn.execute("SELECT * FROM trade_experiences WHERE experience_id = ?", (experience_id,)).fetchone()
                if row:
                    d = dict(row)
                    d["signal_features"] = json.loads(d["signal_features"]) if d["signal_features"] else {}
                    del d["created_at"]
                    return TradeExperience(**d)
        except Exception as e:
            logger.error(f"[ExperienceMemoryStore] Error fetching experience {experience_id}: {e}")
        return None

    def query_experiences(
        self,
        symbol: Optional[str] = None,
        market_regime: Optional[str] = None,
        decision: Optional[str] = None,
        limit: int = 100
    ) -> List[TradeExperience]:
        query = "SELECT * FROM trade_experiences WHERE 1=1"
        params = []
        if symbol:
            query += " AND symbol = ?"
            params.append(symbol)
        if market_regime:
            query += " AND market_regime = ?"
            params.append(market_regime)
        if decision:
            query += " AND decision = ?"
            params.append(decision)
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        results = []
        try:
            with self._get_conn() as conn:
                rows = conn.execute(query, tuple(params)).fetchall()
                for r in rows:
                    d = dict(r)
                    d["signal_features"] = json.loads(d["signal_features"]) if d["signal_features"] else {}
                    del d["created_at"]
                    results.append(TradeExperience(**d))
        except Exception as e:
            logger.error(f"[ExperienceMemoryStore] Query error: {e}")
        return results

    def get_recent_experiences(self, limit: int = 50) -> List[TradeExperience]:
        """Fetch recent trade experiences."""
        return self.query_experiences(limit=limit)


    def get_summary_stats(self) -> Dict[str, Any]:
        try:
            with self._get_conn() as conn:
                row = conn.execute("""
                SELECT 
                    COUNT(*) as total_experiences,
                    SUM(CASE WHEN decision = 'TRADE' THEN 1 ELSE 0 END) as total_trades,
                    SUM(CASE WHEN decision = 'NO_TRADE' THEN 1 ELSE 0 END) as total_no_trades,
                    SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END) as winning_trades,
                    SUM(CASE WHEN realized_pnl < 0 THEN 1 ELSE 0 END) as losing_trades,
                    COALESCE(SUM(realized_pnl), 0.0) as total_realized_pnl,
                    COALESCE(SUM(fees_usd), 0.0) as total_fees_paid,
                    COALESCE(SUM(slippage_usd), 0.0) as total_slippage_cost
                FROM trade_experiences
                """).fetchone()
                if row:
                    total_trades = row["total_trades"]
                    win_count = row["winning_trades"]
                    win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0
                    return {
                        "total_experiences": int(row["total_experiences"]),
                        "total_trades": int(total_trades),
                        "total_no_trades": int(row["total_no_trades"]),
                        "winning_trades": int(win_count),
                        "losing_trades": int(row["losing_trades"]),
                        "win_rate_pct": round(win_rate, 2),
                        "total_realized_pnl": round(float(row["total_realized_pnl"]), 2),
                        "total_fees_paid": round(float(row["total_fees_paid"]), 2),
                        "total_slippage_cost": round(float(row["total_slippage_cost"]), 2)
                    }
        except Exception as e:
            logger.error(f"[ExperienceMemoryStore] Summary error: {e}")
        return {
            "total_experiences": 0, "total_trades": 0, "total_no_trades": 0,
            "winning_trades": 0, "losing_trades": 0, "win_rate_pct": 0.0,
            "total_realized_pnl": 0.0, "total_fees_paid": 0.0, "total_slippage_cost": 0.0
        }

# Global Singleton
experience_memory = ExperienceMemoryStore()
