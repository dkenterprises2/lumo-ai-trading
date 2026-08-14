import pytest
from backend.news_intelligence import (
    NewsItem,
    NewsNormalizer,
    NewsDeduplicator,
    RSSNewsCollector,
    ExchangeAnnouncementCollector,
    MasterNewsCollector,
    TwitterNewsCollector,
    InfluencerTracker,
    WhaleTracker,
    SocialSentimentEngine,
    CryptoEventType,
    EventImpactSeverity,
    EventConfidenceScorer,
    EventClassifier,
    EventReasoningEngine,
    NewsSentimentEngine,
    VolatilityPredictor,
    ImpactForecaster,
    EventSignalEngine,
    NewsGovernanceEngine
)

def test_news_normalizer_symbol_extraction():
    normalizer = NewsNormalizer()
    symbols = normalizer.extract_symbols("SEC Approves Bitcoin & Ethereum Spot ETF")
    assert "BTC/USDT" in symbols
    assert "ETH/USDT" in symbols

def test_news_normalizer_default_symbol():
    normalizer = NewsNormalizer()
    symbols = normalizer.extract_symbols("General Market Overview")
    assert symbols == ["BTC/USDT"]

def test_news_normalizer_timestamp():
    normalizer = NewsNormalizer()
    ts = normalizer.normalize_timestamp(1700000000.0)
    assert ts == 1700000000.0

def test_news_deduplicator_removes_exact_matches():
    dedup = NewsDeduplicator()
    items = [
        NewsItem(title="SEC Approves Spot ETF"),
        NewsItem(title="SEC Approves Spot ETF")
    ]
    unique = dedup.deduplicate(items)
    assert len(unique) == 1

def test_news_deduplicator_removes_similar_titles():
    dedup = NewsDeduplicator()
    items = [
        NewsItem(title="SEC Approves Bitcoin Spot ETF"),
        NewsItem(title="SEC Approves Bitcoin Spot ETF Today")
    ]
    unique = dedup.deduplicate(items)
    assert len(unique) == 1

def test_rss_news_collector_sources():
    collector = RSSNewsCollector()
    items = collector.fetch_rss_news()
    assert len(items) > 0
    assert items[0].source in RSSNewsCollector.SOURCES

def test_exchange_announcements_collector():
    collector = ExchangeAnnouncementCollector()
    items = collector.fetch_announcements()
    assert len(items) > 0
    assert "Binance" in items[0].source or "OKX" in items[0].source

def test_master_news_collector_aggregation():
    collector = MasterNewsCollector()
    all_news = collector.collect_all_news()
    assert len(all_news) > 0

def test_twitter_news_collector():
    collector = TwitterNewsCollector()
    tweets = collector.fetch_social_tweets()
    assert len(tweets) > 0
    assert tweets[0].source == "Twitter/X"

def test_influencer_tracker_scoring():
    tracker = InfluencerTracker()
    score = tracker.compute_influence_score("@crypto_analyst", followers=1000000, avg_likes=25000, historical_accuracy=0.90)
    assert score.total_score > 0.50

def test_whale_tracker_transfers():
    tracker = WhaleTracker()
    transfers = tracker.fetch_recent_whale_transfers()
    assert len(transfers) > 0
    assert transfers[0].amount_usd > 0

def test_social_sentiment_engine_aggregation():
    engine = SocialSentimentEngine()
    snap = engine.get_social_sentiment("BTC/USDT")
    assert snap.symbol == "BTC/USDT"
    assert snap.sentiment_label in ["BULLISH", "BEARISH", "NEUTRAL"]

def test_event_taxonomy_enum_values():
    assert CryptoEventType.ETF_APPROVAL.value == "ETF_APPROVAL"
    assert EventImpactSeverity.CRITICAL.value == "CRITICAL"

def test_event_confidence_scorer_reputation():
    scorer = EventConfidenceScorer()
    conf = scorer.compute_confidence("Binance Announcements")
    assert conf >= 0.95

def test_event_confidence_scorer_corroboration_bonus():
    scorer = EventConfidenceScorer()
    conf = scorer.compute_confidence("CoinDesk", corroborating_sources=["Reuters Crypto", "The Block"])
    assert conf > 0.90

def test_event_classifier_etf_approval():
    classifier = EventClassifier()
    event_type, severity = classifier.classify_text("SEC Grants Final Approval for Bitcoin Spot ETF")
    assert event_type == CryptoEventType.ETF_APPROVAL
    assert severity == EventImpactSeverity.HIGH

