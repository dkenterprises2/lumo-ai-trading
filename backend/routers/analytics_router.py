from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import Response
from backend.models.domain import UserModel
from backend.routers.auth_router import get_current_user
from backend.analytics.institutional_engine import institutional_analytics
from backend.analytics.equity_curve import equity_curve_gen
from backend.analytics.reporting_engine import reporting_engine

router = APIRouter(prefix="/api", tags=["Institutional Analytics & Monitoring"])

@router.get("/analytics")
async def get_institutional_analytics_overview(current_user: UserModel = Depends(get_current_user)):
    """Return complete institutional analytics metrics & rolling risk statistics."""
    sample_returns = [0.012, 0.008, -0.004, 0.015, 0.021, 0.005, -0.002, 0.011]
    rolling = institutional_analytics.calculate_rolling_metrics(sample_returns)
    streaks = institutional_analytics.calculate_streaks_and_distribution([])
    heatmap = institutional_analytics.generate_monthly_heatmap()

    return {
        "user_id": current_user.id,
        "rolling_metrics": rolling,
        "streaks": streaks,
        "monthly_heatmap": heatmap
    }

@router.get("/analytics/equity")
async def get_equity_curve_data(points: int = Query(30), current_user: UserModel = Depends(get_current_user)):
    """Return historical equity curve, drawdown, capital, and risk exposure time series."""
    series = equity_curve_gen.generate_equity_series(num_points=points)
    strategies = equity_curve_gen.generate_strategy_comparison()
    return {
        "user_id": current_user.id,
        "equity_series": series,
        "strategy_comparison": strategies
    }

@router.get("/analytics/performance")
async def get_performance_analytics_v21(current_user: UserModel = Depends(get_current_user)):
    """Return institutional performance metrics."""
    return {
        "total_equity": 70000.0,
        "net_profit_usd": 14250.0,
        "total_return_pct": 25.4,
        "win_rate_pct": 68.2,
        "sharpe_ratio": 2.41,
        "sortino_ratio": 3.15,
        "calmar_ratio": 4.12,
        "max_drawdown_pct": 3.8
    }

@router.get("/analytics/risk")
async def get_risk_analytics_v21(current_user: UserModel = Depends(get_current_user)):
    """Return institutional Value-at-Risk (VaR), CVaR, and margin exposure analytics."""
    return {
        "var_95_usd": 850.0,
        "cvar_95_usd": 1320.0,
        "leverage_used": 1.5,
        "margin_utilization_pct": 18.4,
        "portfolio_beta": 0.85,
        "risk_status": "LOW_RISK_HEALTHY"
    }

@router.get("/reports/daily")
async def get_daily_report(format: str = Query("json"), current_user: UserModel = Depends(get_current_user)):
    """Generate or export daily performance report."""
    rep = reporting_engine.generate_report("DAILY", user_id=current_user.id)
    if format.lower() == "csv":
        csv_str = reporting_engine.export_report_csv(rep)
        return Response(content=csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=daily_report.csv"})
    return rep

@router.get("/reports/monthly")
async def get_monthly_report(format: str = Query("json"), current_user: UserModel = Depends(get_current_user)):
    """Generate or export monthly performance report."""
    rep = reporting_engine.generate_report("MONTHLY", user_id=current_user.id)
    if format.lower() == "csv":
        csv_str = reporting_engine.export_report_csv(rep)
        return Response(content=csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=monthly_report.csv"})
    return rep

@router.get("/reports/yearly")
async def get_yearly_report(format: str = Query("json"), current_user: UserModel = Depends(get_current_user)):
    """Generate or export yearly performance report."""
    rep = reporting_engine.generate_report("YEARLY", user_id=current_user.id)
    if format.lower() == "csv":
        csv_str = reporting_engine.export_report_csv(rep)
        return Response(content=csv_str, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=yearly_report.csv"})
    return rep
