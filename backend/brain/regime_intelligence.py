import time
import math
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Tuple
from loguru import logger

class MarketRegimeType(str, Enum):
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    SIDEWAYS_RANGE = "SIDEWAYS_RANGE"
    HIGH_VOL_BREAKOUT = "HIGH_VOL_BREAKOUT"
    LOW_VOL_COMPRESSION = "LOW_VOL_COMPRESSION"
    MEAN_REVERSION = "MEAN_REVERSION"
    PANIC_LIQUIDATION = "PANIC_LIQUIDATION"
    RECOVERY_REVERSAL = "RECOVERY_REVERSAL"
    EVENT_DRIVEN = "EVENT_DRIVEN"
    LIQUIDITY_SHOCK = "LIQUIDITY_SHOCK"

@dataclass
class RegimeState:
    regime: MarketRegimeType
    confidence: float                  # [0.0, 1.0] Quantitative fit of regime rules
    stability: float                   # [0.0, 1.0] Persistence across rolling time horizons
    transition_probabilities: Dict[str, float]
    description: str
    recommended_alphas: List[str]
    forbidden_alphas: List[str]
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["regime"] = self.regime.value
        return d

class RegimeIntelligenceEngine:
    """
    Phase 44.3 Superintelligent Multi-Factor Market Regime Detection Engine.
    Evaluates 10 distinct macroeconomic & microstructure market regimes.
    """

    # Baseline transition matrix across regimes
    DEFAULT_TRANSITIONS = {
        MarketRegimeType.BULL_TREND: {
            "BULL_TREND": 0.70, "SIDEWAYS_RANGE": 0.15, "HIGH_VOL_BREAKOUT": 0.10, "MEAN_REVERSION": 0.05
        },
        MarketRegimeType.BEAR_TREND: {
            "BEAR_TREND": 0.65, "PANIC_LIQUIDATION": 0.15, "RECOVERY_REVERSAL": 0.10, "SIDEWAYS_RANGE": 0.10
        },
        MarketRegimeType.SIDEWAYS_RANGE: {
            "SIDEWAYS_RANGE": 0.60, "LOW_VOL_COMPRESSION": 0.20, "HIGH_VOL_BREAKOUT": 0.10, "MEAN_REVERSION": 0.10
        },
        MarketRegimeType.HIGH_VOL_BREAKOUT: {
            "BULL_TREND": 0.40, "BEAR_TREND": 0.40, "HIGH_VOL_BREAKOUT": 0.15, "SIDEWAYS_RANGE": 0.05
        },
        MarketRegimeType.LOW_VOL_COMPRESSION: {
            "HIGH_VOL_BREAKOUT": 0.55, "LOW_VOL_COMPRESSION": 0.30, "SIDEWAYS_RANGE": 0.15
        },
        MarketRegimeType.MEAN_REVERSION: {
            "SIDEWAYS_RANGE": 0.50, "BULL_TREND": 0.25, "BEAR_TREND": 0.25
        },
        MarketRegimeType.PANIC_LIQUIDATION: {
            "RECOVERY_REVERSAL": 0.45, "BEAR_TREND": 0.35, "PANIC_LIQUIDATION": 0.20
        },
        MarketRegimeType.RECOVERY_REVERSAL: {
            "BULL_TREND": 0.45, "SIDEWAYS_RANGE": 0.35, "BEAR_TREND": 0.20
        },
        MarketRegimeType.EVENT_DRIVEN: {
            "HIGH_VOL_BREAKOUT": 0.40, "SIDEWAYS_RANGE": 0.30, "PANIC_LIQUIDATION": 0.30
        },
        MarketRegimeType.LIQUIDITY_SHOCK: {
            "HIGH_VOL_BREAKOUT": 0.40, "PANIC_LIQUIDATION": 0.30, "SIDEWAYS_RANGE": 0.30
        }
    }

    ALPHA_SUITABILITY = {
        MarketRegimeType.BULL_TREND: {
            "recommended": ["TrendFollowing", "MomentumAlpha", "BreakoutAlpha"],
            "forbidden": ["MeanReversionShort", "FadeBreakout"]
        },
        MarketRegimeType.BEAR_TREND: {
            "recommended": ["TrendFollowingShort", "MomentumAlphaShort", "VolatilityBreakdown"],
            "forbidden": ["BuyDipLong", "MeanReversionLong"]
        },
        MarketRegimeType.SIDEWAYS_RANGE: {
            "recommended": ["MeanReversion", "GridMarketMaking", "VWAPMeanReversion", "StatisticalArbitrage"],
            "forbidden": ["BreakoutAlpha", "AggressiveTrend"]
        },
        MarketRegimeType.HIGH_VOL_BREAKOUT: {
            "recommended": ["BreakoutAlpha", "VolatilityMomentum", "CrossExchangeArbitrage"],
            "forbidden": ["MeanReversion", "GridMarketMaking"]
        },
        MarketRegimeType.LOW_VOL_COMPRESSION: {
            "recommended": ["VolatilityStraddle", "PreBreakoutAccumulation", "StatisticalArbitrage"],
            "forbidden": ["AggressiveMomentum"]
        },
        MarketRegimeType.MEAN_REVERSION: {
            "recommended": ["RSIOversoldReversion", "BollingerBandRebound", "OrderbookAbsorption"],
            "forbidden": ["TrendChasing"]
        },
        MarketRegimeType.PANIC_LIQUIDATION: {
            "recommended": ["CrossExchangeArbitrage", "LiquidationHarvester", "PostCascadeRebound"],
            "forbidden": ["NakedLongTrend", "StaticGrid"]
        },
        MarketRegimeType.RECOVERY_REVERSAL: {
            "recommended": ["VBottomAbsorption", "MomentumReversalLong", "OrderbookImbalance"],
            "forbidden": ["LateShorts"]
        },
        MarketRegimeType.EVENT_DRIVEN: {
            "recommended": ["EventSignalAlpha", "LatencyArbitrage", "WideSpreadMarketMaking"],
            "forbidden": ["DirectionalTrendHolding"]
        },
        MarketRegimeType.LIQUIDITY_SHOCK: {
            "recommended": ["CapitalPreservation", "CrossExchangeArbitrage"],
            "forbidden": ["MarketOrders", "HighLeverage"]
        }
    }

    def __init__(self):
        self.history: List[Tuple[float, MarketRegimeType]] = []
        self.max_history = 100

    def detect_regime(
        self,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_summary: Optional[Dict[str, Any]] = None,
        orderbook_data: Optional[Dict[str, Any]] = None
    ) -> RegimeState:
        """
        Classify live market data into one of 10 quantitative regimes with confidence.
        """
        sentiment_summary = sentiment_summary or {}
        orderbook_data = orderbook_data or {}

        # 1. Feature extraction
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / max(1e-9, current_price)) * 100.0
        adx = float(technical_data.get("adx", 20.0))
        plus_di = float(technical_data.get("plus_di", 25.0))
        minus_di = float(technical_data.get("minus_di", 25.0))
        vol_spike_ratio = float(technical_data.get("volume_spike_ratio", 1.0))
        rsi = float(technical_data.get("rsi", 50.0))
        vwap = float(technical_data.get("vwap", current_price))
        vwap_diff_pct = ((current_price - vwap) / max(1e-9, vwap)) * 100.0
        bb_width_pct = float(technical_data.get("bb_width_pct", 4.0))

        ema_20 = float(technical_data.get("ema_20", current_price))
        ema_50 = float(technical_data.get("ema_50", current_price))
        ema_200 = float(technical_data.get("ema_200", current_price))

        fg_val = float(sentiment_summary.get("fear_greed", {}).get("value", 50.0))
        spread_bps = float(orderbook_data.get("spread_bps", 2.0))
        depth_liquidity_usd = float(orderbook_data.get("depth_liquidity_usd", 100000.0))

        # 2. Rule evaluation matrix with multi-factor scoring
        regime = MarketRegimeType.SIDEWAYS_RANGE
        confidence = 0.60
        desc = "Consolidating Range-Bound Market."

        # Case A: Liquidity Shock / Orderbook Collapse
        if spread_bps >= 15.0 or depth_liquidity_usd < 10000.0:
            regime = MarketRegimeType.LIQUIDITY_SHOCK
            confidence = min(0.95, 0.60 + (spread_bps / 30.0))
            desc = f"Orderbook Liquidity Shock (Spread {spread_bps:.1f} bps, Depth ${depth_liquidity_usd:,.0f})."

        # Case B: Event-Driven News Volatility
        elif fg_val <= 12.0 or fg_val >= 88.0:
            regime = MarketRegimeType.EVENT_DRIVEN
            confidence = 0.88
            desc = f"Extreme Sentiment/News Driven Event (Fear & Greed Index: {fg_val:.0f})."

        # Case C: Panic Liquidation Cascade
        elif (rsi <= 22.0 and vol_spike_ratio >= 2.5 and minus_di > plus_di + 15.0) or (fg_val <= 18.0 and current_price < ema_200 * 0.94):
            regime = MarketRegimeType.PANIC_LIQUIDATION
            confidence = 0.92
            desc = f"Panic Liquidation Cascade (RSI {rsi:.1f}, Volume Spike {vol_spike_ratio:.1f}x, -DI {minus_di:.1f})."

        # Case D: Recovery & V-Reversal
        elif rsi <= 35.0 and vol_spike_ratio >= 2.0 and current_price > vwap and plus_di > minus_di:
            regime = MarketRegimeType.RECOVERY_REVERSAL
            confidence = 0.85
            desc = f"V-Shape Recovery & Absorption Reversal (RSI {rsi:.1f}, Price reclaimed VWAP ${vwap:,.2f})."

        # Case E: High Volatility Breakout
        elif atr_pct >= 4.0 or (vol_spike_ratio >= 2.5 and abs(vwap_diff_pct) >= 2.0):
            regime = MarketRegimeType.HIGH_VOL_BREAKOUT
            confidence = 0.86
            desc = f"High Volatility Breakout Expansion (ATR {atr_pct:.1f}%, Vol {vol_spike_ratio:.1f}x)."

        # Case F: Low Volatility Compression (Squeeze)
        elif atr_pct <= 1.2 and bb_width_pct <= 2.0 and vol_spike_ratio <= 0.65:
            regime = MarketRegimeType.LOW_VOL_COMPRESSION
            confidence = 0.82
            desc = f"Volatility Squeeze / Range Compression (ATR {atr_pct:.2f}%, BB Width {bb_width_pct:.1f}%)."

        # Case G: Mean Reversion Extremes
        elif (rsi >= 75.0 or rsi <= 25.0) and adx < 22.0:
            regime = MarketRegimeType.MEAN_REVERSION
            confidence = 0.80
            desc = f"Overextended Mean Reversion Zone (RSI {rsi:.1f}, ADX {adx:.1f} indicates weak trend)."

        # Case H: Strong Bull Trend
        elif adx >= 24.0 and plus_di > minus_di and current_price > ema_20 > ema_50:
            regime = MarketRegimeType.BULL_TREND
            confidence = min(0.95, 0.65 + (adx / 100.0) + (0.1 if current_price > ema_200 else 0.0))
            desc = f"Strong Bull Trend (ADX {adx:.1f}, +DI {plus_di:.1f} > -DI {minus_di:.1f}, Price > EMA20 > EMA50)."

        # Case I: Strong Bear Trend
        elif adx >= 24.0 and minus_di > plus_di and current_price < ema_20 < ema_50:
            regime = MarketRegimeType.BEAR_TREND
            confidence = min(0.95, 0.65 + (adx / 100.0) + (0.1 if current_price < ema_200 else 0.0))
            desc = f"Strong Bear Trend (ADX {adx:.1f}, -DI {minus_di:.1f} > +DI {plus_di:.1f}, Price < EMA20 < EMA50)."

        # Case J: Default Range
        else:
            regime = MarketRegimeType.SIDEWAYS_RANGE
            confidence = 0.70
            desc = f"Range-Bound Consolidation (ADX {adx:.1f} < 24.0, Price near VWAP ${vwap:,.2f})."

        # 3. Calculate Stability Score
        now = time.time()
        self.history.append((now, regime))
        if len(self.history) > self.max_history:
            self.history.pop(0)

        # Fraction of recent 10 samples matching current regime
        recent_matches = sum(1 for _, r in self.history[-10:] if r == regime)
        stability = round(recent_matches / max(1.0, float(min(10, len(self.history)))), 2)

        transitions = self.DEFAULT_TRANSITIONS.get(regime, {"SIDEWAYS_RANGE": 0.5, "HIGH_VOL_BREAKOUT": 0.5})
        suitability = self.ALPHA_SUITABILITY.get(regime, {"recommended": ["StatisticalArbitrage"], "forbidden": []})

        return RegimeState(
            regime=regime,
            confidence=round(confidence, 2),
            stability=stability,
            transition_probabilities=transitions,
            description=desc,
            recommended_alphas=suitability["recommended"],
            forbidden_alphas=suitability["forbidden"],
            timestamp=now
        )

# Global Singleton
regime_engine = RegimeIntelligenceEngine()
