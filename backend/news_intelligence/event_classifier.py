import re
from typing import Tuple
from .event_taxonomy import CryptoEventType, EventImpactSeverity

class EventClassifier:
    """Classifies Raw Text Headlines into Crypto Event Taxonomies."""

    KEYWORD_PATTERNS = [
        (r'\b(SEC|ETF APPROVAL|SPOT ETF APPROVED|ETFS APPROVED)\b', CryptoEventType.ETF_APPROVAL, EventImpactSeverity.HIGH),
        (r'\b(ETF REJECTED|REJECTION|DENIED)\b', CryptoEventType.ETF_REJECTION, EventImpactSeverity.HIGH),
        (r'\b(HACK|EXPLOIT|DRAINED|ATTACK|VULNERABILITY)\b', CryptoEventType.EXCHANGE_HACK, EventImpactSeverity.CRITICAL),
        (r'\b(OUTAGE|MAINTENANCE|SUSPENDED|DOWN)\b', CryptoEventType.EXCHANGE_OUTAGE, EventImpactSeverity.HIGH),
        (r'\b(LISTING|LISTED|SUPPORT SPOT|TRADING OPEN)\b', CryptoEventType.TOKEN_LISTING, EventImpactSeverity.MODERATE),
        (r'\b(DELISTING|DELIST|REMOVED|DISCONTINUED)\b', CryptoEventType.TOKEN_DELISTING, EventImpactSeverity.HIGH),
        (r'\b(PARTNERSHIP|PARTNER|COLLABORATION)\b', CryptoEventType.PARTNERSHIP, EventImpactSeverity.MODERATE),
        (r'\b(SUED|LAWSUIT|SEC CHARGES|REGULATORY|DOJ)\b', CryptoEventType.REGULATORY_ACTION, EventImpactSeverity.HIGH),
        (r'\b(WHALE|TRANSFERRED|TRANSFERS|LARGE MOVEMENT)\b', CryptoEventType.WHALE_MOVEMENT, EventImpactSeverity.LOW),
        (r'\b(DEPEG|DEPEGGED|STABLECOIN LOSS)\b', CryptoEventType.STABLECOIN_DEPEG, EventImpactSeverity.CRITICAL),
        (r'\b(BANKRUPTCY|CHAPTER 11|INSOLVENT)\b', CryptoEventType.BANKRUPTCY, EventImpactSeverity.CRITICAL)
    ]

    def classify_text(self, text: str) -> Tuple[CryptoEventType, EventImpactSeverity]:
        text_upper = text.upper()
        for pattern, event_type, severity in self.KEYWORD_PATTERNS:
            if re.search(pattern, text_upper):
                return event_type, severity

        return CryptoEventType.UNKNOWN, EventImpactSeverity.LOW
