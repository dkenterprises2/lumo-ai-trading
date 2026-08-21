import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class MissedOpportunityRecord:
    record_id: str = field(default_factory=lambda: f"MISSED-{uuid.uuid4().hex[:6].upper()}")
    timestamp: float = field(default_factory=time.time)
    symbol: str = "BTC/USDT"
    intended_direction: str = "LONG"
    rejection_reason: str = "ADVERSARIAL_GATE_VETO"
    ref_price_at_rejection: float = 60000.0
    forward_price_30m: float = 60000.0
    hypothetical_pnl: float = 0.0
    assessment: str = "GOOD_SAVE"  # GOOD_SAVE (prevented loss), MISSED_OPPORTUNITY (missed win), NEUTRAL_CHOP
    recommendation: str = "Filter working as intended."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class MissedOpportunityEngine:
    """Missed Opportunity & Rejection Quality Evaluation Engine."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MissedOpportunityEngine, cls).__new__(cls)
            cls._instance.records: List[MissedOpportunityRecord] = []
        return cls._instance

    def evaluate_rejection_outcome(
        self,
        symbol: str,
        direction: str,
        rejection_reason: str,
        entry_price: float,
        forward_price: float,
        allocation_usd: float = 1000.0
    ) -> MissedOpportunityRecord:
        """Evaluate forward trajectory of a rejected trade setup."""
        if entry_price <= 0.0:
            entry_price = forward_price

        price_pct_change = ((forward_price - entry_price) / entry_price) * 100.0
        
        if direction.upper() in ["LONG", "BUY"]:
            hypothetical_pnl = allocation_usd * (price_pct_change / 100.0)
        else:
            hypothetical_pnl = allocation_usd * (-price_pct_change / 100.0)

        # Classify rejection quality
        if hypothetical_pnl < -10.0:
            assessment = "GOOD_SAVE"
            recommendation = f"Rejection correctly prevented a -${abs(hypothetical_pnl):.2f} loss."
        elif hypothetical_pnl > 15.0:
            assessment = "MISSED_OPPORTUNITY"
            recommendation = f"Filter was overly conservative; missed potential +${hypothetical_pnl:.2f} move."
        else:
            assessment = "NEUTRAL_CHOP"
            recommendation = "Market moved sideways; rejection saved unnecessary friction fees."

        rec = MissedOpportunityRecord(
            symbol=symbol,
            intended_direction=direction.upper(),
            rejection_reason=rejection_reason,
            ref_price_at_rejection=entry_price,
            forward_price_30m=forward_price,
            hypothetical_pnl=round(hypothetical_pnl, 2),
            assessment=assessment,
            recommendation=recommendation
        )
        self.records.append(rec)
        return rec

    def get_summary(self) -> Dict[str, Any]:
        total = len(self.records)
        good_saves = sum(1 for r in self.records if r.assessment == "GOOD_SAVE")
        missed = sum(1 for r in self.records if r.assessment == "MISSED_OPPORTUNITY")
        neutral = sum(1 for r in self.records if r.assessment == "NEUTRAL_CHOP")
        
        filter_efficiency = ((good_saves + neutral) / max(1, total)) * 100.0
        return {
            "total_no_trades_analyzed": total,
            "good_saves_count": good_saves,
            "missed_opportunities_count": missed,
            "neutral_saves_count": neutral,
            "filter_efficiency_pct": round(filter_efficiency, 2),
            "recent_records": [r.to_dict() for r in self.records[-10:]]
        }

# Global Singleton
missed_opportunity_engine = MissedOpportunityEngine()
