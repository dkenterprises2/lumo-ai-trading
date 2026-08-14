from dataclasses import dataclass, asdict
from typing import Dict, List, Any

from .event_taxonomy import CryptoEventType, EventImpactSeverity
from .event_classifier import EventClassifier
from .event_confidence import EventConfidenceScorer

@dataclass
class EventReasoningOutput:
    event_type: str
    event_summary: str
    affected_assets: List[str]
    expected_impact: str  # BULLISH, BEARISH, NEUTRAL
    severity: str
    expected_volatility_impact: str  # HIGH, MODERATE, EXTREME
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class EventReasoningEngine:
    """LLM-Assisted Event Reasoning & Impact Analyzer."""

    def __init__(self):
        self.classifier = EventClassifier()
        self.confidence_scorer = EventConfidenceScorer()

    def analyze_event(
        self,
        headline: str,
        source: str = "CoinDesk",
        extracted_symbols: List[str] = None
    ) -> EventReasoningOutput:
        event_type, severity = self.classifier.classify_text(headline)
        conf = self.confidence_scorer.compute_confidence(source)
        assets = extracted_symbols or ["BTC/USDT"]

        impact = "NEUTRAL"
        vol_impact = "MODERATE"

        if event_type == CryptoEventType.ETF_APPROVAL:
            impact = "BULLISH"
            vol_impact = "HIGH"
        elif event_type in [CryptoEventType.EXCHANGE_HACK, CryptoEventType.STABLECOIN_DEPEG, CryptoEventType.BANKRUPTCY]:
            impact = "BEARISH"
            vol_impact = "EXTREME"
        elif event_type == CryptoEventType.TOKEN_DELISTING:
            impact = "BEARISH"
            vol_impact = "HIGH"
        elif event_type in [CryptoEventType.TOKEN_LISTING, CryptoEventType.PARTNERSHIP]:
            impact = "BULLISH"
            vol_impact = "MODERATE"

        return EventReasoningOutput(
            event_type=event_type.value,
            event_summary=headline,
            affected_assets=assets,
            expected_impact=impact,
            severity=severity.value,
            expected_volatility_impact=vol_impact,
            confidence=conf
        )
