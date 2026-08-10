from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, Request, status

from pydantic import BaseModel, Field

from backend.models.domain import UserModel
from backend.auth.security import get_current_user
from backend.repositories.trading_preferences_repo import trading_preferences_repo

router = APIRouter(prefix="/api/preferences", tags=["Trading Preferences"])

class TradingPreferencesUpdateRequest(BaseModel):
    max_concurrent_trades: Optional[int] = Field(None, ge=1, le=100, description="Max allowed concurrent open positions")
    max_capital_per_trade_pct: Optional[float] = Field(None, ge=0.5, le=100.0, description="Max capital allocation per trade (%)")
    daily_loss_limit_pct: Optional[float] = Field(None, ge=0.5, le=50.0, description="Max allowed daily loss (%)")
    symbol_cooldown_minutes: Optional[int] = Field(None, ge=0, le=1440, description="Symbol re-entry cooldown window (minutes)")
    allowed_symbols: Optional[List[str]] = Field(None, description="Whitelist of allowed trading symbols")


async def get_optional_user(request: Request) -> Optional[UserModel]:
    """Extract authenticated user or return None for default preferences."""
    try:
        from backend.auth.security import get_current_user, get_db
        # Attempt to decode token manually if header or cookie exists
        auth_header = request.headers.get("Authorization")
        token = None
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        elif "access_token" in request.cookies:
            token = request.cookies.get("access_token")

        if token:
            from backend.auth.security import decode_token
            payload = decode_token(token)
            if payload and payload.get("sub"):
                user_id = int(payload["sub"])
                return UserModel(id=user_id, email=payload.get("email", "trader@lumo.trade"))
    except Exception:
        pass
    return None



@router.get("/trading")
async def get_trading_preferences(current_user: Optional[UserModel] = Depends(get_optional_user)):
    """Fetch current user's trading risk preferences and plan tier limits."""
    user_id = current_user.id if current_user else 1
    user_plan = getattr(current_user, "subscription_plan", "FREE") or "FREE"
    if hasattr(current_user, "trading_mode") and current_user.trading_mode == "INSTITUTIONAL":
        user_plan = "INSTITUTIONAL"

    prefs = await trading_preferences_repo.get_by_user_id(user_id)
    plan_max_trades = trading_preferences_repo.get_max_concurrent_limit_for_plan(user_plan)

    data = prefs.to_dict()
    data["plan_tier"] = user_plan.upper()
    data["plan_max_concurrent_trades"] = plan_max_trades

    return {
        "status": "success",
        "data": data
    }


@router.put("/trading")
async def update_trading_preferences(
    body: TradingPreferencesUpdateRequest,
    current_user: Optional[UserModel] = Depends(get_optional_user)
):
    """Validate and update user's trading preferences within plan tier limits."""
    user_id = current_user.id if current_user else 1
    user_plan = getattr(current_user, "subscription_plan", "FREE") or "FREE"
    if hasattr(current_user, "trading_mode") and current_user.trading_mode == "INSTITUTIONAL":
        user_plan = "INSTITUTIONAL"

    updates = body.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid fields provided for update."
        )

    updated_prefs, error_msg = await trading_preferences_repo.update_by_user_id(
        user_id=user_id,
        updates=updates,
        user_plan=user_plan
    )

    if error_msg:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    plan_max_trades = trading_preferences_repo.get_max_concurrent_limit_for_plan(user_plan)
    data = updated_prefs.to_dict()
    data["plan_tier"] = user_plan.upper()
    data["plan_max_concurrent_trades"] = plan_max_trades

    return {
        "status": "success",
        "message": "Trading preferences updated successfully.",
        "data": data
    }
