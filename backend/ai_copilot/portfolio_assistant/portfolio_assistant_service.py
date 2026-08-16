from typing import Dict, Any, List
from trader import trader_manager
from backend.portfolio_risk import portfolio_risk_orchestrator
from backend.core.logger import logger

class PortfolioAssistantService:
    """Real Conversational & Analytical Portfolio Intelligence Engine."""

    async def get_portfolio_explanation(self, user_id: int = 1) -> Dict[str, Any]:
        trader = await trader_manager.get_trader_for_user(user_id)
        positions = getattr(trader, "positions", {})
        usdt_balance = getattr(trader, "usdt_balance", 0.0)
        initial_balance = getattr(trader, "initial_balance", 10000.0)

        if not positions or len(positions) == 0:
            return {
                "has_data": False,
                "message": "NO PORTFOLIO DATA AVAILABLE",
                "summary": "No active open positions detected for this trading account.",
                "usdt_balance": usdt_balance,
                "initial_balance": initial_balance,
                "total_positions_count": 0,
                "positions_breakdown": [],
                "concentration": [],
                "recommended_actions": ["No action required. Bot is actively scanning market for high-confidence entries."]
            }

        total_margin = sum(p.get("margin_usd", 0.0) for p in positions.values())
        total_pnl = sum(p.get("unrealized_pnl_usd", p.get("unrealized_pnl", 0.0)) for p in positions.values())
        total_value = usdt_balance + total_margin

        # Concentration calculation per symbol
        concentration = []
        for symbol, pos in positions.items():
            pos_margin = pos.get("margin_usd", 0.0)
            pos_pnl = pos.get("unrealized_pnl_usd", pos.get("unrealized_pnl", 0.0))
            conc_pct = (pos_margin / total_value * 100.0) if total_value > 0 else 0.0
            concentration.append({
                "symbol": symbol,
                "margin_usd": pos_margin,
                "concentration_pct": round(conc_pct, 1),
                "side": pos.get("side", "BUY"),
                "unrealized_pnl": round(pos_pnl, 2)
            })

        # Sort by concentration descending
        concentration.sort(key=lambda x: x["concentration_pct"], reverse=True)
        top_asset = concentration[0] if concentration else {"symbol": "NONE", "concentration_pct": 0.0}

        # Recommendations based on actual risk engine rules
        recommendations = []
        if top_asset["concentration_pct"] > 25.0:
            recommendations.append(f"High concentration detected in {top_asset['symbol']} ({top_asset['concentration_pct']}% of portfolio). Consider rebalancing.")
        else:
            recommendations.append(f"Portfolio concentration is well balanced. Top position {top_asset['symbol']} is {top_asset['concentration_pct']}% of portfolio.")

        if total_margin > (total_value * 0.80):
            recommendations.append("Margin utilization is above 80%. Risk engine suggests lowering position sizing.")

        summary_text = (
            f"Portfolio currently holding {len(positions)} active positions with total margin of ${total_margin:,.2f} USDT. "
            f"Total equity value is ${total_value:,.2f} USDT with unrealized PnL of ${total_pnl:,.2f} USDT."
        )

        return {
            "has_data": True,
            "summary": summary_text,
            "usdt_balance": round(usdt_balance, 2),
            "total_margin_usd": round(total_margin, 2),
            "total_value_usd": round(total_value, 2),
            "total_unrealized_pnl": round(total_pnl, 2),
            "active_positions_count": len(positions),
            "top_asset": top_asset["symbol"],
            "top_asset_concentration_pct": top_asset["concentration_pct"],
            "concentration": concentration,
            "recommended_actions": recommendations,
            "active_strategy": getattr(trader, "active_strategy", "AI Hybrid"),
            "risk_mode": getattr(trader, "risk_mode", "BALANCED")
        }

portfolio_assistant_service = PortfolioAssistantService()
