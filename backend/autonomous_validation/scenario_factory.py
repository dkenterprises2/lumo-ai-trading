import time
from typing import Dict, List, Optional
from .validation_scenario import ValidationScenario, ReplayTickData, ValidationState

class ScenarioFactory:
    """Factory generating deterministic historical replay validation scenarios (A through J)."""

    @staticmethod
    def get_all_scenarios() -> List[ValidationScenario]:
        return [
            ScenarioFactory.create_scenario_a_profitable(),
            ScenarioFactory.create_scenario_b_unprofitable(),
            ScenarioFactory.create_scenario_c_stale_quote(),
            ScenarioFactory.create_scenario_d_risk_rejection(),
            ScenarioFactory.create_scenario_e_governance_rejection(),
            ScenarioFactory.create_scenario_f_kill_switch(),
            ScenarioFactory.create_scenario_g_position_exit(),
            ScenarioFactory.create_scenario_h_net_edge_decay(),
            ScenarioFactory.create_scenario_i_liquidity_collapse(),
            ScenarioFactory.create_scenario_j_exchange_degradation()
        ]

    @staticmethod
    def get_scenario_by_code(code: str) -> Optional[ValidationScenario]:
        for sc in ScenarioFactory.get_all_scenarios():
            if sc.code.upper() == code.upper() or sc.scenario_id.upper() == code.upper():
                return sc
        return None

    @staticmethod
    def create_scenario_a_profitable() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100500.0,
                buy_depth_usd=150000.0,
                sell_depth_usd=150000.0,
                data_age_ms=15.0,
                status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_A",
            code="SCENARIO_A_PROFITABLE_ARBITRAGE",
            title="Scenario A — Profitable Cross-Exchange Arbitrage",
            description="Gross spread 0.50%, fee/friction 0.19%, net edge +0.31%. Should pass all gates, execute OMS dual-leg fill, and open position.",
            category="PROFITABLE",
            ticks=ticks,
            expected_terminal_state="MONITORING",
            expected_should_execute=True
        )

    @staticmethod
    def create_scenario_b_unprofitable() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100050.0,  # Gross spread 0.05%, fees 0.15% -> Net -0.10%
                buy_depth_usd=100000.0,
                sell_depth_usd=100000.0,
                data_age_ms=12.0,
                status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_B",
            code="SCENARIO_B_UNPROFITABLE_AFTER_FEES",
            title="Scenario B — Unprofitable After Fee & Slippage Friction",
            description="Gross spread 0.05% is insufficient to cover 0.15% friction. Expected rejection at net edge check.",
            category="REJECTION",
            ticks=ticks,
            expected_terminal_state=ValidationState.REJECTED_UNPROFITABLE.value,
            expected_should_execute=False
        )

    @staticmethod
    def create_scenario_c_stale_quote() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100600.0,
                buy_depth_usd=100000.0,
                sell_depth_usd=100000.0,
                data_age_ms=2500.0,  # Stale (> 2000ms)
                status="DATA_STALE"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_C",
            code="SCENARIO_C_STALE_QUOTE",
            title="Scenario C — Stale Quote Rejection",
            description="Quote age 2500ms exceeds maximum 2000ms freshness threshold. Expected stale data rejection.",
            category="REJECTION",
            ticks=ticks,
            expected_terminal_state=ValidationState.REJECTED_STALE_DATA.value,
            expected_should_execute=False
        )

    @staticmethod
    def create_scenario_d_risk_rejection() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100500.0,
                buy_depth_usd=100000.0,
                sell_depth_usd=100000.0,
                data_age_ms=10.0,
                status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_D",
            code="SCENARIO_D_RISK_REJECTION",
            title="Scenario D — Portfolio Risk Gate Rejection",
            description="Evaluated trade breaches max portfolio allocation or risk limit. Expected risk gate block.",
            category="REJECTION",
            ticks=ticks,
            expected_terminal_state=ValidationState.REJECTED_RISK.value,
            expected_should_execute=False,
            requires_risk_breach=True
        )

    @staticmethod
    def create_scenario_e_governance_rejection() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100500.0,
                buy_depth_usd=100000.0,
                sell_depth_usd=100000.0,
                data_age_ms=10.0,
                status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_E",
            code="SCENARIO_E_GOVERNANCE_REJECTION",
            title="Scenario E — Governance & Idempotency Rejection",
            description="Duplicate opportunity key or invalid governance policy. Expected governance block.",
            category="REJECTION",
            ticks=ticks,
            expected_terminal_state=ValidationState.REJECTED_GOVERNANCE.value,
            expected_should_execute=False
        )

    @staticmethod
    def create_scenario_f_kill_switch() -> ValidationScenario:
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT",
                buy_exchange="BINANCE",
                sell_exchange="BYBIT",
                buy_price=100000.0,
                sell_price=100500.0,
                buy_depth_usd=100000.0,
                sell_depth_usd=100000.0,
                data_age_ms=10.0,
                status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_F",
            code="SCENARIO_F_KILL_SWITCH",
            title="Scenario F — Emergency Kill Switch Block",
            description="Kill switch activated (HALTED state) prior to trade submission. Expected immediate block.",
            category="SAFETY",
            ticks=ticks,
            expected_terminal_state=ValidationState.REJECTED_KILL_SWITCH.value,
            expected_should_execute=False,
            requires_kill_switch=True
        )

    @staticmethod
    def create_scenario_g_position_exit() -> ValidationScenario:
        # Tick 1: Open position. Tick 2: Spread converges to 0.
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100500.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            ),
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100250.0, sell_price=100250.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_G",
            code="SCENARIO_G_POSITION_EXIT",
            title="Scenario G — Complete Lifecycle & Spread Convergence Exit",
            description="Position opens cleanly on Tick 1. On Tick 2, spread converges to 0. Exit engine triggers automated position close.",
            category="EXIT",
            ticks=ticks,
            expected_terminal_state="CLOSED",
            expected_should_execute=True,
            expected_should_exit=True
        )

    @staticmethod
    def create_scenario_h_net_edge_decay() -> ValidationScenario:
        # Tick 1: Open position. Tick 2: Net edge decays below 0.15%.
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100600.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            ),
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100100.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_H",
            code="SCENARIO_H_NET_EDGE_DECAY",
            title="Scenario H — Net Edge Decay Exit",
            description="Position opens on valid spread, but spread narrows until net edge < 0.15%. Exit engine triggers automated close.",
            category="EXIT",
            ticks=ticks,
            expected_terminal_state="CLOSED",
            expected_should_execute=True,
            expected_should_exit=True
        )

    @staticmethod
    def create_scenario_i_liquidity_collapse() -> ValidationScenario:
        # Tick 1: Open position. Tick 2: Orderbook depth collapses to 0.
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100500.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            ),
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=0.0, sell_price=0.0, buy_depth_usd=0.0, sell_depth_usd=0.0,
                data_age_ms=10.0, status="DATA_UNAVAILABLE"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_I",
            code="SCENARIO_I_LIQUIDITY_COLLAPSE",
            title="Scenario I — Orderbook Liquidity Collapse Exit",
            description="Orderbook depth collapses to zero on active position. Exit engine triggers emergency unwind.",
            category="EXIT",
            ticks=ticks,
            expected_terminal_state="CLOSED",
            expected_should_execute=True,
            expected_should_exit=True
        )

    @staticmethod
    def create_scenario_j_exchange_degradation() -> ValidationScenario:
        # Tick 1: Open position. Tick 2: News security alert / exchange hack event.
        ticks = [
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100500.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH"
            ),
            ReplayTickData(
                symbol="BTC/USDT", buy_exchange="BINANCE", sell_exchange="BYBIT",
                buy_price=100000.0, sell_price=100500.0, buy_depth_usd=100000.0, sell_depth_usd=100000.0,
                data_age_ms=10.0, status="FRESH", news_alert="EXCHANGE_HACK", exchange_health="DEGRADED"
            )
        ]
        return ValidationScenario(
            scenario_id="SCENARIO_J",
            code="SCENARIO_J_EXCHANGE_DEGRADATION",
            title="Scenario J — News Alert / Exchange Health Degradation Exit",
            description="Critical exchange security incident (EXCHANGE_HACK) reported. Exit engine triggers immediate protective position exit.",
            category="EXIT",
            ticks=ticks,
            expected_terminal_state="CLOSED",
            expected_should_execute=True,
            expected_should_exit=True
        )
