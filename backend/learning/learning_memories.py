import time
from typing import Dict, List, Any, Optional
from collections import defaultdict
from .experience_memory import TradeExperience, experience_memory

class LearningMemoryHierarchy:
    """Specialized Multi-Memory Storage Architecture for Continuous Improvement."""

    def __init__(self):
        # 1. Trade Memory is backed by persistent SQLite ExperienceMemoryStore
        self.trade_memory = experience_memory
        
        # In-memory aggregated caches
        self._pattern_cache: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            "occurrences": 0,
            "win_count": 0,
            "loss_count": 0,
            "total_pnl": 0.0,
            "avg_pnl": 0.0,
            "symbols": set(),
            "regimes": set()
        })
        
        self._strategy_regime_matrix: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(
            lambda: defaultdict(lambda: {"trades": 0, "wins": 0, "pnl": 0.0, "expectancy_bps": 0.0})
        )
        
        self._execution_memory: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"samples": 0, "avg_slippage_bps": 0.0, "avg_latency_ms": 0.0, "rejection_rate": 0.0}
        )

        self._arbitrage_failure_memory: List[Dict[str, Any]] = []

    def ingest_experience(self, exp: TradeExperience):
        """Update specialized memories with new trade experience."""
        # 1. Pattern Memory Clustering: Key = (Regime, Direction, ErrorClassification)
        pattern_key = f"{exp.market_regime}_{exp.direction}_{exp.error_classification}"
        p = self._pattern_cache[pattern_key]
        p["occurrences"] += 1
        if exp.realized_pnl > 0:
            p["win_count"] += 1
        elif exp.realized_pnl < 0:
            p["loss_count"] += 1
        p["total_pnl"] += exp.realized_pnl
        p["avg_pnl"] = p["total_pnl"] / p["occurrences"]
        p["symbols"].add(exp.symbol)
        p["regimes"].add(exp.market_regime)

        # 2. Strategy vs Regime Memory
        s_cell = self._strategy_regime_matrix[exp.strategy][exp.market_regime]
        s_cell["trades"] += 1
        if exp.realized_pnl > 0:
            s_cell["wins"] += 1
        s_cell["pnl"] += exp.realized_pnl
        alloc = exp.allocation_usd if exp.allocation_usd > 0 else 1000.0
        s_cell["expectancy_bps"] = round((s_cell["pnl"] / (s_cell["trades"] * alloc)) * 10000.0, 2)

        # 3. Execution Memory
        venue_key = f"{exp.market}_{exp.symbol}"
        ex = self._execution_memory[venue_key]
        ex["samples"] += 1
        ex["avg_slippage_bps"] = (ex["avg_slippage_bps"] * (ex["samples"] - 1) + (exp.slippage_usd / max(1.0, exp.allocation_usd) * 10000.0)) / ex["samples"]
        ex["avg_latency_ms"] = (ex["avg_latency_ms"] * (ex["samples"] - 1) + exp.execution_latency_ms) / ex["samples"]

    def record_arbitrage_failure(self, failure_record: Dict[str, Any]):
        """Store failed or friction-collapsed arbitrage structure in Arbitrage Failure Memory."""
        self._arbitrage_failure_memory.append({
            "timestamp": time.time(),
            "symbol": failure_record.get("symbol", "BTC/USDT"),
            "buy_exchange": failure_record.get("buy_exchange", "BINANCE"),
            "sell_exchange": failure_record.get("sell_exchange", "BYBIT"),
            "gross_spread_pct": failure_record.get("gross_spread_pct", 0.0),
            "fees_bps": failure_record.get("fees_bps", 15.0),
            "slippage_bps": failure_record.get("slippage_bps", 2.0),
            "net_edge_pct": failure_record.get("net_edge_pct", 0.0),
            "failure_reason": failure_record.get("rejection_reason", "FEE_FRICTION_REJECT")
        })

    def get_pattern_memory(self) -> Dict[str, Any]:
        return {
            k: {
                "occurrences": v["occurrences"],
                "win_rate_pct": round((v["win_count"] / max(1, v["occurrences"])) * 100.0, 2),
                "avg_pnl": round(v["avg_pnl"], 2),
                "symbols_count": len(v["symbols"]),
                "regimes": list(v["regimes"])
            }
            for k, v in self._pattern_cache.items()
        }

    def get_strategy_regime_matrix(self) -> Dict[str, Any]:
        return {
            strat: {
                regime: {
                    "trades": data["trades"],
                    "win_rate_pct": round((data["wins"] / max(1, data["trades"])) * 100.0, 2),
                    "expectancy_bps": data["expectancy_bps"],
                    "total_pnl": round(data["pnl"], 2)
                }
                for regime, data in regimes.items()
            }
            for strat, regimes in self._strategy_regime_matrix.items()
        }

    def get_arbitrage_failures(self, limit: int = 50) -> List[Dict[str, Any]]:
        return self._arbitrage_failure_memory[-limit:]

# Global Singleton
learning_memories = LearningMemoryHierarchy()
