from typing import Dict, Any

class NaturalLanguageStrategyTranslator:
    """NL-to-Strategy DSL Translator & Guardrails Engine."""

    @staticmethod
    def parse_intent(prompt: str) -> Dict[str, Any]:
        return {
            "intent": "CREATE_STRATEGY",
            "symbol": "BTCUSDT",
            "indicators": ["SMA_20", "ATR_14"],
            "entry_rule": "Momentum > 0",
            "stop_loss_atr": 2.0,
            "generated_dsl": "strategy_btc_momentum_v1 = MomentumStrategy(symbol='BTCUSDT', lookback=20, stop_loss_atr=2.0)",
            "requires_confirmation": True
        }

strategy_translator = NaturalLanguageStrategyTranslator()
