"use client";

import React from "react";
import { TradeRecord } from "@/types/trading";
import { History } from "lucide-react";

interface TradeHistoryTableProps {
  trades: TradeRecord[];
}

export function TradeHistoryTable({ trades }: TradeHistoryTableProps) {
  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
            <History className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Trade History (Executed Orders)</h3>
            <p className="text-xs text-slate-400">Immediate Database Audit Logging</p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
          {trades ? trades.length : 0} Executed
        </span>
      </div>

      <div className="overflow-x-auto max-h-72 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-slate-950/90 backdrop-blur-md text-slate-400 border-b border-slate-800">
            <tr>
              <th className="py-2.5 px-3 font-semibold">ID / Symbol</th>
              <th className="py-2.5 px-3 font-semibold">Side</th>
              <th className="py-2.5 px-3 font-semibold">Entry / Exit Price</th>
              <th className="py-2.5 px-3 font-semibold">Amount</th>
              <th className="py-2.5 px-3 font-semibold">Margin</th>
              <th className="py-2.5 px-3 font-semibold">PnL ($)</th>
              <th className="py-2.5 px-3 font-semibold">PnL (%)</th>
              <th className="py-2.5 px-3 font-semibold text-right">Status / Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200 font-medium">
            {(!trades || trades.length === 0) ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  No trade history records.
                </td>
              </tr>
            ) : (
              trades.map((t) => {
                const isClosed = t.status === "CLOSED" || (t.exit_time && t.exit_time !== "");
                const pnlVal = t.pnl_usd || 0;
                const pctVal = t.pnl_pct || 0;
                const isProfit = pnlVal >= 0;
                const formattedMoney = isProfit ? `+$${pnlVal.toFixed(2)}` : `-$${Math.abs(pnlVal).toFixed(2)}`;
                const formattedPct = isProfit ? `+${pctVal.toFixed(2)}%` : `-${Math.abs(pctVal).toFixed(2)}%`;

                return (
                  <tr key={t.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3">
                      <div className="font-bold text-slate-100">{t.symbol}</div>
                      <div className="text-[10px] text-slate-500 font-mono truncate max-w-[120px]">{t.id}</div>
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          t.side === "LONG"
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {t.side}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono">
                      <div>${t.entry_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                      <div className="text-[10px] text-slate-400">
                        {isClosed ? `$${t.exit_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}` : "-"}
                      </div>
                    </td>
                    <td className="py-3 px-3 font-mono">{t.amount.toFixed(4)}</td>
                    <td className="py-3 px-3 font-mono">${t.margin_usd.toFixed(2)}</td>
                    <td className={`py-3 px-3 font-mono font-bold ${isProfit ? "text-emerald-400" : "text-rose-400"}`}>
                      {isClosed ? formattedMoney : "$0.00"}
                    </td>
                    <td className={`py-3 px-3 font-mono font-bold ${isProfit ? "text-emerald-400" : "text-rose-400"}`}>
                      {isClosed ? formattedPct : "0.0%"}
                    </td>

                    <td className="py-3 px-3 text-right">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          isClosed
                            ? "bg-slate-800 text-slate-300 border border-slate-700"
                            : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                        }`}
                      >
                        {isClosed ? "CLOSED" : "OPEN"}
                      </span>
                      <div className="text-[10px] text-slate-500 mt-1 font-mono">{isClosed ? t.exit_time : t.entry_time}</div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
