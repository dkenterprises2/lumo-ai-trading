import time
import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

class DegradationStatus:
    HEALTHY = "HEALTHY"
    WATCH = "WATCH"
    DEGRADED = "DEGRADED"
    SUSPENDED = "SUSPENDED"

@dataclass
class DegradationCheckResult:
    pair: str
    version: str
    status: str
    expected_win_rate_pct: float
    actual_paper_win_rate_pct: float
    expected_edge_bps: float
    actual_paper_edge_bps: float
    drawdown_delta_pct: float
    reasons: List[str]
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class StrategyDegradationMonitor:
    """Authoritative Persistent Real-Time Monitor for Strategy Degradation & Signal Decay."""

    DB_PATH = get_db_path()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StrategyDegradationMonitor, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _get_conn(self) -> sqlite3.Connection:
        return create_sqlite_connection(self.DB_PATH, timeout=60.0)

    def _init_db(self):
        conn = None
        try:
            conn = self._get_conn()
            check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_degradation_log'").fetchone()
            if not check:
                conn.execute("""
                CREATE TABLE IF NOT EXISTS strategy_degradation_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pair TEXT NOT NULL,
                    version TEXT NOT NULL,
                    status TEXT NOT NULL,
                    expected_win_rate_pct REAL NOT NULL,
                    actual_paper_win_rate_pct REAL NOT NULL,
                    expected_edge_bps REAL NOT NULL,
                    actual_paper_edge_bps REAL NOT NULL,
                    drawdown_delta_pct REAL NOT NULL,
                    reasons TEXT NOT NULL,
                    timestamp REAL NOT NULL
                );
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_deg_pair ON strategy_degradation_log(pair);")
                conn.commit()
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    def evaluate_strategy_health(
        self,
        pair: str,
        version: str,
        expected_win_rate_pct: float = 65.0,
        expected_edge_bps: float = 25.0,
        actual_paper_win_rate_pct: float = 62.0,
        actual_paper_edge_bps: float = 22.0,
        max_drawdown_pct: float = 4.5
    ) -> DegradationCheckResult:
        now = time.time()
        reasons = []
        status = DegradationStatus.HEALTHY

        wr_delta = expected_win_rate_pct - actual_paper_win_rate_pct
        edge_delta = expected_edge_bps - actual_paper_edge_bps

        if wr_delta > 15.0 or edge_delta > 20.0 or max_drawdown_pct > 12.0:
            status = DegradationStatus.SUSPENDED
            reasons.append(f"Severe OOS performance decay: Win Rate dropped by {wr_delta:.1f}%, Edge dropped by {edge_delta:.1f}bps.")
        elif wr_delta > 8.0 or edge_delta > 10.0 or max_drawdown_pct > 8.0:
            status = DegradationStatus.DEGRADED
            reasons.append(f"Moderate performance degradation: Win Rate down by {wr_delta:.1f}%, Edge down by {edge_delta:.1f}bps.")
        elif wr_delta > 4.0 or edge_delta > 5.0:
            status = DegradationStatus.WATCH
            reasons.append(f"Minor performance variance observed: Win Rate down by {wr_delta:.1f}%.")
        else:
            reasons.append("Strategy performing within expected OOS bounds.")

        res = DegradationCheckResult(
            pair=pair,
            version=version,
            status=status,
            expected_win_rate_pct=expected_win_rate_pct,
            actual_paper_win_rate_pct=actual_paper_win_rate_pct,
            expected_edge_bps=expected_edge_bps,
            actual_paper_edge_bps=actual_paper_edge_bps,
            drawdown_delta_pct=round(max_drawdown_pct, 2),
            reasons=reasons,
            timestamp=now
        )

        try:
            with self._get_conn() as conn:
                conn.execute("""
                INSERT INTO strategy_degradation_log (
                    pair, version, status, expected_win_rate_pct, actual_paper_win_rate_pct,
                    expected_edge_bps, actual_paper_edge_bps, drawdown_delta_pct, reasons, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    res.pair, res.version, res.status, res.expected_win_rate_pct,
                    res.actual_paper_win_rate_pct, res.expected_edge_bps, res.actual_paper_edge_bps,
                    res.drawdown_delta_pct, json.dumps(res.reasons), res.timestamp
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"[StrategyDegradationMonitor] Error logging health: {e}")

        return res

    def get_latest_health(self, pair: str) -> Optional[DegradationCheckResult]:
        try:
            with self._get_conn() as conn:
                row = conn.execute("SELECT * FROM strategy_degradation_log WHERE pair = ? ORDER BY timestamp DESC LIMIT 1", (pair,)).fetchone()
                if row:
                    return DegradationCheckResult(
                        pair=row["pair"],
                        version=row["version"],
                        status=row["status"],
                        expected_win_rate_pct=row["expected_win_rate_pct"],
                        actual_paper_win_rate_pct=row["actual_paper_win_rate_pct"],
                        expected_edge_bps=row["expected_edge_bps"],
                        actual_paper_edge_bps=row["actual_paper_edge_bps"],
                        drawdown_delta_pct=row["drawdown_delta_pct"],
                        reasons=json.loads(row["reasons"]),
                        timestamp=row["timestamp"]
                    )
        except Exception as e:
            logger.error(f"[StrategyDegradationMonitor] Error getting health for {pair}: {e}")
        return None

# Global Singleton Monitor
degradation_monitor = StrategyDegradationMonitor()
strategy_degradation_monitor = degradation_monitor
