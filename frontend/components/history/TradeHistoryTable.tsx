"use client";

import React, { useState, useMemo } from "react";
import { TradeRecord } from "@/types/trading";
import { History, ArrowUpDown, ArrowUp, ArrowDown, Download, FileSpreadsheet } from "lucide-react";

interface TradeHistoryTableProps {
  trades: TradeRecord[];
}

type SortField = "symbol" | "side" | "entry_price" | "amount" | "margin_usd" | "pnl_usd" | "pnl_pct" | "exit_time";
type SortDirection = "asc" | "desc";

export function TradeHistoryTable({ trades }: TradeHistoryTableProps) {
  const [sortField, setSortField] = useState<SortField>("exit_time");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === "desc" ? "asc" : "desc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  const exportTrades = (format: "csv" | "excel") => {
    if (!trades || trades.length === 0) return;

    const headers = [
      "Trade ID",
      "Symbol",
      "Side",
      "Entry Price ($)",
      "Exit Price ($)",
      "Amount",
      "Margin ($)",
      "PnL ($)",
      "PnL (%)",
      "Status",
      "Close Reason",
      "Time"
    ];

    const rows = trades.map(t => [
      `"${t.id}"`,
      `"${t.symbol}"`,
      `"${t.side}"`,
      t.entry_price ? t.entry_price.toFixed(4) : "0",
      t.exit_price ? t.exit_price.toFixed(4) : "0",
      t.amount ? t.amount.toFixed(4) : "0",
      t.margin_usd ? t.margin_usd.toFixed(2) : "0",
      t.pnl_usd ? t.pnl_usd.toFixed(2) : "0",
      t.pnl_pct ? `${t.pnl_pct.toFixed(2)}%` : "0%",
      `"${t.status || 'CLOSED'}"`,
      `"${(t.close_reason || t.reason || '').replace(/"/g, '""')}"`,
      `"${t.exit_time || t.entry_time || ''}"`
    ]);

    const delimiter = format === "csv" ? "," : "\t";
    const mimeType = format === "csv" ? "text/csv;charset=utf-8;" : "application/vnd.ms-excel;charset=utf-8;";
    const filename = `lumo_trade_history_${new Date().toISOString().slice(0, 10)}.${format === "csv" ? "csv" : "xls"}`;

    const content = "\uFEFF" + [headers.join(delimiter), ...rows.map(r => r.join(delimiter))].join("\n");
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const sortedTrades = useMemo(() => {
    if (!trades || trades.length === 0) return [];
    return [...trades].sort((a, b) => {
      let valA: any = a[sortField];
      let valB: any = b[sortField];

      if (sortField === "pnl_usd") {
        valA = a.pnl_usd ?? 0;
        valB = b.pnl_usd ?? 0;
      } else if (sortField === "pnl_pct") {
        valA = a.pnl_pct ?? 0;
        valB = b.pnl_pct ?? 0;
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
  }, [trades, sortField, sortDirection]);

  const renderSortIndicator = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 opacity-40 group-hover:opacity-100 transition-opacity" />;
    }
    return sortDirection === "desc" ? (
      <ArrowDown className="w-3.5 h-3.5 text-blue-400" />
    ) : (
      <ArrowUp className="w-3.5 h-3.5 text-blue-400" />
    );
  };

  return (
    <div className="p-5 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-500/10 text-blue-400">
            <History className="h-5 w-5" />
          </div>
          <div>
            <h3 className="font-bold text-slate-100 text-base">Trade History (Executed Orders)</h3>
            <p className="text-xs text-slate-400">Click column headers to sort High to Low / Low to High</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => exportTrades("csv")}
            disabled={!trades || trades.length === 0}
            className="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-40"
            title="Download Trade History as CSV"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>CSV</span>
          </button>

          <button
            onClick={() => exportTrades("excel")}
            disabled={!trades || trades.length === 0}
            className="px-2.5 py-1 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 text-xs font-semibold flex items-center gap-1.5 transition disabled:opacity-40"
            title="Download Trade History as Excel"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span>Excel</span>
          </button>

          <span className="text-xs font-semibold px-2.5 py-1 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20">
            {trades ? trades.length : 0} Executed
          </span>
        </div>
      </div>


      <div className="overflow-x-auto max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-slate-800">
        <table className="w-full text-left text-xs">
          <thead className="sticky top-0 bg-slate-950/95 backdrop-blur-md text-slate-400 border-b border-slate-800 select-none z-10">
            <tr>
              <th onClick={() => handleSort("symbol")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>ID / Symbol</span> {renderSortIndicator("symbol")}
                </div>
              </th>
              <th onClick={() => handleSort("side")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Side</span> {renderSortIndicator("side")}
                </div>
              </th>
              <th onClick={() => handleSort("entry_price")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Entry / Exit Price</span> {renderSortIndicator("entry_price")}
                </div>
              </th>
              <th onClick={() => handleSort("amount")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Amount</span> {renderSortIndicator("amount")}
                </div>
              </th>
              <th onClick={() => handleSort("margin_usd")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>Margin</span> {renderSortIndicator("margin_usd")}
                </div>
              </th>
              <th onClick={() => handleSort("pnl_usd")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>PnL ($)</span> {renderSortIndicator("pnl_usd")}
                </div>
              </th>
              <th onClick={() => handleSort("pnl_pct")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition group">
                <div className="flex items-center gap-1.5">
                  <span>PnL (%)</span> {renderSortIndicator("pnl_pct")}
                </div>
              </th>
              <th onClick={() => handleSort("exit_time")} className="py-2.5 px-3 font-semibold cursor-pointer hover:text-white transition text-right group">
                <div className="flex items-center justify-end gap-1.5">
                  <span>Status / Time</span> {renderSortIndicator("exit_time")}
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 text-slate-200 font-medium">
            {(!sortedTrades || sortedTrades.length === 0) ? (
              <tr>
                <td colSpan={8} className="py-8 text-center text-slate-500">
                  No trade history records.
                </td>
              </tr>
            ) : (
              sortedTrades.map((t) => {
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
                    <td className="py-3 px-3 font-mono font-bold text-blue-300">${t.margin_usd.toFixed(2)}</td>
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

