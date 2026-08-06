from typing import Dict, Any, List
import time
from backend.core.event_bus import event_bus, EventTypes
from ai_strategy import AITradingStrategy

class MarketReplayEngine:
    """Historical Market Tick Replay Engine streaming events through internal EventBus."""

    def __init__(self):
        self.ai_strategy = AITradingStrategy()

    async def replay_ticks(self, symbol: str, ticks: List[Dict[str, Any]], speed_multiplier: float = 1.0) -> Dict[str, Any]:
        """Replay market ticks and publish MARKET_TICK and AI_SIGNAL events."""
        replayed_count = 0
        generated_signals = 0

        for tick in ticks:
            price = float(tick.get("price", 60000.0))
            ts = tick.get("timestamp", time.time())

            # 1. Publish MARKET_TICK Event
            await event_bus.publish(EventTypes.MARKET_TICK, {
                "symbol": symbol,
                "price": price,
                "timestamp": ts
            })
            replayed_count += 1

            # 2. Evaluate AI Signal & Publish AI_SIGNAL Event
            ta = {
                "rsi": tick.get("rsi", 50.0),
                "ema_20": price * 0.99,
                "ema_50": price * 0.98,
                "ema_200": price * 0.95,
                "macd_hist": 2.0
            }
            sig = self.ai_strategy.evaluate_trading_signal(symbol, price, ta, {"combined_score": 50.0})

            await event_bus.publish(EventTypes.AI_SIGNAL, sig)
            generated_signals += 1

        return {
            "status": "success",
            "symbol": symbol,
            "replayed_ticks_count": replayed_count,
            "generated_signals_count": generated_signals
        }
