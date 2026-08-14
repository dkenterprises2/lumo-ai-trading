"""
Phase 38 — AI News Intelligence & Event-Driven Trading Package
"""

from .crypto_news_feed import NewsItem
from .news_normalizer import NewsNormalizer
from .news_deduplicator import NewsDeduplicator
from .rss_collector import RSSNewsCollector
from .exchange_announcements import ExchangeAnnouncementCollector
from .news_collector import MasterNewsCollector
from .twitter_collector import TwitterNewsCollector
from .influencer_tracker import InfluencerTracker
from .whale_tracker import WhaleTracker
from .social_sentiment_engine import SocialSentimentEngine
from .event_taxonomy import CryptoEventType, EventImpactSeverity
from .event_confidence import EventConfidenceScorer
from .event_classifier import EventClassifier
from .event_reasoning_engine import EventReasoningEngine
from .sentiment_models import SentimentSnapshot
from .sentiment_engine import NewsSentimentEngine
from .volatility_predictor import VolatilityPredictor
from .impact_forecaster import ImpactForecaster
from .event_signal_engine import EventSignalEngine
from .news_governance import NewsGovernanceEngine

__all__ = [
    "NewsItem",
    "NewsNormalizer",
    "NewsDeduplicator",
    "RSSNewsCollector",
    "ExchangeAnnouncementCollector",
    "MasterNewsCollector",
    "TwitterNewsCollector",
    "InfluencerTracker",
    "WhaleTracker",
    "SocialSentimentEngine",
    "CryptoEventType",
    "EventImpactSeverity",
    "EventConfidenceScorer",
    "EventClassifier",
    "EventReasoningEngine",
    "SentimentSnapshot",
    "NewsSentimentEngine",
    "VolatilityPredictor",
    "ImpactForecaster",
    "EventSignalEngine",
    "NewsGovernanceEngine"
]
