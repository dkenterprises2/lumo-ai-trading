import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

@dataclass
class NewsItem:
    item_id: str = field(default_factory=lambda: f"NEWS-{uuid.uuid4().hex[:8].upper()}")
    title: str = ""
    summary: str = ""
    source: str = "CoinDesk"
    url: str = ""
    raw_timestamp: str = ""
    normalized_timestamp: float = field(default_factory=time.time)
    extracted_symbols: List[str] = field(default_factory=list)
    confidence_score: float = 0.85
    category: str = "GENERAL"
    sentiment_score: float = 0.0  # -1.0 to +1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
