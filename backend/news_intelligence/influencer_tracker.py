from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class InfluencerScore:
    handle: str
    followers_weight: float
    engagement_weight: float
    historical_accuracy: float
    total_score: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class InfluencerTracker:
    """Calculates Influencer Credibility & Impact Score."""

    def compute_influence_score(
        self,
        handle: str,
        followers: int = 500000,
        avg_likes: int = 15000,
        historical_accuracy: float = 0.85
    ) -> InfluencerScore:
        f_weight = min(0.40, (followers / 1000000.0) * 0.40)
        e_weight = min(0.30, (avg_likes / 50000.0) * 0.30)
        h_weight = min(0.30, historical_accuracy * 0.30)

        tot = f_weight + e_weight + h_weight

        return InfluencerScore(
            handle=handle,
            followers_weight=round(f_weight, 4),
            engagement_weight=round(e_weight, 4),
            historical_accuracy=round(h_weight, 4),
            total_score=round(tot, 4)
        )
