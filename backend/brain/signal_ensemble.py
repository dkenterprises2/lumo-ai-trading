from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from .regime_intelligence import MarketRegimeType, RegimeState

@dataclass
class AlphaVote:
    alpha_family: str
    direction: str             # LONG, SHORT, NEUTRAL
    raw_score: float           # [0.0, 100.0]
    weight: float              # Regime-adjusted weight
    confidence: float          # [0.0, 1.0]
    reason: str

@dataclass
class EnsembleSignal:
    symbol: str
    composite_score: float     # [0.0, 100.0]
    direction: str             # LONG, SHORT, NEUTRAL
    consensus_pct: float       # [0.0, 100.0] % of alpha models agreeing on direction
    active_regime: str
    alpha_votes: List[Dict[str, Any]]
    dominant_factor: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MultiModelAlphaEnsemble:
    """
    Phase 44.3 Multi-Model Alpha Ensemble Engine.
    Combines 7 independent alpha families with regime-adaptive dynamic meta-weights.
    """

    # Base weights across regimes
    REGIME_WEIGHT_MATRIX = {
        MarketRegimeType.BULL_TREND: {
            "trend": 0.35, "momentum": 0.25, "breakout": 0.20, "microstructure": 0.10, "mean_reversion": 0.00, "sentiment": 0.10
        },
        MarketRegimeType.BEAR_TREND: {
            "trend": 0.35, "momentum": 0.25, "breakout": 0.20, "microstructure": 0.10, "mean_reversion": 0.00, "sentiment": 0.10
        },
        MarketRegimeType.SIDEWAYS_RANGE: {
            "mean_reversion": 0.40, "microstructure": 0.25, "trend": 0.05, "momentum": 0.10, "breakout": 0.00, "sentiment": 0.20
        },
        MarketRegimeType.HIGH_VOL_BREAKOUT: {
            "breakout": 0.40, "momentum": 0.30, "microstructure": 0.15, "trend": 0.15, "mean_reversion": 0.00, "sentiment": 0.00
        },
        MarketRegimeType.LOW_VOL_COMPRESSION: {
            "microstructure": 0.35, "mean_reversion": 0.30, "sentiment": 0.20, "trend": 0.10, "breakout": 0.05, "momentum": 0.00
        },
        MarketRegimeType.MEAN_REVERSION: {
            "mean_reversion": 0.50, "microstructure": 0.25, "momentum": 0.15, "sentiment": 0.10, "trend": 0.00, "breakout": 0.00
        },
        MarketRegimeType.PANIC_LIQUIDATION: {
            "microstructure": 0.40, "sentiment": 0.30, "momentum": 0.20, "mean_reversion": 0.10, "trend": 0.00, "breakout": 0.00
        },
        MarketRegimeType.RECOVERY_REVERSAL: {
            "momentum": 0.35, "microstructure": 0.30, "mean_reversion": 0.20, "trend": 0.10, "breakout": 0.05, "sentiment": 0.00
        },
        MarketRegimeType.EVENT_DRIVEN: {
            "sentiment": 0.45, "microstructure": 0.30, "momentum": 0.15, "breakout": 0.10, "trend": 0.00, "mean_reversion": 0.00
        },
        MarketRegimeType.LIQUIDITY_SHOCK: {
            "microstructure": 0.60, "sentiment": 0.20, "mean_reversion": 0.20, "trend": 0.00, "breakout": 0.00, "momentum": 0.00
        }
    }

    def evaluate_ensemble(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        regime_state: RegimeState,
        orderbook_data: Optional[Dict[str, Any]] = None
    ) -> EnsembleSignal:
        orderbook_data = orderbook_data or {}
        regime = regime_state.regime
        weights = self.REGIME_WEIGHT_MATRIX.get(regime, self.REGIME_WEIGHT_MATRIX[MarketRegimeType.SIDEWAYS_RANGE])

        votes: List[AlphaVote] = []

        # 1. Trend Alpha Family (EMA 20/50/200 alignment)
        ema_20 = float(technical_data.get("ema_20", current_price))
        ema_50 = float(technical_data.get("ema_50", current_price))
        ema_200 = float(technical_data.get("ema_200", current_price))
        if current_price > ema_20 > ema_50 > ema_200:
            trend_score = 90.0
            trend_dir = "LONG"
            trend_reason = "Strong Bullish Triple EMA Alignment"
        elif current_price < ema_20 < ema_50 < ema_200:
            trend_score = 10.0
            trend_dir = "SHORT"
            trend_reason = "Strong Bearish Triple EMA Alignment"
        else:
            trend_score = 50.0
            trend_dir = "NEUTRAL"
            trend_reason = "Neutral EMA Configuration"
        votes.append(AlphaVote("trend", trend_dir, trend_score, weights.get("trend", 0.0), 0.85, trend_reason))

        # 2. Momentum Alpha Family (MACD & RSI Slope)
        macd_hist = float(technical_data.get("macd_hist", 0.0))
        macd_line = float(technical_data.get("macd", 0.0))
        macd_sig = float(technical_data.get("macd_signal", 0.0))
        if macd_hist > 0 and macd_line > macd_sig:
            mom_score = min(90.0, 70.0 + min(20.0, abs(macd_hist) * 2.0))
            mom_dir = "LONG"
            mom_reason = f"Bullish MACD Momentum (+{macd_hist:.2f})"
        elif macd_hist < 0 and macd_line < macd_sig:
            mom_score = max(10.0, 30.0 - min(20.0, abs(macd_hist) * 2.0))
            mom_dir = "SHORT"
            mom_reason = f"Bearish MACD Momentum ({macd_hist:.2f})"
        else:
            mom_score = 50.0
            mom_dir = "NEUTRAL"
            mom_reason = "Neutral MACD Momentum"
        votes.append(AlphaVote("momentum", mom_dir, mom_score, weights.get("momentum", 0.0), 0.80, mom_reason))

        # 3. Mean Reversion Alpha Family (RSI & Bollinger Extremes)
        rsi = float(technical_data.get("rsi", 50.0))
        bb_upper = float(technical_data.get("bb_upper", current_price * 1.02))
        bb_lower = float(technical_data.get("bb_lower", current_price * 0.98))
        if rsi <= 30.0 or current_price <= bb_lower:
            mr_score = 85.0
            mr_dir = "LONG"
            mr_reason = f"Oversold Mean Reversion Target (RSI {rsi:.1f})"
        elif rsi >= 70.0 or current_price >= bb_upper:
            mr_score = 15.0
            mr_dir = "SHORT"
            mr_reason = f"Overbought Mean Reversion Target (RSI {rsi:.1f})"
        else:
            mr_score = 50.0
            mr_dir = "NEUTRAL"
            mr_reason = "Mid-Range RSI"
        votes.append(AlphaVote("mean_reversion", mr_dir, mr_score, weights.get("mean_reversion", 0.0), 0.75, mr_reason))

        # 4. Breakout Alpha Family (Volume & Donchian Channel)
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))
        if vol_spike >= 2.0 and current_price > ema_20:
            bo_score = 90.0
            bo_dir = "LONG"
            bo_reason = f"Bullish Volume Breakout ({vol_spike:.1f}x Volume)"
        elif vol_spike >= 2.0 and current_price < ema_20:
            bo_score = 10.0
            bo_dir = "SHORT"
            bo_reason = f"Bearish Volume Breakdown ({vol_spike:.1f}x Volume)"
        else:
            bo_score = 50.0
            bo_dir = "NEUTRAL"
            bo_reason = "Standard Volume Activity"
        votes.append(AlphaVote("breakout", bo_dir, bo_score, weights.get("breakout", 0.0), 0.80, bo_reason))

        # 5. Microstructure / VWAP Alpha Family
        vwap = float(technical_data.get("vwap", current_price))
        vwap_diff_pct = ((current_price - vwap) / max(1e-9, vwap)) * 100.0
        imbalance = float(orderbook_data.get("imbalance_ratio", 1.0))
        if vwap_diff_pct >= 0.4 and imbalance > 1.2:
            micro_score = 80.0
            micro_dir = "LONG"
            micro_reason = f"Price above VWAP (+{vwap_diff_pct:.2f}%) with Bid Imbalance ({imbalance:.2f})"
        elif vwap_diff_pct <= -0.4 and imbalance < 0.8:
            micro_score = 20.0
            micro_dir = "SHORT"
            micro_reason = f"Price below VWAP ({vwap_diff_pct:.2f}%) with Ask Imbalance ({imbalance:.2f})"
        else:
            micro_score = 50.0
            micro_dir = "NEUTRAL"
            micro_reason = "Price Near VWAP"
        votes.append(AlphaVote("microstructure", micro_dir, micro_score, weights.get("microstructure", 0.0), 0.70, micro_reason))

        # 6. Sentiment Alpha Family
        fg_val = float(sentiment_data.get("fear_greed", {}).get("value", 50.0))
        if fg_val >= 65.0:
            sent_score = 75.0
            sent_dir = "LONG"
            sent_reason = f"Greed Sentiment ({fg_val:.0f})"
        elif fg_val <= 35.0:
            sent_score = 25.0
            sent_dir = "SHORT"
            sent_reason = f"Fear Sentiment ({fg_val:.0f})"
        else:
            sent_score = 50.0
            sent_dir = "NEUTRAL"
            sent_reason = f"Neutral Sentiment ({fg_val:.0f})"
        votes.append(AlphaVote("sentiment", sent_dir, sent_score, weights.get("sentiment", 0.0), 0.65, sent_reason))

        # Dynamic Weighted Aggregation
        active_weights_sum = sum(v.weight for v in votes) or 1.0
        composite_score = sum(v.raw_score * (v.weight / active_weights_sum) for v in votes)
        composite_score = round(max(0.0, min(100.0, composite_score)), 1)

        # Direction determination based on composite
        if composite_score >= 60.0:
            direction = "LONG"
        elif composite_score <= 40.0:
            direction = "SHORT"
        else:
            direction = "NEUTRAL"

        # Consensus percentage among weighted models
        agreeing_weights = sum(v.weight for v in votes if v.direction == direction)
        consensus_pct = round((agreeing_weights / active_weights_sum) * 100.0, 1) if direction != "NEUTRAL" else 50.0

        # Dominant Factor
        dominant = max(votes, key=lambda v: v.weight).alpha_family

        return EnsembleSignal(
            symbol=symbol,
            composite_score=composite_score,
            direction=direction,
            consensus_pct=consensus_pct,
            active_regime=regime.value,
            alpha_votes=[asdict(v) for v in votes],
            dominant_factor=dominant
        )

# Global Singleton
alpha_ensemble = MultiModelAlphaEnsemble()
