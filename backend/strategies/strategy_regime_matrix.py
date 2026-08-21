import sqlite3
import json
from dataclasses import dataclass, asdict, field
from typing import Dict, List, Any, Optional
from loguru import logger
from backend.database.db_config import get_db_path, create_sqlite_connection

@dataclass
class StrategyRegimeCell:
    pair: str
    strategy_family: str
    regime: str
    candidate_count: int = 0
    qualified_signals: int = 0
    accepted_trades: int = 0
    rejected_trades: int = 0
    win_rate: float = 0.0
    expectancy_bps: float = 0.0
    profit_factor: float = 0.0
    net_pnl_usd: float = 0.0
    fees_usd: float = 0.0
    slippage_usd: float = 0.0
    max_drawdown_usd: float = 0.0
    sample_size: int = 0
    oos_support: str = "UNTESTED"
    calibration_score: float = 0.0
    degradation_status: str = "HEALTHY"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class StrategyRegimeMatrix:
    """
    Phase 47 Empirical Strategy-Regime Performance Matrix.
    Maintains empirical tracking across (pair x strategy_family x regime).
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or get_db_path()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        return create_sqlite_connection(self.db_path, timeout=60.0)

    def _init_db(self):
        conn = None
        try:
            conn = self._get_conn()
            check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='strategy_regime_matrix'").fetchone()
            if not check:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS strategy_regime_matrix (
                        pair TEXT,
                        strategy_family TEXT,
                        regime TEXT,
                        candidate_count INTEGER,
                        qualified_signals INTEGER,
                        accepted_trades INTEGER,
                        rejected_trades INTEGER,
                        win_rate REAL,
                        expectancy_bps REAL,
                        profit_factor REAL,
                        net_pnl_usd REAL,
                        fees_usd REAL,
                        slippage_usd REAL,
                        max_drawdown_usd REAL,
                        sample_size INTEGER,
                        oos_support TEXT,
                        calibration_score REAL,
                        degradation_status TEXT,
                        updated_at REAL,
                        PRIMARY KEY (pair, strategy_family, regime)
                    )
                """)
                conn.commit()
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    def update_cell(self, cell: StrategyRegimeCell):
        import time
        conn = None
        try:
            conn = self._get_conn()
            conn.execute("""
                INSERT INTO strategy_regime_matrix (
                    pair, strategy_family, regime, candidate_count, qualified_signals,
                    accepted_trades, rejected_trades, win_rate, expectancy_bps,
                    profit_factor, net_pnl_usd, fees_usd, slippage_usd, max_drawdown_usd,
                    sample_size, oos_support, calibration_score, degradation_status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(pair, strategy_family, regime) DO UPDATE SET
                    candidate_count=excluded.candidate_count,
                    qualified_signals=excluded.qualified_signals,
                    accepted_trades=excluded.accepted_trades,
                    rejected_trades=excluded.rejected_trades,
                    win_rate=excluded.win_rate,
                    expectancy_bps=excluded.expectancy_bps,
                    profit_factor=excluded.profit_factor,
                    net_pnl_usd=excluded.net_pnl_usd,
                    fees_usd=excluded.fees_usd,
                    slippage_usd=excluded.slippage_usd,
                    max_drawdown_usd=excluded.max_drawdown_usd,
                    sample_size=excluded.sample_size,
                    oos_support=excluded.oos_support,
                    calibration_score=excluded.calibration_score,
                    degradation_status=excluded.degradation_status,
                    updated_at=excluded.updated_at
            """, (
                cell.pair, cell.strategy_family, cell.regime, cell.candidate_count,
                cell.qualified_signals, cell.accepted_trades, cell.rejected_trades,
                cell.win_rate, cell.expectancy_bps, cell.profit_factor, cell.net_pnl_usd,
                cell.fees_usd, cell.slippage_usd, cell.max_drawdown_usd, cell.sample_size,
                cell.oos_support, cell.calibration_score, cell.degradation_status, time.time()
            ))
            conn.commit()
        except Exception:
            pass
        finally:
            if conn:
                conn.close()

    def get_matrix_for_pair(self, pair: str) -> List[StrategyRegimeCell]:
        cells = []
        conn = None
        try:
            conn = self._get_conn()
            rows = conn.execute(
                "SELECT * FROM strategy_regime_matrix WHERE pair = ?", (pair,)
            ).fetchall()
            for r in rows:
                cells.append(StrategyRegimeCell(
                    pair=r["pair"],
                    strategy_family=r["strategy_family"],
                    regime=r["regime"],
                    candidate_count=r["candidate_count"],
                    qualified_signals=r["qualified_signals"],
                    accepted_trades=r["accepted_trades"],
                    rejected_trades=r["rejected_trades"],
                    win_rate=r["win_rate"],
                    expectancy_bps=r["expectancy_bps"],
                    profit_factor=r["profit_factor"],
                    net_pnl_usd=r["net_pnl_usd"],
                    fees_usd=r["fees_usd"],
                    slippage_usd=r["slippage_usd"],
                    max_drawdown_usd=r["max_drawdown_usd"],
                    sample_size=r["sample_size"],
                    oos_support=r["oos_support"],
                    calibration_score=r["calibration_score"],
                    degradation_status=r["degradation_status"]
                ))
        except Exception:
            pass
        finally:
            if conn:
                conn.close()
        return cells

strategy_regime_matrix = StrategyRegimeMatrix()
