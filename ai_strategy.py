from typing import Dict, Any

class AITradingStrategy:
    def __init__(self):
        pass

    def evaluate_trading_signal(
        self,
        symbol: str,
        current_price: float,
        technical_data: Dict[str, Any],
        sentiment_summary: Dict[str, Any],
        strategy_name: str = "AI Hybrid",
        risk_mode: str = "Moderate"
    ) -> Dict[str, Any]:
        """Layered AI Quantitative Decision Engine producing LONG & SHORT signals."""
        
        tech_score = technical_data.get("technical_score", 50.0)
        sentiment_score = sentiment_summary.get("combined_score", 50.0)
        rsi = technical_data.get("rsi", 50.0)
        trend = technical_data.get("trend", "NEUTRAL")
        macd_hist = technical_data.get("macd_hist", 0.0)
        vwap = technical_data.get("vwap", current_price)
        bb_upper = technical_data.get("bb_upper", current_price * 1.02)
        bb_lower = technical_data.get("bb_lower", current_price * 0.98)
        atr = technical_data.get("atr", current_price * 0.02)

        # 1. Strategy-Specific Modifications
        if strategy_name == "Trend Following":
            # Relies heavily on EMA trends & MACD
            composite_score = (tech_score * 0.70) + (sentiment_score * 0.30)
        elif strategy_name == "Breakout":
            # Looks for price breaking Bollinger Bands or ATR spikes
            breakout_boost = 15.0 if current_price > bb_upper else (-15.0 if current_price < bb_lower else 0.0)
            composite_score = min(100.0, max(0.0, tech_score + breakout_boost))
        elif strategy_name == "Scalping":
            # Fast RSI oversold/overbought signals
            composite_score = (100.0 - rsi) if rsi < 40 else (100.0 - rsi if rsi > 60 else 50.0)
        elif strategy_name == "Grid" or strategy_name == "DCA":
            composite_score = 55.0 if current_price < vwap else 45.0
        else: # AI Hybrid (Default)
            composite_score = (tech_score * 0.50) + (sentiment_score * 0.50)

        composite_score = round(composite_score, 1)

        # 2. Risk Mode Thresholds
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

        # 3. Layered Decision Pipeline -> Action Determination
        if composite_score >= 78.0:
            action = "STRONG_BUY"
            direction = "LONG"
            confidence = min(98.0, composite_score + 4.0)
        elif composite_score >= buy_thresh:
            action = "BUY"
            direction = "LONG"
            confidence = composite_score
        elif composite_score <= 22.0:
            action = "STRONG_SELL"
            direction = "SHORT"
            confidence = min(98.0, (100.0 - composite_score) + 4.0)
        elif composite_score <= sell_thresh:
            action = "SELL"
            direction = "SHORT"
            confidence = round(100.0 - composite_score, 1)
        else:
            action = "HOLD"
            direction = "NEUTRAL"
            confidence = round(50.0 + abs(composite_score - 50.0), 1)

        # Calculate Price Targets based on LONG vs SHORT
        if direction == "LONG":
            stop_loss_price = round(current_price - stop_loss_dist, 4)
            take_profit_price = round(current_price + take_profit_dist, 4)
        elif direction == "SHORT":
            stop_loss_price = round(current_price + stop_loss_dist, 4)
            take_profit_price = round(current_price - take_profit_dist, 4)
        else:
            stop_loss_price = round(current_price * 0.975, 4)
            take_profit_price = round(current_price * 1.05, 4)

        sl_pct = round(abs(current_price - stop_loss_price) / current_price * 100.0, 2)
        tp_pct = round(abs(take_profit_price - current_price) / current_price * 100.0, 2)

        # Quantitative Reasoning Summary
        reasons = [
            f"Strategy: {strategy_name}.",
            f"RSI: {rsi}.",
            f"EMA Trend: {trend}.",
            f"VWAP: ${vwap:.2f}.",
            f"News Sentiment: {sentiment_summary.get('label', 'NEUTRAL')} ({sentiment_summary.get('combined_score', 50)}/100)."
        ]

        return {
            "symbol": symbol,
            "current_price": current_price,
            "action": action,
            "direction": direction,
            "confidence_score": round(confidence, 1),
            "composite_score": composite_score,
            "technical_score": tech_score,
            "sentiment_score": sentiment_score,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price,
            "stop_loss_pct": sl_pct,
            "take_profit_pct": tp_pct,
            "risk_mode": risk_mode,
            "strategy": strategy_name,
            "reasoning": " ".join(reasons)
        }
