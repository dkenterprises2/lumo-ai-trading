import pytest
from backend.arbitrage import (
    ExchangePriceCollector,
    SpreadDetector,
    FundingRateCollector,
    BasisSpreadEngine,
    TriangularArbitrageEngine,
    CrossExchangeArbitrageEngine,
    ArbitrageOpportunityRanker,
    ArbitrageRiskFilter,
    ArbitrageExecutionSimulator,
    ArbitrageShadowRouter,
    ArbitrageMetricsTracker,
    ArbitrageGovernance
)

def test_exchange_price_collector_all_venues():
    collector = ExchangePriceCollector()
    quotes = collector.fetch_all_quotes("BTC/USDT", 118450.0)
    assert len(quotes) == 5
    assert "BINANCE" in quotes
    assert "BYBIT" in quotes
    assert "OKX" in quotes
    assert "KRAKEN" in quotes
    assert "COINBASE" in quotes

def test_exchange_quote_structure():
    collector = ExchangePriceCollector()
    quotes = collector.fetch_all_quotes("BTC/USDT", 118450.0)
    q = quotes["BINANCE"]
    assert q.symbol == "BTC/USDT"
    assert q.ask_price >= q.bid_price
    assert q.spread_bps >= 0

def test_spread_detector_gross_calculation():
    detector = SpreadDetector()
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 10000.0, 10100.0)
    assert spread.gross_spread_usd == 100.0
    assert spread.gross_spread_pct == 1.0

def test_spread_detector_fee_deduction():
    detector = SpreadDetector()
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 10000.0, 10100.0, buy_fee_bps=7.5, sell_fee_bps=7.5)
    assert spread.total_fees_bps == 15.0

def test_spread_detector_latency_penalty():
    detector = SpreadDetector()
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 10000.0, 10100.0, latency_ms=100.0)
    assert spread.latency_penalty_bps == 1.5

def test_spread_detector_executable_threshold():
    detector = SpreadDetector()
    # Tiny spread (net edge < 0.15%)
    spread = detector.compute_spread("BTC/USDT", "BINANCE", "BYBIT", 10000.0, 10010.0)
    assert not spread.is_executable

def test_funding_rate_collector_structure():
    collector = FundingRateCollector()
    rates = collector.fetch_funding_rates("BTC/USDT")
    assert len(rates) == 4
    assert "BINANCE" in rates

def test_funding_rate_annualization():
    collector = FundingRateCollector()
    rates = collector.fetch_funding_rates("BTC/USDT")
    binance_rate = rates["BINANCE"]
    expected_ann = round(0.0001 * 3 * 365 * 100, 2)
    assert binance_rate.annualized_funding_pct == expected_ann

def test_basis_spread_engine_calculation():
    engine = BasisSpreadEngine()
    res = engine.evaluate_basis("BTC/USDT", "BINANCE", spot_price=100000.0, perp_mark_price=101000.0, days_to_expiry=365)
    assert res.basis_usd == 1000.0
    assert res.annualized_basis_pct == 1.0

def test_basis_spread_engine_threshold():
    engine = BasisSpreadEngine()
    res = engine.evaluate_basis("BTC/USDT", "BINANCE", spot_price=100000.0, perp_mark_price=109000.0, days_to_expiry=365)
    assert res.is_actionable

def test_triangular_arbitrage_math():
    engine = TriangularArbitrageEngine()
    opp = engine.evaluate_triangular_route("BINANCE", pair_a_price=100.0, pair_b_price=0.01, pair_c_price=1.05)
    assert opp.implied_multiplier == 1.05

def test_triangular_arbitrage_fee_deduction():
    engine = TriangularArbitrageEngine()
    opp = engine.evaluate_triangular_route("BINANCE", pair_a_price=100.0, pair_b_price=0.01, pair_c_price=1.05)
    assert opp.profit_pct < 5.0  # Fees deducted

def test_cross_exchange_scan_opportunities():
    engine = CrossExchangeArbitrageEngine()
    opps = engine.scan_opportunities("BTC/USDT")
    assert isinstance(opps, list)

def test_opportunity_ranker_ordering():
    ranker = ArbitrageOpportunityRanker()
    class DummyOpp:
        def __init__(self, net_spread):
            self.net_spread_pct = net_spread

    opps = [DummyOpp(0.20), DummyOpp(0.85), DummyOpp(0.40)]
    ranked = ranker.rank_opportunities(opps)
    assert ranked[0].net_spread_pct == 0.85

def test_risk_filter_kill_switch_blocking():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.50, kill_switch_state="HALTED")
    assert not res.passed

def test_risk_filter_portfolio_heat_blocking():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.50, portfolio_heat_utilization_pct=80.0)
    assert not res.passed

def test_risk_filter_net_edge_threshold():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.10)
    assert not res.passed

def test_risk_filter_slippage_exceeds_edge():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.20, slippage_bps=25.0)  # 0.25% slippage > 0.20% net edge
    assert not res.passed

def test_risk_filter_degraded_exchange():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.50, exchange_health="DEGRADED")
    assert not res.passed

def test_risk_filter_valid_opportunity_pass():
    rf = ArbitrageRiskFilter()
    res = rf.evaluate_opportunity_risk(net_spread_pct=0.50, slippage_bps=5.0, exchange_health="HEALTHY")
    assert res.passed

def test_arbitrage_execution_simulator_shadow_fills():
    sim = ArbitrageExecutionSimulator()
    res = sim.simulate_arbitrage_execution("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0, 10000.0)
    assert res.status in ["COMPLETED", "SUCCESS"]
    assert res.buy_fill_price > 100000.0

def test_arbitrage_execution_simulator_realized_profit():
    sim = ArbitrageExecutionSimulator()
    res = sim.simulate_arbitrage_execution("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0, 10000.0)
    assert res.profit_usd > 0

def test_arbitrage_shadow_router_approval_flow():
    router = ArbitrageShadowRouter()
    res = router.route_arbitrage_opportunity("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0, net_spread_pct=0.50)
    assert res["status"] == "success"

def test_arbitrage_shadow_router_rejection_flow():
    router = ArbitrageShadowRouter()
    res = router.route_arbitrage_opportunity("BTC/USDT", "BINANCE", "BYBIT", 100000.0, 101000.0, net_spread_pct=0.05)
    assert res["status"] == "rejected"

def test_arbitrage_governance_validation():
    gov = ArbitrageGovernance()
    res = gov.validate_session(portfolio_heat_pct=20.0, kill_switch_state="NORMAL")
    assert res.is_approved

def test_arbitrage_metrics_tracker_summary():
    summary = ArbitrageMetricsTracker.get_summary()
    assert summary.overall_readiness_score > 90.0
