import time
import math
import numpy as np
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple

@dataclass
class CandidateDiagnosticRecord:
    pair: str
    timestamp: float
    price: float
    regime: str
    signal_direction: str              # LONG, SHORT, NEUTRAL
    signal_strength: float            # [-1.0, +1.0]
    calibrated_probability: float     # [0.0, 1.0]
    expected_gross_edge_bps: float
    estimated_friction_bps: float
    expected_net_edge_bps: float
    pair_hurdle_bps: float
    decision: str                     # TRADE, NO_TRADE
    rejection_reason: str
    secondary_rejection_reason: str
    entry_quality: str                # EARLY, OPTIMAL, MID, LATE, EXHAUSTED, REJECT, N/A
    risk_state: str
    portfolio_state: str
    learning_context: str
    # Detailed technical indicators
    rsi: float = 50.0
    adx: float = 25.0
    ema_alignment: str = "MIXED"      # BULLISH, BEARISH, MIXED
    macd_signal: str = "NEUTRAL"      # BULLISH, BEARISH, NEUTRAL
    volume_spike_ratio: float = 1.0
    atr_pct: float = 2.0
    extension_ratio: float = 0.0
    reversal_risk_score: float = 0.0
    # Future outcome if evaluated
    simulated_future_pnl_usd: Optional[float] = None
    is_counterfactual_win: Optional[bool] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CandidateDiagnosticLogger:
    """
    Phase 46.3 Diagnostic Telemetry Engine.
    Records every evaluated historical candidate, classifies rejection root causes,
    computes edge percentiles, regime matrices, entry quality, and counterfactuals.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CandidateDiagnosticLogger, cls).__new__(cls)
            cls._instance.records_by_pair: Dict[str, List[CandidateDiagnosticRecord]] = {}
        return cls._instance

    def clear_records(self, pair: Optional[str] = None):
        if pair:
            self.records_by_pair[pair] = []
        else:
            self.records_by_pair.clear()

    def record_candidate(self, record: CandidateDiagnosticRecord):
        if record.pair not in self.records_by_pair:
            self.records_by_pair[record.pair] = []
        self.records_by_pair[record.pair].append(record)

    def get_records(self, pair: str) -> List[CandidateDiagnosticRecord]:
        return self.records_by_pair.get(pair, [])

    # -------------------------------------------------------------------------
    # 1. REJECTION CATEGORIZATION
    # -------------------------------------------------------------------------
    def categorize_rejection(self, reason: str, entry_q: str, net_edge: float, gross_edge: float, prob: float, direction: str) -> str:
        reason_upper = (reason or "").upper()
        if "NEWS" in reason_upper:
            return "NEWS_RISK"
        if "LEARNING" in reason_upper:
            return "LEARNING_VETO"
        if "PORTFOLIO" in reason_upper or "CORRELATION" in reason_upper:
            return "PORTFOLIO_RISK"
        if "REVERSAL" in reason_upper or "TRAP" in reason_upper:
            return "REVERSAL_RISK"
        if "LATE" in reason_upper or entry_q in ["LATE", "EXHAUSTED"]:
            return "LATE_ENTRY"
        if direction == "NEUTRAL" or "NEUTRAL" in reason_upper:
            return "SIGNAL_WEAK"
        if prob < 0.510:
            return "LOW_PROBABILITY"
        if gross_edge <= 0:
            return "LOW_GROSS_EDGE"
        if net_edge < 0 and gross_edge > 0:
            return "FRICTION_TOO_HIGH"
        if "FRICTION" in reason_upper or "NET EDGE" in reason_upper or "HURDLE" in reason_upper:
            return "LOW_NET_EDGE"
        if "REGIME" in reason_upper:
            return "REGIME_MISMATCH"
        if "LIQUIDITY" in reason_upper:
            return "LIQUIDITY"
        if "EXECUTION" in reason_upper:
            return "EXECUTION_COST"
        return "LOW_NET_EDGE"

    # -------------------------------------------------------------------------
    # 2. REJECTION DISTRIBUTION
    # -------------------------------------------------------------------------
    def compute_rejection_distribution(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        total_candidates = len(records)
        if total_candidates == 0:
            return {
                "total_candidates": 0,
                "trades_count": 0,
                "no_trades_count": 0,
                "counts": {},
                "percentages": {},
                "top_rejection_reason": "NO_CANDIDATES"
            }

        trade_count = sum(1 for r in records if r.decision == "TRADE")
        no_trade_count = sum(1 for r in records if r.decision == "NO_TRADE")

        categories = [
            "SIGNAL_WEAK", "LOW_PROBABILITY", "LOW_GROSS_EDGE", "FRICTION_TOO_HIGH",
            "LOW_NET_EDGE", "LATE_ENTRY", "REVERSAL_RISK", "REGIME_MISMATCH",
            "NEWS_RISK", "LEARNING_VETO", "PORTFOLIO_RISK", "CORRELATION",
            "LIQUIDITY", "EXECUTION_COST", "OTHER"
        ]
        counts = {cat: 0 for cat in categories}

        for r in records:
            if r.decision == "NO_TRADE":
                cat = self.categorize_rejection(
                    reason=r.rejection_reason,
                    entry_q=r.entry_quality,
                    net_edge=r.expected_net_edge_bps,
                    gross_edge=r.expected_gross_edge_bps,
                    prob=r.calibrated_probability,
                    direction=r.signal_direction
                )
                if cat in counts:
                    counts[cat] += 1
                else:
                    counts["OTHER"] += 1

        rejections_total = max(1, no_trade_count)
        percentages = {cat: round((cnt / rejections_total) * 100.0, 1) for cat, cnt in counts.items()}

        # Identify top rejection category
        top_cat = max(counts.items(), key=lambda x: x[1])[0] if counts else "NONE"

        return {
            "total_candidates": total_candidates,
            "trades_count": trade_count,
            "no_trades_count": no_trade_count,
            "counts": counts,
            "percentages": percentages,
            "top_rejection_reason": top_cat
        }

    # -------------------------------------------------------------------------
    # 3. EDGE PERCENTILES & COMPARISONS
    # -------------------------------------------------------------------------
    def compute_edge_distribution(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        if not records:
            return {
                "gross_edge": {"p10": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "p90": 0.0, "max": 0.0},
                "friction": {"p10": 0.0, "median": 0.0, "p90": 0.0},
                "net_edge": {"p10": 0.0, "p25": 0.0, "median": 0.0, "p75": 0.0, "p90": 0.0, "max": 0.0},
                "gross_above_zero_count": 0,
                "gross_above_friction_count": 0,
                "net_above_zero_count": 0,
                "net_above_hurdle_count": 0
            }

        gross = [r.expected_gross_edge_bps for r in records]
        fric = [r.estimated_friction_bps for r in records]
        net = [r.expected_net_edge_bps for r in records]
        hurdle = records[0].pair_hurdle_bps if records else 4.0

        def calc_pcts(arr):
            return {
                "p10": round(float(np.percentile(arr, 10)), 2),
                "p25": round(float(np.percentile(arr, 25)), 2),
                "median": round(float(np.median(arr)), 2),
                "p75": round(float(np.percentile(arr, 75)), 2),
                "p90": round(float(np.percentile(arr, 90)), 2),
                "max": round(float(np.max(arr)), 2)
            }

        return {
            "gross_edge": calc_pcts(gross),
            "friction": {
                "p10": round(float(np.percentile(fric, 10)), 2),
                "median": round(float(np.median(fric)), 2),
                "p90": round(float(np.percentile(fric, 90)), 2)
            },
            "net_edge": calc_pcts(net),
            "gross_above_zero_count": sum(1 for g in gross if g > 0),
            "gross_above_friction_count": sum(1 for g, f in zip(gross, fric) if g > f),
            "net_above_zero_count": sum(1 for n in net if n > 0),
            "net_above_hurdle_count": sum(1 for n in net if n >= hurdle)
        }

    # -------------------------------------------------------------------------
    # 4. SIGNAL DISTRIBUTION
    # -------------------------------------------------------------------------
    def compute_signal_distribution(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        if not records:
            return {}

        buy_count = sum(1 for r in records if r.signal_direction == "LONG")
        sell_count = sum(1 for r in records if r.signal_direction == "SHORT")
        neutral_count = sum(1 for r in records if r.signal_direction == "NEUTRAL")
        no_trade_count = sum(1 for r in records if r.decision == "NO_TRADE")

        rsis = [r.rsi for r in records]
        adxs = [r.adx for r in records]
        vol_spikes = [r.volume_spike_ratio for r in records]
        atr_pcts = [r.atr_pct for r in records]

        ema_bullish = sum(1 for r in records if r.ema_alignment == "BULLISH")
        ema_bearish = sum(1 for r in records if r.ema_alignment == "BEARISH")
        ema_mixed = sum(1 for r in records if r.ema_alignment == "MIXED")

        macd_bullish = sum(1 for r in records if r.macd_signal == "BULLISH")
        macd_bearish = sum(1 for r in records if r.macd_signal == "BEARISH")
        macd_neutral = sum(1 for r in records if r.macd_signal == "NEUTRAL")

        n = len(records)
        return {
            "buy_signals": buy_count,
            "sell_signals": sell_count,
            "neutral_signals": neutral_count,
            "no_trade_count": no_trade_count,
            "rsi": {
                "p10": round(float(np.percentile(rsis, 10)), 1),
                "p50": round(float(np.median(rsis)), 1),
                "p90": round(float(np.percentile(rsis, 90)), 1)
            },
            "adx": {
                "p10": round(float(np.percentile(adxs, 10)), 1),
                "p50": round(float(np.median(adxs)), 1),
                "p90": round(float(np.percentile(adxs, 90)), 1)
            },
            "volume_spike_ratio": {
                "p10": round(float(np.percentile(vol_spikes, 10)), 2),
                "p50": round(float(np.median(vol_spikes)), 2),
                "p90": round(float(np.percentile(vol_spikes, 90)), 2)
            },
            "atr_pct": {
                "p10": round(float(np.percentile(atr_pcts, 10)), 2),
                "p50": round(float(np.median(atr_pcts)), 2),
                "p90": round(float(np.percentile(atr_pcts, 90)), 2)
            },
            "ema_alignment": {
                "bullish_pct": round((ema_bullish / n) * 100.0, 1),
                "bearish_pct": round((ema_bearish / n) * 100.0, 1),
                "mixed_pct": round((ema_mixed / n) * 100.0, 1)
            },
            "macd_relationship": {
                "bullish_pct": round((macd_bullish / n) * 100.0, 1),
                "bearish_pct": round((macd_bearish / n) * 100.0, 1),
                "neutral_pct": round((macd_neutral / n) * 100.0, 1)
            }
        }

    # -------------------------------------------------------------------------
    # 5. REGIME DISTRIBUTION
    # -------------------------------------------------------------------------
    def compute_regime_distribution(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        regimes_list = [
            "BULL_TREND", "BEAR_TREND", "SIDEWAYS_RANGE",
            "HIGH_VOL_BREAKOUT", "LOW_VOL_COMPRESSION", "RECOVERY_REVERSAL", "OTHER"
        ]
        breakdown = {}
        for reg in regimes_list:
            matching = [r for r in records if (r.regime == reg or (reg == "OTHER" and r.regime not in regimes_list))]
            c_cnt = len(matching)
            s_cnt = sum(1 for r in matching if r.signal_direction in ["LONG", "SHORT"])
            t_cnt = sum(1 for r in matching if r.decision == "TRADE")
            r_cnt = sum(1 for r in matching if r.decision == "NO_TRADE")
            avg_net = round(float(np.mean([r.expected_net_edge_bps for r in matching])), 2) if matching else 0.0
            avg_prob = round(float(np.mean([r.calibrated_probability for r in matching])), 3) if matching else 0.0

            breakdown[reg] = {
                "candidates": c_cnt,
                "signals": s_cnt,
                "trades": t_cnt,
                "rejects": r_cnt,
                "avg_net_edge_bps": avg_net,
                "avg_probability": avg_prob
            }
        return breakdown

    # -------------------------------------------------------------------------
    # 6. ENTRY QUALITY DIAGNOSTIC
    # -------------------------------------------------------------------------
    def compute_entry_quality_diagnostic(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        if not records:
            return {}

        qual_counts = {"EARLY": 0, "OPTIMAL": 0, "MID": 0, "LATE": 0, "EXHAUSTED": 0, "REJECT": 0, "N/A": 0}
        for r in records:
            eq = r.entry_quality
            if eq in qual_counts:
                qual_counts[eq] += 1
            else:
                qual_counts["N/A"] += 1

        n = len(records)
        late_or_exhausted = qual_counts["LATE"] + qual_counts["EXHAUSTED"]
        return {
            "counts": qual_counts,
            "percentages": {k: round((v / n) * 100.0, 1) for k, v in qual_counts.items()},
            "late_or_exhausted_count": late_or_exhausted,
            "late_or_exhausted_pct": round((late_or_exhausted / n) * 100.0, 1)
        }

    # -------------------------------------------------------------------------
    # 7. FRICTION DIAGNOSTIC
    # -------------------------------------------------------------------------
    def compute_friction_diagnostic(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        if not records:
            return {}

        edge_gt_friction = sum(1 for r in records if r.expected_gross_edge_bps > (r.estimated_friction_bps + 2.0))
        edge_eq_friction = sum(1 for r in records if abs(r.expected_gross_edge_bps - r.estimated_friction_bps) <= 2.0)
        edge_lt_friction = sum(1 for r in records if r.expected_gross_edge_bps < (r.estimated_friction_bps - 2.0))
        n = len(records)

        return {
            "edge_gt_friction_count": edge_gt_friction,
            "edge_gt_friction_pct": round((edge_gt_friction / n) * 100.0, 1),
            "edge_approx_friction_count": edge_eq_friction,
            "edge_approx_friction_pct": round((edge_eq_friction / n) * 100.0, 1),
            "edge_lt_friction_count": edge_lt_friction,
            "edge_lt_friction_pct": round((edge_lt_friction / n) * 100.0, 1),
            "average_friction_bps": round(float(np.mean([r.estimated_friction_bps for r in records])), 2)
        }

    # -------------------------------------------------------------------------
    # 8. PROBABILITY / CALIBRATION DIAGNOSTIC
    # -------------------------------------------------------------------------
    def compute_probability_diagnostic(self, pair: str) -> Dict[str, Any]:
        records = self.get_records(pair)
        if not records:
            return {"status": "NO_DATA"}

        probs = [r.calibrated_probability for r in records]
        trade_records = [r for r in records if r.decision == "TRADE"]

        return {
            "distribution": {
                "p10": round(float(np.percentile(probs, 10)), 3),
                "median": round(float(np.median(probs)), 3),
                "p90": round(float(np.percentile(probs, 90)), 3),
                "min": round(float(np.min(probs)), 3),
                "max": round(float(np.max(probs)), 3)
            },
            "trade_sample_count": len(trade_records),
            "calibration_status": "CALIBRATION NOT YET VALIDATED" if len(trade_records) < 10 else "VALIDATED"
        }

    # -------------------------------------------------------------------------
    # 9. USER DASHBOARD TRANSPARENT EXPLANATION
    # -------------------------------------------------------------------------
    def generate_why_no_trades_explanation(self, pair: str) -> Dict[str, Any]:
        rej_dist = self.compute_rejection_distribution(pair)
        edge_dist = self.compute_edge_distribution(pair)
        sig_dist = self.compute_signal_distribution(pair)

        total_c = rej_dist.get("total_candidates", 0)
        top_reason = rej_dist.get("top_rejection_reason", "LOW_NET_EDGE")
        top_pct = rej_dist.get("percentages", {}).get(top_reason, 0.0)

        hurdle = edge_dist.get("net_edge", {}).get("median", 0.0)
        net_above_hurdle = edge_dist.get("net_above_hurdle_count", 0)

        if top_reason == "SIGNAL_WEAK":
            text = f"Bot did not trade because {top_pct}% of evaluated candles showed neutral technical indicators without directional conviction."
        elif top_reason == "LOW_NET_EDGE":
            text = f"Bot did not trade because {top_pct}% of candidates had an expected net edge below the required threshold."
        elif top_reason == "FRICTION_TOO_HIGH":
            text = f"Bot did not trade because {top_pct}% of opportunities were eroded by taker fees and execution slippage."
        elif top_reason == "LATE_ENTRY":
            text = f"Bot did not trade because {top_pct}% of candidate setups triggered late-cycle ATR extension traps."
        else:
            text = f"Bot did not trade because candidates were filtered by {top_reason} ({top_pct}% of evaluations)."

        return {
            "pair": pair,
            "total_candidates": total_c,
            "signals_generated": sig_dist.get("buy_signals", 0) + sig_dist.get("sell_signals", 0),
            "rejected_count": rej_dist.get("no_trades_count", 0),
            "top_rejection_reason": top_reason,
            "top_rejection_pct": top_pct,
            "median_gross_edge_bps": edge_dist.get("gross_edge", {}).get("median", 0.0),
            "median_friction_bps": edge_dist.get("friction", {}).get("median", 0.0),
            "median_net_edge_bps": edge_dist.get("net_edge", {}).get("median", 0.0),
            "pair_hurdle_bps": self.get_records(pair)[0].pair_hurdle_bps if self.get_records(pair) else 4.0,
            "candidates_above_hurdle": net_above_hurdle,
            "explanation_text": text
        }

# Global Singleton
candidate_diagnostic_logger = CandidateDiagnosticLogger()
