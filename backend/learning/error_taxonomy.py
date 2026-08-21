from enum import Enum
from typing import Dict, Any, List

class TradeErrorCategory(str, Enum):
    NONE = "NONE"
    LATE_ENTRY = "LATE_ENTRY"
    FALSE_BREAKOUT = "FALSE_BREAKOUT"
    REGIME_MISCLASSIFICATION = "REGIME_MISCLASSIFICATION"
    MEAN_REVERSION_TRAP = "MEAN_REVERSION_TRAP"
    TREND_REVERSAL = "TREND_REVERSAL"
    OVERCONFIDENCE = "OVERCONFIDENCE"
    POOR_CALIBRATION = "POOR_CALIBRATION"
    EXCESS_CORRELATION = "EXCESS_CORRELATION"
    OVERSIZING = "OVERSIZING"
    UNDERHEDGING = "UNDERHEDGING"
    HIGH_SLIPPAGE = "HIGH_SLIPPAGE"
    STALE_DATA = "STALE_DATA"
    LEG_FAILURE = "LEG_FAILURE"
    PARTIAL_FILL = "PARTIAL_FILL"
    EXCESS_FEES = "EXCESS_FEES"
    LATENCY = "LATENCY"
    WRONG_EXIT = "WRONG_EXIT"
    THESIS_INVALIDATION = "THESIS_INVALIDATION"
    LIQUIDITY_SHOCK = "LIQUIDITY_SHOCK"
    MODEL_DECAY = "MODEL_DECAY"
    NO_TRADE_MISSED = "NO_TRADE_MISSED"
    OTHER = "OTHER"

class ErrorTaxonomyClassifier:
    """Quantitative Rule-Based Error Taxonomy Classifier.
    
    Categorizes every unprofitable or degraded trade into specific diagnostic error types.
    """

    def classify_trade_error(
        self,
        realized_pnl: float,
        features: Dict[str, Any],
        market_regime: str,
        direction: str,
        expected_edge_bps: float,
        fees_usd: float,
        slippage_usd: float,
        latency_ms: float,
        holding_time_seconds: float,
        exit_reason: str
    ) -> TradeErrorCategory:
        if realized_pnl >= 0.0:
            return TradeErrorCategory.NONE

        rsi = float(features.get("rsi", 50.0))
        adx = float(features.get("adx", 20.0))
        ema_dist = float(features.get("ema20_dist_pct", 0.0))
        quote_age_ms = float(features.get("quote_age_ms", 0.0))
        notional_usd = float(features.get("notional_usd", 1000.0))

        # 1. High Friction / Fees / Slippage
        friction_usd = fees_usd + slippage_usd
        expected_dollar_edge = notional_usd * (expected_edge_bps / 10000.0)
        if friction_usd >= expected_dollar_edge and expected_dollar_edge > 0:
            if fees_usd > slippage_usd:
                return TradeErrorCategory.EXCESS_FEES
            return TradeErrorCategory.HIGH_SLIPPAGE

        # 2. Latency / Stale Quotes
        if quote_age_ms > 1000.0 or latency_ms > 50.0:
            return TradeErrorCategory.STALE_DATA if quote_age_ms > 1000.0 else TradeErrorCategory.LATENCY

        # 3. Late Entry / Chasing overextended market
        if (direction == "LONG" and rsi > 72.0 and ema_dist > 3.0) or (direction == "SHORT" and rsi < 28.0 and ema_dist < -3.0):
            return TradeErrorCategory.LATE_ENTRY

        # 4. Mean Reversion Trap (fighting strong trend)
        if adx > 32.0 and ("RANGE" in market_regime or "MEAN_REVERSION" in market_regime):
            return TradeErrorCategory.MEAN_REVERSION_TRAP

        # 5. False Breakout
        if "BREAKOUT" in market_regime and holding_time_seconds < 180.0:
            return TradeErrorCategory.FALSE_BREAKOUT

        # 6. Regime Misclassification
        if "CHOP" in market_regime and "TRENDING" in features.get("true_regime", ""):
            return TradeErrorCategory.REGIME_MISCLASSIFICATION

        # 7. Thesis Invalidation / Stop Loss Hit
        if exit_reason in ["STOP_LOSS", "THESIS_INVALIDATED"]:
            return TradeErrorCategory.THESIS_INVALIDATION

        return TradeErrorCategory.OTHER

# Global Singleton
error_classifier = ErrorTaxonomyClassifier()
