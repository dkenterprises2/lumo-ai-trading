from dataclasses import dataclass, asdict
from typing import Dict, Any

from .influencer_tracker import InfluencerTracker
from .whale_tracker import WhaleTracker

@dataclass
class SocialSentimentSnapshot:
    symbol: str
    tweet_volume_24h: int
    sentiment_score: float  # -1.0 to +1.0
    sentiment_label: str
    whale_bias: str  # BULLISH_ACCUMULATION, BEARISH_INFLOW, NEUTRAL

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class SocialSentimentEngine:
    """Aggregates Social & Whale Activity into Symbol Sentiment Metrics."""

    def __init__(self):
        self.influencer_tracker = InfluencerTracker()
        self.whale_tracker = WhaleTracker()

    def get_social_sentiment(self, symbol: str = "BTC/USDT") -> SocialSentimentSnapshot:
        transfers = self.whale_tracker.fetch_recent_whale_transfers()
        inflow_usd = sum(t.amount_usd for t in transfers if "Deposit" in t.to_address)
        outflow_usd = sum(t.amount_usd for t in transfers if "Custody" in t.from_address)

        bias = "NEUTRAL"
        score = 0.45
        if outflow_usd > inflow_usd:
            bias = "BULLISH_ACCUMULATION"
            score = 0.65
        elif inflow_usd > outflow_usd:
            bias = "BEARISH_INFLOW"
            score = -0.35

        return SocialSentimentSnapshot(
            symbol=symbol,
            tweet_volume_24h=145000,
            sentiment_score=score,
            sentiment_label="BULLISH" if score > 0.15 else ("BEARISH" if score < -0.15 else "NEUTRAL"),
            whale_bias=bias
        )
