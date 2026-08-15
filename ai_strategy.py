from typing import Dict, Any, List, Tuple

class MarketRegimeDetector:
    """Quantitative Market Regime Detection Engine."""

    REGIMES = [
        "BULL_TREND",
        "BEAR_TREND",
        "SIDEWAYS",
        "HIGH_VOLATILITY",
        "LOW_LIQUIDITY",
        "NEWS_DRIVEN"
    ]

    REGIME_WEIGHTS = {
        "BULL_TREND": {
            "ema_trend": 0.30,
            "macd_momentum": 0.25,
            "adx_trend_strength": 0.20,
            "volume_spike": 0.15,
            "rsi_oscillator": 0.10,
            "vwap_position": 0.00,
            "obv_flow": 0.00,
            "atr_volatility": 0.00
        },
        "BEAR_TREND": {
            "ema_trend": 0.30,
            "macd_momentum": 0.25,
            "adx_trend_strength": 0.20,
            "volume_spike": 0.15,
            "rsi_oscillator": 0.10,
            "vwap_position": 0.00,
            "obv_flow": 0.00,
            "atr_volatility": 0.00
        },
        "SIDEWAYS": {
            "rsi_oscillator": 0.30,
            "vwap_position": 0.25,
            "macd_momentum": 0.15,
            "ema_trend": 0.10,
            "atr_volatility": 0.10,
            "volume_spike": 0.10,
            "adx_trend_strength": 0.00,
            "obv_flow": 0.00
        },
        "HIGH_VOLATILITY": {
            "atr_volatility": 0.30,
            "vwap_position": 0.25,
            "rsi_oscillator": 0.20,
            "adx_trend_strength": 0.15,
            "volume_spike": 0.10,
            "ema_trend": 0.00,
            "macd_momentum": 0.00,
            "obv_flow": 0.00
        },
        "LOW_LIQUIDITY": {
            "vwap_position": 0.35,
            "rsi_oscillator": 0.25,
            "ema_trend": 0.20,
            "volume_spike": 0.20,
            "macd_momentum": 0.00,
            "adx_trend_strength": 0.00,
            "obv_flow": 0.00,
            "atr_volatility": 0.00
        },
        "NEWS_DRIVEN": {
            "ema_trend": 0.20,
            "volume_spike": 0.25,
            "atr_volatility": 0.20,
            "macd_momentum": 0.20,
            "rsi_oscillator": 0.15,
            "adx_trend_strength": 0.00,
            "vwap_position": 0.00,
            "obv_flow": 0.00
        }
    }

    @classmethod
    def detect_regime(cls, current_price: float, technical_data: Dict[str, Any], sentiment_summary: Dict[str, Any]) -> Tuple[str, str]:
        """Detect current active market regime and return regime name + description."""
        atr = float(technical_data.get("atr", current_price * 0.02))
        atr_pct = (atr / (current_price + 1e-9)) * 100.0
        adx = float(technical_data.get("adx", 20.0))
        plus_di = float(technical_data.get("plus_di", 25.0))
        minus_di = float(technical_data.get("minus_di", 25.0))
        vol_spike_ratio = float(technical_data.get("volume_spike_ratio", 1.0))
        fg_val = float(sentiment_summary.get("fear_greed", {}).get("value", 50))
        ema_20 = float(technical_data.get("ema_20", current_price))
        ema_50 = float(technical_data.get("ema_50", current_price))

        if fg_val <= 18 or fg_val >= 82:
            return "NEWS_DRIVEN", f"Extreme Fear & Greed sentiment ({fg_val}) driving market sentiment."
        elif atr_pct >= 4.0 or vol_spike_ratio >= 3.0:
            return "HIGH_VOLATILITY", f"High ATR volatility spike ({atr_pct:.1f}%) and volume expansion ({vol_spike_ratio:.1f}x)."
        elif vol_spike_ratio <= 0.35:
            return "LOW_LIQUIDITY", f"Low volume activity ({vol_spike_ratio:.2f}x avg) and tight range."
        elif adx >= 25.0 and plus_di > minus_di and current_price > ema_20 > ema_50:
            return "BULL_TREND", f"Strong Bull Trend (ADX {adx:.1f}, +DI {plus_di:.1f} > -DI {minus_di:.1f}, Price > EMA20)."
        elif adx >= 25.0 and minus_di > plus_di and current_price < ema_20 < ema_50:
            return "BEAR_TREND", f"Strong Bear Trend (ADX {adx:.1f}, -DI {minus_di:.1f} > +DI {plus_di:.1f}, Price < EMA20)."
        else:
            return "SIDEWAYS", f"Consolidating Range-Bound Market (ADX {adx:.1f} < 25)."


