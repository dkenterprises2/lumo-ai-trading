"""
Autonomous Shadow Validation Framework (Phase 42)
Provides deterministic market replay scenarios, lifecycle validation, safety isolation,
and empirical audit reporting for the Lumo Autonomous Trading Engine.
"""

from .validation_scenario import ValidationScenario, ScenarioResult, ValidationState
from .scenario_factory import ScenarioFactory
from .replay_market_feed import ReplayMarketFeed
from .opportunity_injector import OpportunityInjector
from .lifecycle_validator import LifecycleValidator, TransitionRecord
from .validation_metrics import ValidationMetricsCalculator
from .validation_report import ValidationReportGenerator
from .validation_router import router as validation_router

__all__ = [
    "ValidationScenario",
    "ScenarioResult",
    "ValidationState",
    "ScenarioFactory",
    "ReplayMarketFeed",
    "OpportunityInjector",
    "LifecycleValidator",
    "TransitionRecord",
    "ValidationMetricsCalculator",
    "ValidationReportGenerator",
    "validation_router"
]
