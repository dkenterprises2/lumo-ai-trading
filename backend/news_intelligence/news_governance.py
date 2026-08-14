from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class GovernanceDecision:
    is_allowed: bool
    status: str
    reason: str
    minimum_confidence_required: float = 0.80

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

class NewsGovernanceEngine:
    """Enforces News & Event Integrity Rules."""

    def evaluate_news_event(
        self,
        headline: str,
        source: str,
        confidence_score: float,
        is_unverified_rumor: bool = False
    ) -> GovernanceDecision:
        if is_unverified_rumor:
            return GovernanceDecision(False, "BLOCKED", "Unverified social rumor blocked by governance")

        if confidence_score < 0.80:
            return GovernanceDecision(False, "NO_ACTION", f"Event confidence score ({confidence_score:.2f}) < 0.80 minimum threshold")

        if source in ["Twitter/X", "Telegram", "Reddit"]:
            if confidence_score < 0.85:
                return GovernanceDecision(False, "WARNING", f"Single social source news from {source} requires corroboration")

        return GovernanceDecision(True, "APPROVED", "News event passed governance validation")
