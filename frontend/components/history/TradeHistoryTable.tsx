"use client";

import React, { useState, useMemo, useEffect } from "react";
import { TradeRecord } from "@/types/trading";
import { History, ArrowUpDown, ArrowUp, ArrowDown, Download, FileSpreadsheet, Zap, Layers, TrendingUp, Search, RefreshCw } from "lucide-react";
import { fetchAllUnifiedTrades } from "@/services/api";

interface TradeHistoryTableProps {
  trades?: TradeRecord[];
}

type SubsystemFilter = "ALL" | "SPOT" | "ARBITRAGE" | "SHADOW";
type SortField = "subsystem" | "symbol" | "venue" | "side" | "entry_price" | "exit_price" | "amount" | "margin_usd" | "pnl_usd" | "pnl_pct" | "status" | "time";
type SortDirection = "asc" | "desc";

export function formatCryptoPrice(price: number | undefined | null): string {
  if (price === undefined || price === null || isNaN(price)) return "$0.00";
  if (price === 0) return "$0.00";
  if (price < 0.0001) return `$${price.toFixed(8)}`;
  if (price < 0.01) return `$${price.toFixed(6)}`;
  if (price < 0.1) return `$${price.toFixed(5)}`;
  if (price < 1.0) return `$${price.toFixed(4)}`;
  return `$${price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 4 })}`;
}

