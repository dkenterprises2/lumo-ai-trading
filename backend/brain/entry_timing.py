from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional
from loguru import logger

class EntryQuality(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    MARGINAL = "MARGINAL"
    LATE = "LATE"
    REJECT = "REJECT"

@dataclass
class EntryAssessment:
    quality: EntryQuality
    quality_score: float             # [0.0, 100.0]
    is_approved: bool                # True for EXCELLENT, GOOD, MARGINAL; False for LATE, REJECT
    extension_ratio: float           # Distance from baseline / ATR
    reversal_risk_score: float       # [0.0, 100.0]
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["quality"] = self.quality.value
        return d

class EntryTimingEngine:
    """
    Phase 44.3 Entry Timing Intelligence Engine.
    Prevents entering trades after the move has concluded and rejects reversal traps.
    """

    def evaluate_entry_timing(
        self,
        symbol: str,
        direction: str,                # LONG, SHORT
        current_price: float,
        technical_data: Dict[str, Any]
    ) -> EntryAssessment:
        if direction not in ["LONG", "SHORT"]:
            return EntryAssessment(
                quality=EntryQuality.REJECT,
                quality_score=0.0,
                is_approved=False,
                extension_ratio=0.0,
                reversal_risk_score=100.0,
                reason="Direction is Neutral; no trade to enter."
            )

        atr = float(technical_data.get("atr", current_price * 0.02))
        rsi = float(technical_data.get("rsi", 50.0))
        ema_20 = float(technical_data.get("ema_20", current_price))
        vol_spike = float(technical_data.get("volume_spike_ratio", 1.0))

        # 1. Extension Ratio: Distance from 20 EMA in units of ATR
        dist_from_ema = abs(current_price - ema_20)
        extension_ratio = round(dist_from_ema / max(1e-4, atr), 2)

        # 2. Reversal Risk Assessment
        reversal_risk = 15.0  # Baseline low risk

        if direction == "LONG":
            # Overbought exhaustion check
            if rsi >= 72.0:
                reversal_risk += 40.0
            if current_price > ema_20 and extension_ratio >= 2.2:
                reversal_risk += 35.0
            # Exhaustion volume check
            if rsi >= 70.0 and vol_spike >= 2.5:
                reversal_risk += 20.0  # Climax buying / blow-off top

        elif direction == "SHORT":
            # Oversold exhaustion check
            if rsi <= 28.0:
                reversal_risk += 40.0
            if current_price < ema_20 and extension_ratio >= 2.2:
                reversal_risk += 35.0
            # Capitulation volume check
            if rsi <= 26.0 and vol_spike >= 2.5:
                reversal_risk += 20.0  # Climax selling / bottom absorption

        reversal_risk = min(100.0, reversal_risk)

        # 3. Quality Categorization
        if reversal_risk >= 70.0:
            quality = EntryQuality.REJECT
            quality_score = 15.0
            approved = False
            reason = f"High Reversal Trap Risk ({reversal_risk:.0f}/100) at RSI {rsi:.1f} -> NO TRADE."

        elif extension_ratio >= 2.0:
            quality = EntryQuality.LATE
            quality_score = 25.0
            approved = False
            reason = f"Late-Cycle Entry: Price extended {extension_ratio:.1f}x ATR away from EMA20 -> NO TRADE (Move exhausted)."

        elif extension_ratio <= 0.8 and reversal_risk <= 30.0:
            quality = EntryQuality.EXCELLENT
            quality_score = 92.0
            approved = True
            reason = f"Fresh Early Breakout: Tight extension ({extension_ratio:.1f}x ATR) and low reversal risk ({reversal_risk:.0f})."

        elif extension_ratio <= 1.5 and reversal_risk <= 50.0:
            quality = EntryQuality.GOOD
            quality_score = 78.0
            approved = True
            reason = f"Clean Trend Continuation: Moderate extension ({extension_ratio:.1f}x ATR)."

        else:
            quality = EntryQuality.MARGINAL
            quality_score = 55.0
            approved = True
            reason = f"Marginal Extension ({extension_ratio:.1f}x ATR); position size should be moderated."

        return EntryAssessment(
            quality=quality,
            quality_score=quality_score,
            is_approved=approved,
            extension_ratio=extension_ratio,
            reversal_risk_score=reversal_risk,
            reason=reason
        )

# Global Singleton
entry_timing_engine = EntryTimingEngine()