def test_event_classifier_exchange_hack():
    classifier = EventClassifier()
    event_type, severity = classifier.classify_text("Major Protocol Exploit Drains $50M")
    assert event_type == CryptoEventType.EXCHANGE_HACK
    assert severity == EventImpactSeverity.CRITICAL

def test_event_classifier_token_delisting():
    classifier = EventClassifier()
    event_type, severity = classifier.classify_text("OKX Delisting Notice for Token Pair")
    assert event_type == CryptoEventType.TOKEN_DELISTING

def test_event_classifier_unknown():
    classifier = EventClassifier()
    event_type, severity = classifier.classify_text("Random Unrelated Text Announcement")
    assert event_type == CryptoEventType.UNKNOWN

def test_event_reasoning_engine_etf_approval():
    engine = EventReasoningEngine()
    output = engine.analyze_event("SEC Approves Bitcoin Spot ETF", "CoinDesk", ["BTC/USDT"])
    assert output.event_type == "ETF_APPROVAL"
    assert output.expected_impact == "BULLISH"
    assert output.confidence >= 0.85

def test_event_reasoning_engine_exchange_hack():
    engine = EventReasoningEngine()
    output = engine.analyze_event("Exchange Hack Drains Funds", "CoinTelegraph", ["ETH/USDT"])
    assert output.event_type == "EXCHANGE_HACK"
    assert output.expected_impact == "BEARISH"

def test_sentiment_engine_text_scoring():
    engine = NewsSentimentEngine()
    s_pos = engine.compute_text_sentiment("SEC Approves Bullish Record ETF Listing")
    s_neg = engine.compute_text_sentiment("Exchange Hack Exploit Crash Lawsuit")
    assert s_pos > 0
    assert s_neg < 0

def test_sentiment_engine_aggregate_labels():
    engine = NewsSentimentEngine()
    snap = engine.aggregate_sentiment("BTC/USDT", social_score=0.80)
    assert snap.label in ["VERY_BULLISH", "BULLISH", "NEUTRAL"]

def test_volatility_predictor_horizon_forecast():
    predictor = VolatilityPredictor()
    forecast = predictor.predict_volatility("ETF_APPROVAL", "HIGH")
    assert forecast.expected_volatility_1h_pct > 0
    assert forecast.expected_volatility_24h_pct > forecast.expected_volatility_1h_pct

def test_volatility_predictor_critical_severity():
    predictor = VolatilityPredictor()
    forecast = predictor.predict_volatility("EXCHANGE_HACK", "CRITICAL")
    assert forecast.volatility_regime == "EXTREME_VOLATILITY"

def test_impact_forecaster_bullish_impact():
    forecaster = ImpactForecaster()
    res = forecaster.forecast_impact("BTC/USDT", "ETF_APPROVAL", "BULLISH", "HIGH")
    assert res.impact_1h_pct > 0
    assert res.direction == "BULLISH"

def test_event_signal_engine_exchange_hack_action():
    engine = EventSignalEngine()
    sig = engine.generate_signal("EXCHANGE_HACK", "BTC/USDT")
    assert sig.action == "CLOSE_POSITION"
    assert sig.urgency == "IMMEDIATE"
    assert sig.risk_adjustment["portfolio_heat_cap_pct"] == 30.0

def test_event_signal_engine_etf_approval_action():
    engine = EventSignalEngine()
    sig = engine.generate_signal("ETF_APPROVAL", "BTC/USDT")
    assert sig.action == "BUY"

def test_news_governance_unverified_rumor_block():
    gov = NewsGovernanceEngine()
    res = gov.evaluate_news_event("Unverified Twitter Rumor", "Twitter/X", 0.70, is_unverified_rumor=True)
    assert not res.is_allowed
    assert res.status == "BLOCKED"

def test_news_governance_low_confidence_no_action():
    gov = NewsGovernanceEngine()
    res = gov.evaluate_news_event("Low Confidence Story", "Unknown Source", 0.65)
    assert not res.is_allowed
    assert res.status == "NO_ACTION"

def test_news_governance_approved_flow():
    gov = NewsGovernanceEngine()
    res = gov.evaluate_news_event("SEC Approves Spot ETF", "CoinDesk", 0.95)
    assert res.is_allowed
    assert res.status == "APPROVED"