class AITradingStrategy:
    """AI Trading Engine 2.0 - Dynamic Market Regime Adaptive Decision Engine."""

    def __init__(self):
        # Base default weights
        self.default_weights = {
            "ema_trend": 0.20,
            "macd_momentum": 0.15,
            "rsi_oscillator": 0.15,
            "adx_trend_strength": 0.15,
            "vwap_position": 0.10,
            "obv_flow": 0.10,
            "volume_spike": 0.10,
            "atr_volatility": 0.05
        }
        self.weights = dict(self.default_weights)


    def evaluate_trading_signal(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_summary: Dict[str, Any],
        strategy_name: str = "AI Hybrid",
        risk_mode: str = "Moderate"
    ) -> Dict[str, Any]:
        """Layered AI Quantitative Decision Engine producing weighted signals & explainable reasons."""

        # ---------------------------------------------------------------------
        # 0. MARKET REGIME DETECTION & DYNAMIC WEIGHT ADAPTATION
        # ---------------------------------------------------------------------
        market_regime, regime_desc = MarketRegimeDetector.detect_regime(current_price, technical_data, sentiment_summary)
        
        try:
            from backend.learning.strategy_weight_loader import strategy_weight_loader
            dynamic_weights = strategy_weight_loader.get_active_weights_sync(strategy_name="AI_HYBRID", market_regime=market_regime)
        except Exception:
            dynamic_weights = None

        regime_base_weights = MarketRegimeDetector.REGIME_WEIGHTS.get(market_regime, self.default_weights)
        active_weights = dynamic_weights or regime_base_weights


        # ---------------------------------------------------------------------
        # 1. EXTRACT QUANTITATIVE INDICATOR SUITE DATA
        # ---------------------------------------------------------------------
        rsi = float(technical_data.get("rsi", 50.0))
        trend = technical_data.get("trend", "NEUTRAL")
        macd_line = float(technical_data.get("macd", 0.0))
        macd_signal = float(technical_data.get("macd_signal", 0.0))
        macd_hist = float(technical_data.get("macd_hist", 0.0))
        vwap = float(technical_data.get("vwap", current_price))
        atr = float(technical_data.get("atr", current_price * 0.02))
        bb_upper = float(technical_data.get("bb_upper", current_price * 1.02))
        bb_lower = float(technical_data.get("bb_lower", current_price * 0.98))

        ema_20 = float(technical_data.get("ema_20", current_price))
        ema_50 = float(technical_data.get("ema_50", current_price))
        ema_200 = float(technical_data.get("ema_200", current_price))

        adx = float(technical_data.get("adx", 20.0))
        plus_di = float(technical_data.get("plus_di", 25.0))
        minus_di = float(technical_data.get("minus_di", 25.0))
        trend_strength = technical_data.get("trend_strength", "MODERATE")

        obv = float(technical_data.get("obv", 0.0))
        obv_ema = float(technical_data.get("obv_ema", 0.0))
        vol_spike_ratio = float(technical_data.get("volume_spike_ratio", 1.0))
        is_vol_spike = bool(technical_data.get("is_volume_spike", False))

        sentiment_score = float(sentiment_summary.get("combined_score", 50.0))

        # ---------------------------------------------------------------------
        # 2. MULTI-FACTOR WEIGHTED AI SCORING MATRIX (0.0 to 100.0 each)
        # ---------------------------------------------------------------------
        explainable_reasons: List[str] = [f"Market Regime [{market_regime}]: {regime_desc}"]

        # --- Factor A: EMA Trend Alignment ---
        if current_price > ema_20 and ema_20 > ema_50 and ema_50 > ema_200:
            ema_score = 95.0
            ema_label = f"Strong Bullish Alignment (Price > EMA20 ${ema_20:,.2f} > EMA50 ${ema_50:,.2f} > EMA200 ${ema_200:,.2f})"
        elif current_price > ema_20 and ema_20 > ema_50:
            ema_score = 80.0
            ema_label = f"Bullish Trend (Price ${current_price:,.2f} > EMA20 ${ema_20:,.2f} > EMA50 ${ema_50:,.2f})"
        elif current_price < ema_20 and ema_20 < ema_50 and ema_50 < ema_200:
            ema_score = 5.0
            ema_label = f"Strong Bearish Alignment (Price < EMA20 ${ema_20:,.2f} < EMA50 ${ema_50:,.2f} < EMA200 ${ema_200:,.2f})"
        elif current_price < ema_20 and ema_20 < ema_50:
            ema_score = 20.0
            ema_label = f"Bearish Trend (Price ${current_price:,.2f} < EMA20 ${ema_20:,.2f} < EMA50 ${ema_50:,.2f})"
        else:
            ema_score = 50.0
            ema_label = f"Consolidating / Neutral EMAs (Price ${current_price:,.2f})"

        if ema_score >= 80.0:
            explainable_reasons.append(f"EMA Alignment: {ema_label}.")
        elif ema_score <= 20.0:
            explainable_reasons.append(f"EMA Alignment: {ema_label}.")

        # --- Factor B: MACD Momentum ---
        if macd_hist > 0 and macd_line > macd_signal:
            macd_score = min(95.0, 70.0 + min(25.0, abs(macd_hist) * 2.0))
            macd_label = f"Bullish Crossover (Histogram +{macd_hist:.2f}, Line {macd_line:.2f} > Signal {macd_signal:.2f})"
            if macd_score >= 75.0:
                explainable_reasons.append(f"MACD Momentum: Positive momentum acceleration with histogram expanding (+{macd_hist:.2f}).")
        elif macd_hist < 0 and macd_line < macd_signal:
            macd_score = max(5.0, 30.0 - min(25.0, abs(macd_hist) * 2.0))
            macd_label = f"Bearish Crossover (Histogram {macd_hist:.2f}, Line {macd_line:.2f} < Signal {macd_signal:.2f})"
            if macd_score <= 25.0:
                explainable_reasons.append(f"MACD Momentum: Negative momentum expansion with histogram contracting ({macd_hist:.2f}).")
        else:
            macd_score = 50.0
            macd_label = f"Neutral MACD (Histogram {macd_hist:.2f})"

        # --- Factor C: RSI Oscillator ---
        if rsi <= 30.0:
            rsi_score = 90.0
            rsi_label = f"Oversold Reversal Zone (RSI {rsi:.1f} <= 30)"
            explainable_reasons.append(f"RSI Oscillator: Deeply oversold at {rsi:.1f}, indicating high probability of bullish mean reversion.")
        elif rsi <= 45.0:
            rsi_score = 70.0
            rsi_label = f"Bullish Recovery Zone (RSI {rsi:.1f})"
        elif rsi >= 70.0:
            rsi_score = 10.0
            rsi_label = f"Overbought Exhaustion Zone (RSI {rsi:.1f} >= 70)"
            explainable_reasons.append(f"RSI Oscillator: Overbought condition at {rsi:.1f}, signaling potential top exhaustion.")
        elif rsi >= 55.0:
            rsi_score = 30.0
            rsi_label = f"Bearish Pressure Zone (RSI {rsi:.1f})"
        else:
            rsi_score = 50.0
            rsi_label = f"Neutral RSI ({rsi:.1f})"

        # --- Factor D: ADX & Trend Strength ---
        if plus_di > minus_di:
            adx_score = min(95.0, 50.0 + (adx * 1.1))
            adx_label = f"Strong Bullish Trend Strength (ADX {adx:.1f}, +DI {plus_di:.1f} > -DI {minus_di:.1f})"
            if adx >= 25.0:
                explainable_reasons.append(f"Trend Strength: ADX is {adx:.1f} ({trend_strength}) with +DI dominating, confirming strong trend persistence.")
        elif minus_di > plus_di:
            adx_score = max(5.0, 50.0 - (adx * 1.1))
            adx_label = f"Strong Bearish Trend Strength (ADX {adx:.1f}, -DI {minus_di:.1f} > +DI {plus_di:.1f})"
            if adx >= 25.0:
                explainable_reasons.append(f"Trend Strength: ADX is {adx:.1f} ({trend_strength}) with -DI dominating, confirming downtrend momentum.")
        else:
            adx_score = 50.0
            adx_label = f"Weak Directional Trend (ADX {adx:.1f})"

        # --- Factor E: VWAP Relative Position ---
        vwap_diff_pct = ((current_price - vwap) / (vwap + 1e-9)) * 100.0
        if vwap_diff_pct >= 0.5:
            vwap_score = min(90.0, 65.0 + (vwap_diff_pct * 10.0))
            vwap_label = f"Price Above VWAP (+{vwap_diff_pct:.2f}% vs ${vwap:,.2f})"
            explainable_reasons.append(f"VWAP Benchmark: Price (${current_price:,.2f}) is trading above VWAP (${vwap:,.2f}), favoring buyer control.")
        elif vwap_diff_pct <= -0.5:
            vwap_score = max(10.0, 35.0 - (abs(vwap_diff_pct) * 10.0))
            vwap_label = f"Price Below VWAP ({vwap_diff_pct:.2f}% vs ${vwap:,.2f})"
            explainable_reasons.append(f"VWAP Benchmark: Price (${current_price:,.2f}) is trading below VWAP (${vwap:,.2f}), favoring seller control.")
        else:
            vwap_score = 50.0
            vwap_label = f"Price At VWAP (${vwap:,.2f})"

        # --- Factor F: OBV Volume Flow ---
        if obv > obv_ema:
            obv_score = 85.0
            obv_label = f"Institutional Accumulation (OBV {obv:,.0f} > 20 EMA {obv_ema:,.0f})"
            explainable_reasons.append("On-Balance Volume (OBV): Volume expansion above 20 EMA confirms institutional accumulation.")
        elif obv < obv_ema:
            obv_score = 15.0
            obv_label = f"Capital Distribution (OBV {obv:,.0f} < 20 EMA {obv_ema:,.0f})"
            explainable_reasons.append("On-Balance Volume (OBV): Volume contraction below 20 EMA indicates capital distribution.")
        else:
            obv_score = 50.0
            obv_label = "Neutral OBV Flow"

        # --- Factor G: Volume Spike Confirmation ---
        if is_vol_spike or vol_spike_ratio >= 1.8:
            if ema_score >= 50.0:
                vol_score = 90.0
                vol_label = f"Bullish Volume Spike ({vol_spike_ratio:.1f}x 20MA Avg)"
                explainable_reasons.append(f"Volume Surge: High volume spike of {vol_spike_ratio:.1f}x relative to 20 MA validates strong buying conviction.")
            else:
                vol_score = 10.0
                vol_label = f"Bearish Volume Spike ({vol_spike_ratio:.1f}x 20MA Avg)"
                explainable_reasons.append(f"Volume Surge: High volume spike of {vol_spike_ratio:.1f}x relative to 20 MA validates heavy selling pressure.")
        else:
            vol_score = 50.0
            vol_label = f"Normal Volume ({vol_spike_ratio:.1f}x 20MA Avg)"

        # --- Factor H: ATR Volatility Sizing ---
        atr_pct = (atr / current_price) * 100.0
        if 1.0 <= atr_pct <= 3.5:
            atr_score = 70.0
            atr_label = f"Optimal Trading Volatility (ATR ${atr:,.2f} / {atr_pct:.1f}%)"
        else:
            atr_score = 50.0
            atr_label = f"High/Low Volatility (ATR ${atr:,.2f} / {atr_pct:.1f}%)"

        # ---------------------------------------------------------------------
        # 3. DYNAMIC WEIGHTED COMPOSITE AGGREGATION
        # ---------------------------------------------------------------------
        w_sum = sum(active_weights.values()) or 1.0
        norm_weights = {k: v / w_sum for k, v in active_weights.items()}

        weighted_tech_score = (
            (ema_score * norm_weights.get("ema_trend", 0.0)) +
            (macd_score * norm_weights.get("macd_momentum", 0.0)) +
            (rsi_score * norm_weights.get("rsi_oscillator", 0.0)) +
            (adx_score * norm_weights.get("adx_trend_strength", 0.0)) +
            (vwap_score * norm_weights.get("vwap_position", 0.0)) +
            (obv_score * norm_weights.get("obv_flow", 0.0)) +
            (vol_score * norm_weights.get("volume_spike", 0.0)) +
            (atr_score * norm_weights.get("atr_volatility", 0.0))
        )
        weighted_tech_score = round(max(0.0, min(100.0, weighted_tech_score)), 1)

        if "technical_score" in technical_data and technical_data.get("technical_score") != 50.0 and len(explainable_reasons) <= 1:
            weighted_tech_score = float(technical_data["technical_score"])

        # Strategy-specific adjustments
        if strategy_name == "Trend Following":
            composite_score = (weighted_tech_score * 0.75) + (sentiment_score * 0.25)
        elif strategy_name == "Breakout":
            breakout_boost = 15.0 if current_price > bb_upper else (-15.0 if current_price < bb_lower else 0.0)
            composite_score = min(100.0, max(0.0, weighted_tech_score + breakout_boost))
        elif strategy_name == "Scalping":
            composite_score = (100.0 - rsi) if rsi < 40 else (100.0 - rsi if rsi > 60 else 50.0)
        elif strategy_name == "Grid" or strategy_name == "DCA":
            composite_score = 55.0 if current_price < vwap else 45.0
        else: # AI Hybrid (Default)
            composite_score = (weighted_tech_score * 0.70) + (sentiment_score * 0.30)

        composite_score = round(max(0.0, min(100.0, composite_score)), 1)

        # ---------------------------------------------------------------------
        # 4. RISK MODE THRESHOLDS & DIRECTION DETERMINATION
        # ---------------------------------------------------------------------
        if risk_mode == "Conservative":
            buy_thresh, sell_thresh = 70.0, 30.0
            stop_loss_dist = atr * 1.5
            take_profit_dist = atr * 3.0
        elif risk_mode == "Aggressive":
            buy_thresh, sell_thresh = 58.0, 42.0
            stop_loss_dist = atr * 2.5
            take_profit_dist = atr * 5.0
        else: # Moderate
            buy_thresh, sell_thresh = 62.0, 38.0
            stop_loss_dist = atr * 2.0
            take_profit_dist = atr * 4.0

        if composite_score >= 78.0:
            action = "STRONG_BUY"
            direction = "LONG"
            confidence = min(99.0, composite_score + 3.0)
        elif composite_score >= buy_thresh:
            action = "BUY"
            direction = "LONG"
            confidence = composite_score
        elif composite_score <= 22.0:
            action = "STRONG_SELL"
            direction = "SHORT"
            confidence = min(99.0, (100.0 - composite_score) + 3.0)
        elif composite_score <= sell_thresh:
            action = "SELL"
            direction = "SHORT"
            confidence = round(100.0 - composite_score, 1)
        else:
            action = "HOLD"
            direction = "NEUTRAL"
            confidence = round(50.0 + abs(composite_score - 50.0), 1)

        confidence = round(max(0.0, min(99.0, confidence)), 1)

        # ---------------------------------------------------------------------
        def round_price(val: float) -> float:
            if not val or val <= 0:
                return 0.0
            if val < 0.0001:
                return round(val, 8)
            if val < 0.01:
                return round(val, 6)
            if val < 1.0:
                return round(val, 4)
            return round(val, 2)

        if direction == "LONG":
            stop_loss_price = round_price(current_price - stop_loss_dist)
            take_profit_price = round_price(current_price + take_profit_dist)
        elif direction == "SHORT":
            stop_loss_price = round_price(current_price + stop_loss_dist)
            take_profit_price = round_price(current_price - take_profit_dist)
        else:
            stop_loss_price = round_price(current_price * 0.975)
            take_profit_price = round_price(current_price * 1.05)

        sl_pct = round(abs(current_price - stop_loss_price) / (current_price + 1e-9) * 100.0, 2)
        tp_pct = round(abs(take_profit_price - current_price) / (current_price + 1e-9) * 100.0, 2)


        sentiment_label = sentiment_summary.get("label", "NEUTRAL")
        explainable_reasons.append(
            f"Market Sentiment: News sentiment index is {sentiment_score:.1f}/100 ({sentiment_label})."
        )

        # 100-Point Score Breakdown Output Structure
        trend_pts = round((ema_score / 100.0) * 20.0 + (adx_score / 100.0) * 10.0, 1)
        momentum_pts = round((macd_score / 100.0) * 20.0, 1)
        volume_pts = round((vol_score / 100.0) * 10.0 + (obv_score / 100.0) * 5.0, 1)
        rsi_pts = round((rsi_score / 100.0) * 10.0, 1)
        macd_pts = round((macd_score / 100.0) * 10.0, 1)
        vwap_pts = round((vwap_score / 100.0) * 5.0, 1)
        risk_pts = round((atr_score / 100.0) * 10.0, 1)
        sentiment_pts = 0.0
        total_pts = round(trend_pts + momentum_pts + volume_pts + rsi_pts + macd_pts + vwap_pts + risk_pts + sentiment_pts, 1)

        score_breakdown = {
            "trend": {"points": trend_pts, "max": 30},
            "momentum": {"points": momentum_pts, "max": 20},
            "volume": {"points": volume_pts, "max": 15},
            "rsi": {"points": rsi_pts, "max": 10},
            "macd": {"points": macd_pts, "max": 10},
            "vwap": {"points": vwap_pts, "max": 5},
            "risk": {"points": risk_pts, "max": 10},
            "sentiment": {"points": sentiment_pts, "max": 0},
            "total": {"points": total_pts, "max": 100},
            "ema_trend": {"score": round(ema_score, 1), "weight": norm_weights.get("ema_trend", 0.20), "label": ema_label},
            "macd_momentum": {"score": round(macd_score, 1), "weight": norm_weights.get("macd_momentum", 0.15), "label": macd_label},
            "rsi_oscillator": {"score": round(rsi_score, 1), "weight": norm_weights.get("rsi_oscillator", 0.15), "label": rsi_label},
            "adx_trend_strength": {"score": round(adx_score, 1), "weight": norm_weights.get("adx_trend_strength", 0.15), "label": adx_label},
            "vwap_position": {"score": round(vwap_score, 1), "weight": norm_weights.get("vwap_position", 0.10), "label": vwap_label},
            "obv_flow": {"score": round(obv_score, 1), "weight": norm_weights.get("obv_flow", 0.10), "label": obv_label},
            "volume_spike": {"score": round(vol_score, 1), "weight": norm_weights.get("volume_spike", 0.10), "label": vol_label},
            "atr_volatility": {"score": round(atr_score, 1), "weight": norm_weights.get("atr_volatility", 0.05), "label": atr_label}
        }

        reasoning_summary = " ".join(explainable_reasons)

        return {
            "symbol": symbol,
            "current_price": current_price,
            "action": action,
            "direction": direction,
            "confidence_score": confidence,
            "composite_score": composite_score,
            "technical_score": weighted_tech_score,
            "sentiment_score": sentiment_score,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "stop_loss_pct": sl_pct,
            "take_profit_pct": tp_pct,
            "risk_mode": risk_mode,
            "strategy": strategy_name,
            "market_regime": market_regime,
            "regime_description": regime_desc,
            "reasoning": reasoning_summary,
            "explainable_reasons": explainable_reasons,
            "score_breakdown": score_breakdown
        }


