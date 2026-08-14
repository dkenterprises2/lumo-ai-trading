from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class SentimentSnapshot:
    symbol: str
    headline_sentiment: float  # -1.0 to +1.0
    article_sentiment: float   # -1.0 to +1.0
    social_sentiment: float    # -1.0 to +1.0
    composite_sentiment: float # -1.0 to +1.0
    label: str  # VERY_BEARISH, BEARISH, NEUTRAL, BULLISH, VERY_BULLISH

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
