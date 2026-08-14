from dataclasses import dataclass, asdict
from typing import Dict, List, Any

from .event_taxonomy import CryptoEventType

@dataclass
class EventSignal:
    event_type: str
    symbol: str
    action: str  # BUY, SELL, REDUCE_RISK, CLOSE_POSITION, BLOCK_NEW_LONGS, BLOCK_NEW_SHORTS, HEDGE
    urgency: str  # IMMEDIATE, HIGH, MEDIUM
    risk_adjustment: Dict[str, Any]
    arbitrage_action: str
    shadow_trade_action: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class EventSignalEngine:
    """Converts Classified News Events into Actionable Execution & Risk Signals."""

    def generate_signal(self, event_type: str, symbol: str = "BTC/USDT", confidence: float = 0.90) -> EventSignal:
        action = "REDUCE_RISK"
        urgency = "HIGH"
        risk_adj = {}
        arb_action = "NORMAL"
        shadow_action = "MONITOR"

        if event_type == CryptoEventType.EXCHANGE_HACK.value:
            action = "CLOSE_POSITION"
            urgency = "IMMEDIATE"
            risk_adj = {"portfolio_heat_cap_pct": 30.0, "max_exposure_pct": 10.0}
            arb_action = "DISABLE_VENUE"
            shadow_action = "SIMULATE_EMERGENCY_EXIT"

        elif event_type == CryptoEventType.ETF_APPROVAL.value:
            action = "BUY"
            urgency = "HIGH"
            risk_adj = {"max_exposure_pct": 50.0}
            arb_action = "BOOST_SCAN_FREQUENCY"
            shadow_action = "SIMULATE_EVENT_ENTRY_LONG"

        elif event_type == CryptoEventType.TOKEN_DELISTING.value:
            action = "SELL"
            urgency = "IMMEDIATE"
            risk_adj = {"max_exposure_pct": 0.0}
            arb_action = "DISABLE_PAIR"
            shadow_action = "SIMULATE_EVENT_EXIT"

        elif event_type == CryptoEventType.TOKEN_LISTING.value:
            action = "BUY"
            urgency = "MEDIUM"
            risk_adj = {"max_exposure_pct": 20.0}
            arb_action = "BOOST_SCAN_FREQUENCY"
            shadow_action = "SIMULATE_EVENT_ENTRY_LONG"

        elif event_type == CryptoEventType.EXCHANGE_OUTAGE.value:
            action = "BLOCK_NEW_LONGS"
            urgency = "HIGH"
            risk_adj = {"max_exposure_pct": 15.0}
            arb_action = "DISABLE_VENUE"
            shadow_action = "PAUSE_SHADOW_Fills"

        return EventSignal(
            event_type=event_type,
            symbol=symbol,
            action=action,
            urgency=urgency,
            risk_adjustment=risk_adj,
            arbitrage_action=arb_action,
            shadow_trade_action=shadow_action
        )
