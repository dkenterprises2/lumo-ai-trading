"use client";

import React, { useState, useMemo } from "react";
import { Position } from "@/types/trading";
import { Crosshair, XCircle, RefreshCw, Percent, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

interface ActivePositionsTableProps {
  positions: Position[];
  onAction: (symbol: string, action: "CLOSE" | "PARTIAL_CLOSE" | "REVERSE") => void;
}

type SortField = "symbol" | "side" | "leverage" | "entry_price" | "margin_usd" | "unrealized_pnl_usd";
type SortDirection = "asc" | "desc";

export function ActivePositionsTable({ positions, onAction }: ActivePositionsTableProps) {
  const [sortField, setSortField] = useState<SortField>("margin_usd");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === "desc" ? "asc" : "desc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const sortedPositions = useMemo(() => {
    if (!positions || positions.length === 0) return [];
    return [...positions].sort((a, b) => {
      let valA: any = a[sortField];
      let valB: any = b[sortField];

      if (sortField === "unrealized_pnl_usd") {
        valA = a.unrealized_pnl_usd ?? 0;
        valB = b.unrealized_pnl_usd ?? 0;
      }

      if (typeof valA === "string") {
        return sortDirection === "asc"
          ? valA.localeCompare(valB)
          : valB.localeCompare(valA);
      }

      return sortDirection === "asc"
        ? (valA > valB ? 1 : -1)
        : (valA < valB ? 1 : -1);
    });
  }, [positions, sortField, sortDirection]);

  const renderSortIndicator = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 opacity-40 group-hover:opacity-100 transition-opacity" />;
    }
    return sortDirection === "desc" ? (
      <ArrowDown className="w-3.5 h-3.5 text-cyan-400" />
    ) : (
      <ArrowUp className="w-3.5 h-3.5 text-cyan-400" />
    );
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400">
            <Crosshair className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Active Open Positions</h3>
            <p className="text-xs text-slate-400">Click column headers to sort High to Low / Low to High</p>
          </div>
        </div>

        <span className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          {positions ? positions.length : 0} Positions Open
        </span>
      </div>

      <div className="overflow-x-auto max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-slate-950/95 backdrop-blur-md text-slate-400 border-b border-slate-800 select-none z-10">
            <tr>
              <th onClick={() => handleSort("symbol")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Symbol</span> {renderSortIndicator("symbol")}
                </div>
              </th>
              <th onClick={() => handleSort("side")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Side</span> {renderSortIndicator("side")}
                </div>
              </th>
              <th onClick={() => handleSort("leverage")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Leverage</span> {renderSortIndicator("leverage")}
                </div>
              </th>
              <th onClick={() => handleSort("entry_price")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Entry / Current</span> {renderSortIndicator("entry_price")}
                </div>
              </th>
              <th onClick={() => handleSort("margin_usd")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Margin</span> {renderSortIndicator("margin_usd")}
                </div>
              </th>
              <th onClick={() => handleSort("unrealized_pnl_usd")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Unrealized PnL ($)</span> {renderSortIndicator("unrealized_pnl_usd")}
                </div>
              </th>
              <th className="py-2.5 px-3 font-semibold text-right">Quick Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200 font-medium">
            {(!sortedPositions || sortedPositions.length === 0) ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No active open positions. Submit order or enable Auto-Bot.
                </td>
              </tr>
            ) : (
              sortedPositions.map((pos) => {
                const isLong = pos.side === "LONG";
                const pnlVal = pos.unrealized_pnl_usd || 0;
                const pctVal = pos.unrealized_pnl_pct || 0;
                const isProfit = pnlVal >= 0;
                const formattedMoney = isProfit ? `+$${pnlVal.toFixed(2)}` : `-$${Math.abs(pnlVal).toFixed(2)}`;
                const formattedPct = isProfit ? `+${pctVal.toFixed(2)}%` : `-${Math.abs(pctVal).toFixed(2)}%`;

                return (
                  <tr key={pos.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-3 font-bold text-slate-100">{pos.symbol}</td>
                    <td className="py-3 px-3">
                      <span
                        className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${
                          isLong
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {pos.side}
                      </span>
                    </td>
                    <td className="py-3 px-3 font-mono text-slate-400">{pos.leverage}x</td>
                    <td className="py-3 px-3 font-mono">
                      <div>${pos.entry_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                      <div className="text-[10px] text-slate-400">${pos.current_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</div>
                    </td>
                    <td className="py-3 px-3 font-mono font-bold text-cyan-300">${pos.margin_usd.toFixed(2)}</td>
                    <td className={`py-3 px-3 font-mono font-bold ${isProfit ? "text-emerald-400" : "text-rose-400"}`}>
                      {formattedMoney} ({formattedPct})
                    </td>

                    <td className="py-3 px-3 text-right">
                      <div className="flex items-center justify-end gap-1.5">
                        <button
                          onClick={() => onAction(pos.symbol, "CLOSE")}
                          className="px-2.5 py-1 rounded-lg bg-rose-500/10 border border-rose-500/30 text-rose-400 hover:bg-rose-500/20 text-[11px] font-semibold flex items-center gap-1 transition"
                        >
                          <XCircle className="h-3 w-3" />
                          <span>Close</span>
                        </button>
                        <button
                          onClick={() => onAction(pos.symbol, "PARTIAL_CLOSE")}
                          className="px-2 py-1 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:bg-slate-700 text-[11px] font-semibold flex items-center gap-1 transition"
                        >
                          <Percent className="h-3 w-3" />
                          <span>50%</span>
                        </button>
                        <button
                          onClick={() => onAction(pos.symbol, "REVERSE")}
                          className="px-2 py-1 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400 hover:bg-amber-500/20 text-[11px] font-semibold flex items-center gap-1 transition"
                        >
                          <RefreshCw className="h-3 w-3" />
                          <span>Reverse</span>
                        </button>
                      </div>
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

