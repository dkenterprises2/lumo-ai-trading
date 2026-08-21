from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel

from backend.auth.security import get_optional_current_user
from backend.models.domain import UserModel
from backend.wallet.sub_wallet_manager import sub_wallet_manager

router = APIRouter(tags=["Multi-Wallet Sub-Account Ledger"])

class WalletTransferRequest(BaseModel):
    from_wallet: str  # funding, spot, arbitrage, shadow
    to_wallet: str
    asset: str = "USDT"
    amount: float

@router.get("/api/wallets/summary")
@router.get("/api/wallet/summary")
async def get_wallet_summary(current_user: Optional[UserModel] = Depends(get_optional_current_user)):
    """Fetch live balances across all 4 isolated sub-wallets (Funding, Spot, Arbitrage, Shadow)."""
    return sub_wallet_manager.get_summary()

@router.post("/api/wallets/transfer")
@router.post("/api/wallet/transfer")
async def transfer_wallet_funds(
    body: WalletTransferRequest,
    current_user: Optional[UserModel] = Depends(get_optional_current_user)
):
    """Instant 0-fee internal transfer between sub-wallets."""
    try:
        res = sub_wallet_manager.transfer_funds(
            from_wallet=body.from_wallet,
            to_wallet=body.to_wallet,
            asset=body.asset,
            amount=body.amount
        )
        return res
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(ex)}")
