from typing import Dict, Any, Optional
from backend.exchange.base import BaseExchangeAdapter

class PaperExchangeAdapter(BaseExchangeAdapter):
    """Paper Trading Exchange Adapter wrapping the underlying PaperTrader engine."""

    def __init__(self, paper_trader):
        self.paper_trader = paper_trader

    def get_exchange_name(self) -> str:
        return "PAPER_EXCHANGE"

    def fetch_ticker(self, symbol: str) -> Dict[str, Any]:
        return {
            "symbol": symbol,
            "last": 65000.0,
            "bid": 64990.0,
            "ask": 65010.0,
            "volume": 10000.0
        }

    def fetch_balance(self) -> Dict[str, Any]:
        summary = self.paper_trader.get_portfolio_summary(current_prices={"BTC/USDT": 65000.0})
        return {
            "total_wallet": summary.get("wallet_balance", 10000.0),
            "free_balance": summary.get("cash_balance", 10000.0),
            "total_equity": summary.get("total_equity", 10000.0)
        }


    def create_order(
        self,
        symbol: str,
        side: str,
        amount_usd: float,
        order_type: str = "MARKET",
        leverage: int = 1,
        stop_loss_price: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        ticker = self.fetch_ticker(symbol)
        price = ticker["last"]
        sl = stop_loss_price or (price * 0.95 if side == "BUY" else price * 1.05)
        tp = take_profit_price or (price * 1.05 if side == "BUY" else price * 0.95)
        return self.paper_trader.open_position(
            symbol=symbol,
            side=side,
            price=price,
            allocation_usd=amount_usd,
            stop_loss_price=sl,
            take_profit_price=tp,
            leverage=leverage
        )


    def close_position(self, symbol: str, price: Optional[float] = None) -> Dict[str, Any]:
        p = price or self.fetch_ticker(symbol)["last"]
        return self.paper_trader.close_position(symbol=symbol, price=p, reason="Exchange Adapter Request")

    def get_positions(self) -> Dict[str, Any]:
        return self.paper_trader.positions