export function TradeHistoryTable({ trades: propTrades }: TradeHistoryTableProps) {
  // Normalize incoming prop trades immediately
  const normalizedPropTrades = useMemo(() => {
    if (!propTrades || !Array.isArray(propTrades) || propTrades.length === 0) return [];
    return propTrades.map((t: any, idx: number) => ({
      id: t.id || `SPOT_${t.symbol || 'PAIR'}_${t.exit_time || t.entry_time || idx}`,
      subsystem: t.subsystem || "SPOT",
      symbol: t.symbol || "UNKNOWN",
      side: t.side || "BUY",
      entry_price: typeof t.entry_price === "number" ? t.entry_price : parseFloat(t.entry_price || "0") || 0,
      exit_price: typeof t.exit_price === "number" ? t.exit_price : parseFloat(t.exit_price || "0") || 0,
      amount: typeof t.amount === "number" ? t.amount : parseFloat(t.amount || "0") || 0,
      margin_usd: typeof t.margin_usd === "number" ? t.margin_usd : parseFloat(t.margin_usd || "0") || 0,
      pnl_usd: typeof t.pnl_usd === "number" ? t.pnl_usd : parseFloat(t.pnl_usd ?? t.net_pnl ?? t.pnl ?? "0") || 0,
      pnl_pct: typeof t.pnl_pct === "number" ? t.pnl_pct : parseFloat(t.pnl_pct || "0") || 0,
      status: t.status || "CLOSED",
      reason: t.close_reason || t.reason || "Spot AI Paper Trading",
      venue: t.exchange || t.venue || "BINANCE",
      time: t.exit_time || t.entry_time || t.time || ""
    }));
  }, [propTrades]);

  const [unifiedTrades, setUnifiedTrades] = useState<any[]>(normalizedPropTrades);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<SubsystemFilter>("ALL");
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [sortField, setSortField] = useState<SortField>("time");
  const [sortDirection, setSortDirection] = useState<SortDirection>("desc");

  // Keep state synchronized with incoming WebSocket prop trades
  useEffect(() => {
    if (normalizedPropTrades.length > 0) {
      setUnifiedTrades(prev => {
        if (!prev || prev.length === 0) {
          return normalizedPropTrades;
        }
        const nonSpot = prev.filter(t => (t.subsystem || "SPOT") !== "SPOT");
        return [...normalizedPropTrades, ...nonSpot];
      });
    }
  }, [normalizedPropTrades]);

  const loadTrades = async () => {
    try {
      setLoading(true);
      const res = await fetchAllUnifiedTrades();
      if (res && Array.isArray(res.trades) && res.trades.length > 0) {
        const spotFromApi = res.trades.filter((t: any) => (t.subsystem || "SPOT") === "SPOT");
        if (spotFromApi.length === 0 && normalizedPropTrades.length > 0) {
          setUnifiedTrades([...normalizedPropTrades, ...res.trades]);
        } else {
          setUnifiedTrades(res.trades);
        }
      } else if (normalizedPropTrades.length > 0) {
        setUnifiedTrades(normalizedPropTrades);
      }
    } catch (e) {
      console.warn("Failed to load unified trades, using prop fallback:", e);
      if (normalizedPropTrades.length > 0) {
        setUnifiedTrades(normalizedPropTrades);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTrades();
    const timer = setInterval(loadTrades, 5000);
    return () => clearInterval(timer);
  }, []);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === "desc" ? "asc" : "desc"));
    } else {
      setSortField(field);
      setSortDirection("desc");
    }
  };

  // Effective trades to display: prioritize unifiedTrades, fallback to normalizedPropTrades
  const effectiveTrades = useMemo(() => {
    if (unifiedTrades && unifiedTrades.length > 0) {
      return unifiedTrades;
    }
    return normalizedPropTrades;
  }, [unifiedTrades, normalizedPropTrades]);

  const filteredTrades = useMemo(() => {
    let list = [...effectiveTrades];

    if (activeTab !== "ALL") {
      list = list.filter(t => (t.subsystem || "SPOT").toUpperCase() === activeTab);
    }

    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(t => 
        (t.symbol || "").toLowerCase().includes(q) ||
        (t.id || "").toLowerCase().includes(q) ||
        (t.venue || "").toLowerCase().includes(q) ||
        (t.reason || "").toLowerCase().includes(q) ||
        (t.status || "").toLowerCase().includes(q)
      );
    }

    list.sort((a, b) => {
      let valA: any = a[sortField];
      let valB: any = b[sortField];

      if (sortField === "pnl_usd") {
        valA = a.pnl_usd ?? 0;
        valB = b.pnl_usd ?? 0;
      } else if (sortField === "pnl_pct") {
        valA = a.pnl_pct ?? 0;
        valB = b.pnl_pct ?? 0;
      } else if (sortField === "entry_price") {
        valA = a.entry_price ?? 0;
        valB = b.entry_price ?? 0;
      } else if (sortField === "exit_price") {
        valA = a.exit_price ?? 0;
        valB = b.exit_price ?? 0;
      } else if (sortField === "amount") {
        valA = a.amount ?? 0;
        valB = b.amount ?? 0;
      } else if (sortField === "margin_usd") {
        valA = a.margin_usd ?? 0;
        valB = b.margin_usd ?? 0;
      }

      if (typeof valA === "string") {
        return sortDirection === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
      }
      return sortDirection === "asc" ? (valA || 0) - (valB || 0) : (valB || 0) - (valA || 0);
    });

    return list;
  }, [effectiveTrades, activeTab, searchQuery, sortField, sortDirection]);

  const exportTrades = (format: "csv" | "excel") => {
    if (!filteredTrades || filteredTrades.length === 0) return;

    const headers = [
      "Trade ID",
      "Engine / Subsystem",
      "Symbol",
      "Venue / Route",
      "Side",
      "Entry Price ($)",
      "Exit/Mark Price ($)",
      "Amount",
      "Margin ($)",
      "PnL ($)",
      "PnL (%)",
      "Status",
      "Strategy / Reason",
      "Time"
    ];

    const rows = filteredTrades.map(t => [
      `"${t.id}"`,
      `"${t.subsystem || 'SPOT'}"`,
      `"${t.symbol}"`,
      `"${t.venue || 'BINANCE'}"`,
      `"${t.side}"`,
      t.entry_price ? (t.entry_price < 0.001 ? t.entry_price.toFixed(8) : t.entry_price.toFixed(4)) : "0",
      t.exit_price ? (t.exit_price < 0.001 ? t.exit_price.toFixed(8) : t.exit_price.toFixed(4)) : "0",
      t.amount ? t.amount.toFixed(4) : "0",
      t.margin_usd ? t.margin_usd.toFixed(2) : "0",
      t.pnl_usd ? t.pnl_usd.toFixed(2) : "0",
      t.pnl_pct ? `${t.pnl_pct.toFixed(2)}%` : "0%",
      `"${t.status || 'CLOSED'}"`,
      `"${(t.reason || '').replace(/"/g, '""')}"`,
      `"${t.time || ''}"`
    ]);

    const delimiter = format === "csv" ? "," : "\t";
    const mimeType = format === "csv" ? "text/csv;charset=utf-8;" : "application/vnd.ms-excel;charset=utf-8;";
    const filename = `lumo_unified_trades_${activeTab.toLowerCase()}_${new Date().toISOString().slice(0, 10)}.${format === "csv" ? "csv" : "xls"}`;

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

  const renderSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-3 h-3 text-slate-500 opacity-40 group-hover:opacity-100" />;
    }
    return sortDirection === "asc" ? (
      <ArrowUp className="w-3.5 h-3.5 text-cyan-400 font-bold" />
    ) : (
      <ArrowDown className="w-3.5 h-3.5 text-cyan-400 font-bold" />
    );
  };

  const spotCount = effectiveTrades.filter(t => (t.subsystem || "SPOT") === "SPOT").length;
  const arbCount = effectiveTrades.filter(t => t.subsystem === "ARBITRAGE").length;
  const shadowCount = effectiveTrades.filter(t => t.subsystem === "SHADOW").length;

  return (
    <div className="space-y-4">
      {/* Control Banner & Subsystem Tabs */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900 border border-slate-800">
        
        {/* Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto">
          {[
            { id: "ALL", label: `All Trades (${effectiveTrades.length})`, icon: History },
            { id: "SPOT", label: `Spot AI (${spotCount})`, icon: TrendingUp, color: "text-cyan-400" },
            { id: "ARBITRAGE", label: `Arbitrage (${arbCount})`, icon: Zap, color: "text-amber-400" },
            { id: "SHADOW", label: `Shadow Replay (${shadowCount})`, icon: Layers, color: "text-purple-400" }
          ].map((tab) => {
            const Icon = tab.icon;
            const active = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as SubsystemFilter)}
                className={`px-3.5 py-2 rounded-xl text-xs font-bold transition flex items-center gap-2 cursor-pointer whitespace-nowrap ${
                  active
                    ? "bg-slate-800 text-white border border-slate-700 shadow-md"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${tab.color || "text-slate-400"}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Search & Export Buttons */}
        <div className="flex items-center gap-2">
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              placeholder="Search symbol, route, status..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-xl pl-8 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 w-44 sm:w-56 font-mono"
            />
          </div>

          <button
            onClick={() => exportTrades("csv")}
            disabled={filteredTrades.length === 0}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition flex items-center gap-1.5 border border-slate-700 cursor-pointer disabled:opacity-50"
            title="Download CSV"
          >
            <Download className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">CSV</span>
          </button>

          <button
            onClick={() => exportTrades("excel")}
            disabled={filteredTrades.length === 0}
            className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold rounded-xl transition flex items-center gap-1.5 border border-slate-700 cursor-pointer disabled:opacity-50"
            title="Download Excel"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Excel</span>
          </button>

          <button
            onClick={loadTrades}
            disabled={loading}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl transition cursor-pointer border border-slate-700"
            title="Refresh Trades"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
          </button>
        </div>
      </div>

      {/* Main Table */}
      <div className="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900 shadow-xl">
        <table className="w-full text-left text-xs font-mono">
          <thead className="bg-slate-950 text-slate-400 border-b border-slate-800">
            <tr>
              {[
                { key: "subsystem", label: "Engine" },
                { key: "symbol", label: "Symbol / ID" },
                { key: "venue", label: "Execution Venue" },
                { key: "side", label: "Side" },
                { key: "entry_price", label: "Entry Price" },
                { key: "exit_price", label: "Exit / Mark Price" },
                { key: "amount", label: "Amount" },
                { key: "margin_usd", label: "Margin" },
                { key: "pnl_usd", label: "PnL ($)" },
                { key: "pnl_pct", label: "PnL (%)" },
                { key: "status", label: "Status" },
                { key: "time", label: "Execution Time" }
              ].map((col) => (
                <th
                  key={col.key}
                  onClick={() => handleSort(col.key as SortField)}
                  className="p-3 cursor-pointer hover:bg-slate-900 transition group select-none whitespace-nowrap"
                >
                  <div className="flex items-center gap-1.5">
                    <span>{col.label}</span>
                    {renderSortIcon(col.key as SortField)}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/50 bg-slate-900/40">
            {filteredTrades.length > 0 ? (
              filteredTrades.map((t: any, idx: number) => {
                const isSpot = (t.subsystem || "SPOT") === "SPOT";
                const isArb = t.subsystem === "ARBITRAGE";
                const isShadow = t.subsystem === "SHADOW";
                const pnl = t.pnl_usd ?? 0;
                const isPositive = pnl > 0;
                const isZero = pnl === 0;

                return (
                  <tr key={t.id || idx} className="hover:bg-slate-800/30 transition">
                    
                    {/* Subsystem Badge */}
                    <td className="p-3">
                      {isSpot && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                          SPOT
                        </span>
                      )}
                      {isArb && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center gap-1 w-fit">
                          <Zap className="w-2.5 h-2.5" /> ARB
                        </span>
                      )}
                      {isShadow && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20 flex items-center gap-1 w-fit">
                          <Layers className="w-2.5 h-2.5" /> SHADOW
                        </span>
                      )}
                    </td>

                    {/* Symbol / ID */}
                    <td className="p-3">
                      <div className="font-bold text-white">{t.symbol}</div>
                      <div className="text-[10px] text-slate-500 truncate max-w-[120px]">{t.id}</div>
                    </td>

                    {/* Venue / Route */}
                    <td className="p-3 text-slate-300">
                      {isArb ? (
                        <span className="text-amber-300 font-bold text-[11px]">{t.venue}</span>
                      ) : isShadow ? (
                        <span className="text-purple-300 text-[11px]">{t.venue}</span>
                      ) : (
                        <span className="text-slate-300 text-[11px]">{t.venue || "BINANCE"}</span>
                      )}
                    </td>

                    {/* Side */}
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        t.side === "BUY" || t.side === "LONG"
                          ? "bg-emerald-500/20 text-emerald-400"
                          : t.side === "SHORT" || t.side === "SELL"
                          ? "bg-rose-500/20 text-rose-400"
                          : "bg-amber-500/20 text-amber-400"
                      }`}>
                        {t.side}
                      </span>
                    </td>

                    {/* Entry Price */}
                    <td className="p-3 text-slate-200">
                      {formatCryptoPrice(t.entry_price)}
                    </td>

                    {/* Exit / Mark Price */}
                    <td className="p-3 text-slate-200">
                      {t.exit_price ? formatCryptoPrice(t.exit_price) : "-"}
                    </td>

                    {/* Amount */}
                    <td className="p-3 text-slate-300">
                      {t.amount ? t.amount.toLocaleString(undefined, { maximumFractionDigits: 4 }) : "-"}
                    </td>

                    {/* Margin */}
                    <td className="p-3 text-slate-300">
                      ${(t.margin_usd || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                    </td>

                    {/* PnL ($) */}
                    <td className={`p-3 font-extrabold ${isZero ? "text-slate-400" : isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                      {isZero ? "$0.00" : `${isPositive ? "+" : ""}$${pnl.toFixed(2)}`}
                    </td>

                    {/* PnL (%) */}
                    <td className={`p-3 font-bold ${isZero ? "text-slate-400" : isPositive ? "text-emerald-400" : "text-rose-400"}`}>
                      {isZero ? "0.00%" : `${isPositive ? "+" : ""}${(t.pnl_pct || 0).toFixed(2)}%`}
                    </td>

                    {/* Status */}
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        t.status === "OPEN"
                          ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                          : t.status === "CAPTURED"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                          : t.status === "SIMULATED"
                          ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                          : "bg-slate-700/50 text-slate-300"
                      }`}>
                        {t.status || "CLOSED"}
                      </span>
                    </td>

                    {/* Execution Time */}
                    <td className="p-3 text-slate-400 whitespace-nowrap text-[11px]">
                      {t.time || "-"}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan={12} className="p-8 text-center text-slate-500">
                  No trade history found for current filter.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
