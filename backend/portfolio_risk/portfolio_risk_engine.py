import time
from typing import Dict, List, Any, Optional

from .portfolio_state import PortfolioRiskState
from .correlation_engine import CorrelationEngine
from .covariance_engine import CovarianceEngine
from .concentration_engine import ConcentrationEngine
from .portfolio_heat import PortfolioHeatEngine
from .volatility_engine import VolatilityEngine
from .drawdown_engine import DrawdownEngine
from .streak_engine import StreakEngine
from .regime_risk_engine import RegimeRiskEngine
from .leverage_engine import LeverageEngine
from .position_sizing import PositionSizingEngine
from .kelly_sizing import KellySizingEngine
from .dynamic_trade_limit import DynamicTradeLimitEngine
from .exposure_allocator import ExposureAllocator
from .risk_budget import RiskBudgetTracker
from .kill_switch import PortfolioKillSwitch
from .user_risk_profile import UserRiskProfileManager
from .risk_recommendation import RiskRecommendationEngine
from .risk_explainability import RiskExplainabilityEngine
from .risk_governance import RiskGovernanceEngine

class InstitutionalPortfolioRiskEngine:
    """Master Institutional Portfolio Intelligence & Risk Engine Coordinating All Sub-Engines."""

    def __init__(self):
        self.correlation_engine = CorrelationEngine()
        self.covariance_engine = CovarianceEngine()
        self.concentration_engine = ConcentrationEngine()
        self.heat_engine = PortfolioHeatEngine()
        self.volatility_engine = VolatilityEngine()
        self.drawdown_engine = DrawdownEngine()
        self.streak_engine = StreakEngine()
        self.regime_engine = RegimeRiskEngine()
        self.leverage_engine = LeverageEngine()
        self.sizing_engine = PositionSizingEngine()
        self.kelly_engine = KellySizingEngine()
        self.limit_engine = DynamicTradeLimitEngine()
        self.exposure_allocator = ExposureAllocator()
        self.budget_tracker = RiskBudgetTracker()
        self.kill_switch = PortfolioKillSwitch()
        self.profile_manager = UserRiskProfileManager()
        self.recommendation_engine = RiskRecommendationEngine()
        self.explainability_engine = RiskExplainabilityEngine()
        self.governance_engine = RiskGovernanceEngine()

    def evaluate_portfolio_state(
        self,
        user_id: str,
        user_trader,
        market_prices: Optional[Dict[str, float]] = None
    ) -> PortfolioRiskState:
        """Build full PortfolioRiskState snapshot."""
        prices = market_prices or {}
        summary = user_trader.get_portfolio_summary(prices)
        positions = user_trader.positions
        trade_history = user_trader.trade_history

        eq = summary.get("total_portfolio_value", user_trader.usdt_balance)
        avail = user_trader.usdt_balance
        unrealized = summary.get("total_unrealized_pnl_usd", 0.0)
        daily_pnl = summary.get("daily_pnl_usd", 0.0)

        # 1. Peak Equity & Drawdown
        peak_eq = getattr(user_trader, 'peak_equity', eq)
        if eq > peak_eq:
            user_trader.peak_equity = eq
            peak_eq = eq
        dd_usd = max(0.0, peak_eq - eq)
        dd_pct = (dd_usd / (peak_eq + 1e-9)) * 100.0

        dd_adj = self.drawdown_engine.compute_drawdown_adjustment(dd_pct)

        # 2. Correlation & Concentration Analysis
        corr_res = self.correlation_engine.analyze_positions_correlation(positions, eq)
        conc_res = self.concentration_engine.evaluate_concentration(positions, eq)

        # 3. Portfolio Heat Analysis
        heat_res = self.heat_engine.compute_heat(positions, eq, corr_res["correlation_risk_score"])

        # 4. Volatility Analysis
        vol_res = self.volatility_engine.analyze_volatility(atr_pct=2.0, realized_vol_pct=25.0)

        # 5. Streak Analysis
        streak_res = self.streak_engine.analyze_streaks(trade_history)

        # 6. Regime Analysis
        regime_res = self.regime_engine.evaluate_regime_risk("BULL")

        # 7. Risk Budget Analysis
        budget_res = self.budget_tracker.compute_budget(user_trader.initial_balance, daily_pnl)

        # 8. Dynamic Trade Limit Analysis
        configured_max = getattr(user_trader, 'max_open_positions', 10)
        if hasattr(user_trader, 'risk_manager') and hasattr(user_trader.risk_manager, 'config'):
            configured_max = getattr(user_trader.risk_manager.config, 'max_concurrent_trades', configured_max)
        if not configured_max or configured_max <= 0:
            configured_max = 10

        limit_res = self.limit_engine.compute_effective_limit(
            user_configured_max_positions=configured_max,
            currently_open_positions=len(positions),
            portfolio_heat_status=heat_res.status,
            drawdown_pct=dd_pct,
            correlation_risk_score=corr_res["correlation_risk_score"],
            volatility_regime=vol_res.volatility_regime,
            daily_loss_used_pct=budget_res.used_today_pct,
            max_daily_loss_pct=budget_res.daily_budget_pct,
            is_kill_switch_halted=(self.kill_switch.status == "HALTED")
        )


        # 9. Evaluate Kill Switch Triggers
        ks_status = self.kill_switch.evaluate_triggers(
            daily_loss_breached=budget_res.status == "EXHAUSTED",
            drawdown_breached=dd_adj.trading_status == "HALTED",
            portfolio_heat_critical=heat_res.status == "CRITICAL"
        )

        # Overall Status & Risk Score Calculation
        overall_status = "HEALTHY"
        if ks_status.is_active:
            overall_status = "HALTED"
        elif heat_res.status == "CRITICAL" or dd_adj.trading_status == "HALTED":
            overall_status = "HALTED"
        elif heat_res.status in ["HIGH", "WARNING"] or budget_res.status == "WARNING":
            overall_status = "WARNING"

        risk_score = min(100.0, (corr_res["correlation_risk_score"] * 30.0) + (conc_res.concentration_risk_score * 30.0) + (heat_res.utilization_pct * 0.40))

        return PortfolioRiskState(
            user_id=str(user_id),
            equity=round(eq, 2),
            available_balance=round(avail, 2),
            unrealized_pnl=round(unrealized, 2),
            realized_pnl_today=round(daily_pnl, 2),
            drawdown_pct=round(dd_pct, 2),
            volatility_regime=vol_res.volatility_regime,
            market_regime=regime_res.market_regime,
            open_positions=len(positions),
            configured_max_positions=configured_max,
            dynamic_max_positions=limit_res.dynamic_risk_limit,
            effective_max_positions=limit_res.effective_max_positions,
            portfolio_heat_pct=heat_res.net_heat_pct,
            correlation_risk_score=corr_res["correlation_risk_score"],
            concentration_risk_score=conc_res.concentration_risk_score,
            leverage_used=1.0,
            recommended_max_leverage=2.0,
            risk_budget_remaining_pct=budget_res.remaining_daily_pct,
            risk_score=round(risk_score, 2),
            overall_status=overall_status,
            timestamp=time.time(),
            metadata={
                "correlation": corr_res,
                "concentration": conc_res.to_dict(),
                "heat": heat_res.to_dict(),
                "volatility": vol_res.to_dict(),
                "drawdown": dd_adj.to_dict(),
                "streak": streak_res.to_dict(),
                "regime": regime_res.to_dict(),
                "budget": budget_res.to_dict(),
                "trade_limit": limit_res.to_dict(),
                "kill_switch": ks_status.to_dict()
            }
        )

    def evaluate_trade_risk_gate(
        self,
        user_trader,
        symbol: str,
        side: str,
        requested_allocation_usd: float,
        requested_leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """Core Execution Risk Gate evaluating whether a new trade signal is ALLOWED, SCALED, or BLOCKED."""
        try:
            p_state = self.evaluate_portfolio_state(str(user_trader.user_id), user_trader)

            # 1. Kill Switch Check
            if self.kill_switch.is_halted:
                exp = self.explainability_engine.format_explanation(
                    decision="BLOCKED",
                    symbol=symbol,
                    side=side,
                    requested_alloc=requested_allocation_usd,
                    approved_alloc=0.0,
                    effective_limit=p_state.effective_max_positions,
                    open_positions=p_state.open_positions,
                    rem_budget_pct=p_state.risk_budget_remaining_pct,
                    primary_factor="KILL_SWITCH_HALTED",
                    reasons=[f"Kill-Switch active: {self.kill_switch.trigger_reason}"]
                )
                return {"passed": False, "decision": exp.to_dict()}

            # 2. Dynamic Trade Limit Check
            meta_limit = p_state.metadata.get("trade_limit", {})
            if not meta_limit.get("can_open_new_trade", True):
                factor = meta_limit.get("constraining_factor", "DYNAMIC_LIMIT_REACHED")
                exp = self.explainability_engine.format_explanation(
                    decision="BLOCKED",
                    symbol=symbol,
                    side=side,
                    requested_alloc=requested_allocation_usd,
                    approved_alloc=0.0,
                    effective_limit=p_state.effective_max_positions,
                    open_positions=p_state.open_positions,
                    rem_budget_pct=p_state.risk_budget_remaining_pct,
                    primary_factor=factor,
                    reasons=[f"Active positions ({p_state.open_positions}) reached dynamic limit ({p_state.effective_max_positions}). Constrained by {factor}."]
                )
                return {"passed": False, "decision": exp.to_dict()}

            # 3. Position Sizing & Risk Multipliers
            vol_mult = p_state.metadata.get("volatility", {}).get("position_size_multiplier", 1.0)
            dd_mult = p_state.metadata.get("drawdown", {}).get("risk_multiplier", 1.0)
            streak_mult = p_state.metadata.get("streak", {}).get("streak_risk_multiplier", 1.0)
            regime_mult = p_state.metadata.get("regime", {}).get("position_size_multiplier", 1.0)

            sizing_res = self.sizing_engine.compute_size(
                base_allocation_usd=requested_allocation_usd,
                portfolio_equity=p_state.equity,
                max_capital_per_trade_pct=10.0,
                volatility_mult=vol_mult,
                drawdown_mult=dd_mult,
                streak_mult=streak_mult,
                regime_mult=regime_mult
            )

            # 4. Leverage Recommendation
            lev_rec = self.leverage_engine.evaluate_leverage(
                requested_leverage=requested_leverage,
                user_max_leverage=getattr(user_trader, 'default_leverage', 10),
                volatility_multiplier=vol_mult,
                drawdown_pct=p_state.drawdown_pct,
                portfolio_heat_status=p_state.overall_status
            )

            approved_alloc = sizing_res.recommended_allocation_usd
            decision = "ALLOWED" if approved_alloc == requested_allocation_usd else "SCALED"

            exp = self.explainability_engine.format_explanation(
                decision=decision,
                symbol=symbol,
                side=side,
                requested_alloc=requested_allocation_usd,
                approved_alloc=approved_alloc,
                effective_limit=p_state.effective_max_positions,
                open_positions=p_state.open_positions,
                rem_budget_pct=p_state.risk_budget_remaining_pct,
                primary_factor="RISK_SCALING_APPLIED" if decision == "SCALED" else "RISK_VALIDATION_PASSED",
                reasons=[sizing_res.reason, lev_rec.reason]
            )

            return {
                "passed": True,
                "approved_allocation_usd": approved_alloc,
                "approved_leverage": int(lev_rec.recommended),
                "decision": exp.to_dict()
            }
        except Exception as e:
            # FAIL-SAFE: Any risk calculation failure MUST block new trades!
            exp = self.explainability_engine.format_explanation(
                decision="BLOCKED",
                symbol=symbol,
                side=side,
                requested_alloc=requested_allocation_usd,
                approved_alloc=0.0,
                effective_limit=0,
                open_positions=len(getattr(user_trader, 'positions', {})),
                rem_budget_pct=0.0,
                primary_factor="RISK_CALCULATION_FAILSAFE",
                reasons=[f"Fail-safe activated: Risk engine exception: {str(e)}"]
            )
            return {"passed": False, "decision": exp.to_dict()}
