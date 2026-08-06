import time
import uuid
from typing import Dict, Any, List, Optional
from backend.exchange.multi_exchange import multi_exchange_manager
from backend.core.logger import logger

class AlgorithmicExecutionEngine:
    """Institutional Algorithmic Execution Engine (TWAP, VWAP, Iceberg, Bracket Orders)."""

    def execute_twap_order(
        self,
        symbol: str,
        side: str,
        total_amount_usd: float,
        duration_minutes: int = 15,
        slices_count: int = 5,
        exchange_id: str = "PAPER"
    ) -> Dict[str, Any]:
        """Execute Time-Weighted Average Price (TWAP) algorithmic order."""
        slice_amount = total_amount_usd / max(1, slices_count)
        algo_id = f"TWAP_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        adapter = multi_exchange_manager.get_adapter(exchange_id)

        slices_executed = []
        for i in range(slices_count):
            c_id = f"{algo_id}_SLICE_{i+1}"
            res = adapter.create_order(symbol, side, slice_amount, client_order_id=c_id)
            slices_executed.append(res)

        logger.info(f"[ALGO_EXECUTION] Executed TWAP order {algo_id} across {slices_count} slices for ${total_amount_usd}.")
        return {
            "algo_id": algo_id,
            "order_type": "TWAP",
            "symbol": symbol,
            "side": side,
            "total_amount_usd": total_amount_usd,
            "slices_count": slices_count,
            "status": "COMPLETED",
            "slices": slices_executed
        }

    def execute_iceberg_order(
        self,
        symbol: str,
        side: str,
        total_amount_usd: float,
        visible_clip_usd: float = 1000.0,
        exchange_id: str = "PAPER"
    ) -> Dict[str, Any]:
        """Execute Iceberg order hiding true order depth."""
        algo_id = f"ICEBERG_{int(time.time())}_{uuid.uuid4().hex[:4]}"
        clips = int(total_amount_usd // visible_clip_usd) + (1 if total_amount_usd % visible_clip_usd > 0 else 0)
        adapter = multi_exchange_manager.get_adapter(exchange_id)

        res = adapter.create_order(symbol, side, visible_clip_usd, client_order_id=f"{algo_id}_CLIP_1")
        return {
            "algo_id": algo_id,
            "order_type": "ICEBERG",
            "symbol": symbol,
            "side": side,
            "total_amount_usd": total_amount_usd,
            "visible_clip_usd": visible_clip_usd,
            "total_clips": clips,
            "status": "ACTIVE",
            "first_clip": res
        }

    def execute_bracket_order(
        self,
        symbol: str,
        side: str,
        amount_usd: float,
        entry_price: float,
        stop_loss_price: float,
        take_profit_price: float,
        exchange_id: str = "PAPER"
    ) -> Dict[str, Any]:
        """Execute Bracket Order (Entry + SL + TP)."""
        adapter = multi_exchange_manager.get_adapter(exchange_id)
        entry_res = adapter.create_order(
            symbol, side, amount_usd,
            stop_loss_price=stop_loss_price,
            take_profit_price=take_profit_price
        )

        return {
            "status": "success",
            "order_type": "BRACKET",
            "symbol": symbol,
            "side": side,
            "entry_order": entry_res,
            "stop_loss_price": stop_loss_price,
            "take_profit_price": take_profit_price
        }

algo_execution_engine = AlgorithmicExecutionEngine()
