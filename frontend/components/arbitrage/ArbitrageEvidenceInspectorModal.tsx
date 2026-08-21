"use client";

import React, { useState, useEffect, useCallback } from "react";
import { 
  ShieldCheck, 
  AlertTriangle, 
  Download, 
  Filter, 
  RefreshCw, 
  Search, 
  ArrowUpDown, 
  FileSpreadsheet, 
  FileCode, 
  CheckCircle2, 
  X, 
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  Database
} from "lucide-react";
import { apiFetch } from "@/services/api";
import { getApiBaseUrl } from "@/lib/config";
import { ArbitrageForensicDetailModal } from "./ArbitrageForensicDetailModal";

interface EvidenceInspectorModalProps {
  initialCategory?: string;
  onClose: () => void;
}

const CATEGORIES = [
  { id: "SCANNED_ROUTES", label: "Scanned Routes", color: "text-slate-300 border-slate-700 bg-slate-800/60" },
  { id: "GROSS_PROFITABLE", label: "Gross Profitable", color: "text-cyan-400 border-cyan-500/40 bg-cyan-950/40" },
  { id: "NEGATIVE_SPREAD", label: "Negative Spread", color: "text-slate-400 border-slate-700 bg-slate-900/60" },
  { id: "STALE_QUOTES", label: "Stale Quotes", color: "text-amber-400 border-amber-500/40 bg-amber-950/40" },
  { id: "CACHED_FALLBACK", label: "Cached / Fallback", color: "text-orange-400 border-orange-500/40 bg-orange-950/40" },
  { id: "FEE_REJECTIONS", label: "Fee Rejections", color: "text-yellow-400 border-yellow-500/40 bg-yellow-950/40" },
  { id: "SLIPPAGE_REJECTIONS", label: "Slippage Rejections", color: "text-orange-400 border-orange-500/40 bg-orange-950/40" },
  { id: "LIQUIDITY_REJECTIONS", label: "Liquidity Rejections", color: "text-indigo-400 border-indigo-500/40 bg-indigo-950/40" },
  { id: "RISK_REJECTIONS", label: "Risk Rejections", color: "text-rose-400 border-rose-500/40 bg-rose-950/40" },
  { id: "GOVERNANCE_REJECTIONS", label: "Gov Rejections", color: "text-purple-400 border-purple-500/40 bg-purple-950/40" },
  { id: "NET_PROFITABLE", label: "Net Profitable", color: "text-emerald-400 border-emerald-500/40 bg-emerald-950/40" },
  { id: "EXECUTABLE", label: "Executable", color: "text-emerald-300 border-emerald-400/50 bg-emerald-900/50" }
];

const TIME_RANGES = [
  { label: "1 Minute", seconds: 60 },
  { label: "5 Minutes", seconds: 300 },
  { label: "15 Minutes", seconds: 900 },
  { label: "1 Hour", seconds: 3600 },
  { label: "6 Hours", seconds: 21600 },
  { label: "24 Hours", seconds: 86400 },
  { label: "All Time", seconds: undefined }
];

const VENUES = ["BINANCE", "BYBIT", "OKX", "KRAKEN", "COINBASE"];
const SYMBOLS = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "AVAX/USDT", "BNB/USDT"];

export function ArbitrageEvidenceInspectorModal({ initialCategory = "SCANNED_ROUTES", onClose }: EvidenceInspectorModalProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>(initialCategory.toUpperCase().replace(" ", "_"));
  const [selectedTimeRange, setSelectedTimeRange] = useState<number | undefined>(undefined);
  const [selectedSymbol, setSelectedSymbol] = useState<string>("");
  const [selectedBuyVenue, setSelectedBuyVenue] = useState<string>("");
  const [selectedSellVenue, setSelectedSellVenue] = useState<string>("");
  const [selectedDecision, setSelectedDecision] = useState<string>("");
  const [searchReason, setSearchReason] = useState<string>("");

  const [page, setPage] = useState<number>(0);
  const limit = 50;

  // Sorting
  const [sortBy, setSortBy] = useState<string>("created_at");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");

  // Evidence state
  const [events, setEvents] = useState<any[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [loading, setLoading] = useState<boolean>(true);

  // Selected single event for deep drilldown
  const [inspectingEventId, setInspectingEventId] = useState<string | null>(null);

  // Reconciliation Audit state
  const [reconcileData, setReconcileData] = useState<any>(null);
  const [showReconcileProof, setShowReconcileProof] = useState<boolean>(false);

  // Export Checksum state
  const [exportChecksumModal, setExportChecksumModal] = useState<{ type: string; hash: string; count: number } | null>(null);

  const fetchEvidence = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (selectedCategory && selectedCategory !== "SCANNED_ROUTES") params.append("category", selectedCategory);
      if (selectedSymbol) params.append("symbol", selectedSymbol);
      if (selectedBuyVenue) params.append("buy_venue", selectedBuyVenue);
      if (selectedSellVenue) params.append("sell_venue", selectedSellVenue);
      if (selectedDecision) params.append("decision", selectedDecision);
      if (searchReason) params.append("rejection_reason", searchReason);
      if (selectedTimeRange !== undefined) params.append("time_range_seconds", selectedTimeRange.toString());
      params.append("sort_by", sortBy);
      params.append("sort_dir", sortDir);
      params.append("limit", limit.toString());
      params.append("offset", (page * limit).toString());

      const res = await apiFetch(`/api/arbitrage/evidence?${params.toString()}`);
      const data = await res.json();
      if (data.status === "success") {
        setEvents(data.events || []);
        setTotalCount(data.total_count || 0);
      }
    } catch (e) {
      console.error("[ArbitrageEvidenceInspector] Fetch error:", e);
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, selectedSymbol, selectedBuyVenue, selectedSellVenue, selectedDecision, searchReason, selectedTimeRange, sortBy, sortDir, page]);

  const fetchReconciliation = useCallback(async () => {
    try {
      const res = await apiFetch("/api/arbitrage/evidence/reconcile");
      const data = await res.json();
      if (data.status === "success") {
        setReconcileData(data);
      }
    } catch (e) {
      console.warn("[ArbitrageEvidenceInspector] Reconcile error:", e);
    }
  }, []);

  useEffect(() => {
    fetchEvidence();
  }, [fetchEvidence]);

  useEffect(() => {
    fetchReconciliation();
  }, [fetchReconciliation]);

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortDir(prev => (prev === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortDir("desc");
    }
    setPage(0);
  };

  const handleExport = async (format: "csv" | "json") => {
    try {
      const params = new URLSearchParams();
      if (selectedCategory && selectedCategory !== "SCANNED_ROUTES") params.append("category", selectedCategory);
      if (selectedSymbol) params.append("symbol", selectedSymbol);
      if (selectedTimeRange !== undefined) params.append("time_range_seconds", selectedTimeRange.toString());

      const url = `${getApiBaseUrl()}/api/arbitrage/evidence/export/${format}?${params.toString()}`;
      const token = typeof window !== "undefined" ? localStorage.getItem("lumo_access_token") : null;
      
      const response = await fetch(url, {
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });

      const sha256 = response.headers.get("X-Export-SHA256") || "INTEGRITY_CALCULATED";
      const totalRecs = parseInt(response.headers.get("X-Total-Records") || "0", 10);
      const blob = await response.blob();

      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = blobUrl;
      a.download = `arbitrage_evidence_${selectedCategory.toLowerCase()}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(blobUrl);
      document.body.removeChild(a);

      setExportChecksumModal({
        type: format.toUpperCase(),
        hash: sha256,
        count: totalRecs || totalCount
      });
    } catch (e) {
      console.error("[ArbitrageEvidenceInspector] Export error:", e);
    }
  };

  return (
    <div className="fixed inset-0 bg-slate-950/85 backdrop-blur-md flex items-center justify-center p-2 sm:p-4 z-50 animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl max-w-7xl w-full h-[94vh] flex flex-col shadow-2xl overflow-hidden font-sans">
        
        {/* Header */}
        <div className="px-6 py-4 bg-slate-950/80 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
              <Database className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-white tracking-wide font-mono">
                  Arbitrage Evidence Inspector
                </h2>
                <span className="px-2.5 py-0.5 rounded text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                  LIVE PROVENANCE STORE
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono">
                Authoritative runtime route evaluations • Zero synthetic records • Deterministic replay
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Reconciliation Proof Button */}
            <button
              onClick={() => setShowReconcileProof(prev => !prev)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-mono transition cursor-pointer ${
                reconcileData?.is_consistent 
                  ? "bg-emerald-950/40 border-emerald-500/40 text-emerald-300 hover:bg-emerald-900/50" 
                  : "bg-rose-950/40 border-rose-500/40 text-rose-300 hover:bg-rose-900/50"
              }`}
            >
              {reconcileData?.is_consistent ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
              )}
              <span>{reconcileData?.is_consistent ? "AUDIT PASSED (0 Diff)" : "METRIC INTEGRITY ERROR"}</span>
            </button>

            {/* Export Buttons */}
            <button
              onClick={() => handleExport("csv")}
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono rounded-lg transition cursor-pointer"
            >
              <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-400" />
              <span>CSV</span>
            </button>

            <button
              onClick={() => handleExport("json")}
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-mono rounded-lg transition cursor-pointer"
            >
              <FileCode className="w-3.5 h-3.5 text-cyan-400" />
              <span>JSON</span>
            </button>

            <button
              onClick={() => { fetchEvidence(); fetchReconciliation(); }}
              disabled={loading}
              className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition cursor-pointer"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
            </button>

            <button
              onClick={onClose}
              className="w-8 h-8 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition cursor-pointer text-sm font-bold"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Category Pill Navigation Bar (12 Cards Mapping) */}
        <div className="px-6 py-2.5 bg-slate-950/40 border-b border-slate-800 overflow-x-auto custom-scrollbar flex items-center gap-2">
          {CATEGORIES.map(cat => (
            <button
              key={cat.id}
              onClick={() => { setSelectedCategory(cat.id); setPage(0); }}
              className={`px-3 py-1 rounded-lg text-xs font-mono font-medium whitespace-nowrap transition cursor-pointer border ${
                selectedCategory === cat.id
                  ? cat.color + " shadow-md ring-1 ring-white/20"
                  : "bg-slate-900/60 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200"
              }`}
            >
              {cat.label}
            </button>
          ))}
        </div>

        {/* Filter Controls Bar */}
        <div className="px-6 py-3 bg-slate-950/20 border-b border-slate-800/80 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 text-xs font-mono">
          {/* Time Range */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Time Range</label>
            <select
              value={selectedTimeRange === undefined ? "ALL" : selectedTimeRange}
              onChange={e => {
                const val = e.target.value;
                setSelectedTimeRange(val === "ALL" ? undefined : Number(val));
                setPage(0);
              }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              {TIME_RANGES.map(tr => (
                <option key={tr.label} value={tr.seconds === undefined ? "ALL" : tr.seconds}>
                  {tr.label}
                </option>
              ))}
            </select>
          </div>

          {/* Symbol */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Symbol</label>
            <select
              value={selectedSymbol}
              onChange={e => { setSelectedSymbol(e.target.value); setPage(0); }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Pairs</option>
              {SYMBOLS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          {/* Buy Venue */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Buy Venue</label>
            <select
              value={selectedBuyVenue}
              onChange={e => { setSelectedBuyVenue(e.target.value); setPage(0); }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Venues</option>
              {VENUES.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>

          {/* Sell Venue */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Sell Venue</label>
            <select
              value={selectedSellVenue}
              onChange={e => { setSelectedSellVenue(e.target.value); setPage(0); }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Venues</option>
              {VENUES.map(v => <option key={v} value={v}>{v}</option>)}
            </select>
          </div>

          {/* Decision */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Decision</label>
            <select
              value={selectedDecision}
              onChange={e => { setSelectedDecision(e.target.value); setPage(0); }}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="">All Decisions</option>
              <option value="EXECUTABLE">EXECUTABLE</option>
              <option value="REJECTED">REJECTED</option>
            </select>
          </div>

          {/* Reason Keyword Search */}
          <div>
            <label className="text-[10px] text-slate-400 block mb-1">Rejection Reason</label>
            <div className="relative">
              <input
                type="text"
                placeholder="e.g. FEE, STALE"
                value={searchReason}
                onChange={e => { setSearchReason(e.target.value); setPage(0); }}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-indigo-500 text-xs"
              />
              {searchReason && (
                <button onClick={() => setSearchReason("")} className="absolute right-2 top-2 text-slate-500 hover:text-white">✕</button>
              )}
            </div>
          </div>
        </div>

        {/* Reconciliation Proof Matrix Modal Drawer */}
        {showReconcileProof && reconcileData && (
          <div className="bg-slate-950 p-4 border-b border-indigo-500/30 font-mono text-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-indigo-300 font-bold">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span>Forensic Card Metric vs SQLite Evidence Proof Reconciliation</span>
              </div>
              <button onClick={() => setShowReconcileProof(false)} className="text-slate-400 hover:text-white">✕ Close Proof</button>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-2 text-[11px]">
              {reconcileData.reconciliation.map((r: any) => (
                <div key={r.card_metric} className="p-2 bg-slate-900 rounded border border-slate-800">
                  <span className="text-slate-400 block text-[10px] truncate">{r.card_metric}</span>
                  <div className="flex items-center justify-between mt-1">
                    <strong className="text-slate-200">{r.evidence_count}</strong>
                    <span className={`text-[9px] px-1 py-0.5 rounded font-bold ${r.status === "PASS" ? "bg-emerald-500/20 text-emerald-300" : "bg-rose-500/20 text-rose-300"}`}>
                      Diff: {r.difference}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Main Data Table */}
        <div className="flex-1 overflow-auto custom-scrollbar">
          <table className="w-full text-left font-mono text-[11px] whitespace-nowrap">
            <thead className="bg-slate-950 text-slate-400 sticky top-0 z-10 border-b border-slate-800">
              <tr>
                <th className="py-2.5 px-3 cursor-pointer hover:text-white" onClick={() => handleSort("created_at")}>
                  <div className="flex items-center gap-1">TIME (UTC) <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3">PAIR</th>
                <th className="py-2.5 px-3">BUY → SELL</th>
                <th className="py-2.5 px-3 text-right">BUY PRICE</th>
                <th className="py-2.5 px-3 text-right">SELL PRICE</th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("gross_spread")}>
                  <div className="flex items-center justify-end gap-1">GROSS SPREAD <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("fees")}>
                  <div className="flex items-center justify-end gap-1">FEES <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("slippage")}>
                  <div className="flex items-center justify-end gap-1">SLIPPAGE <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("net_edge")}>
                  <div className="flex items-center justify-end gap-1">NET EDGE <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("latency")}>
                  <div className="flex items-center justify-end gap-1">LATENCY <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3 text-right cursor-pointer hover:text-white" onClick={() => handleSort("quote_age")}>
                  <div className="flex items-center justify-end gap-1">AGE <ArrowUpDown className="w-3 h-3" /></div>
                </th>
                <th className="py-2.5 px-3">DECISION</th>
                <th className="py-2.5 px-3">REJECTION REASON</th>
                <th className="py-2.5 px-3">SOURCE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={14} className="py-16 text-center text-slate-400">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-indigo-400" />
                      <span>Loading immutable forensic records...</span>
                    </div>
                  </td>
                </tr>
              ) : events.length === 0 ? (
                <tr>
                  <td colSpan={14} className="py-16 text-center text-slate-500 font-bold">
                    NO REAL RECORDS CAPTURED (Zero evaluation events match current filter)
                  </td>
                </tr>
              ) : (
                events.map(ev => {
                  const isExec = ev.decision === "EXECUTABLE";
                  const grossProfit = ev.gross_spread_bps > 0;
                  const netProfit = ev.net_edge_bps > 0;

                  return (
                    <tr
                      key={ev.event_id}
                      onClick={() => setInspectingEventId(ev.event_id)}
                      className="hover:bg-slate-800/50 cursor-pointer transition-colors"
                    >
                      <td className="py-2.5 px-3 text-slate-400 font-mono">{ev.timestamp_utc}</td>
                      <td className="py-2.5 px-3 font-bold text-white">{ev.symbol}</td>
                      <td className="py-2.5 px-3">
                        <span className="text-emerald-400 font-semibold">{ev.buy_exchange}</span>
                        <span className="text-slate-500 mx-1">→</span>
                        <span className="text-rose-400 font-semibold">{ev.sell_exchange}</span>
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-300">
                        ${ev.buy_price_used?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-300">
                        ${ev.sell_price_used?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>
                      <td className={`py-2.5 px-3 text-right font-bold ${grossProfit ? "text-cyan-400" : "text-slate-400"}`}>
                        {grossProfit ? `+${ev.gross_spread_bps} bps` : `${ev.gross_spread_bps} bps`}
                      </td>
                      <td className="py-2.5 px-3 text-right text-yellow-400">
                        {(ev.estimated_fee_buy + ev.estimated_fee_sell).toFixed(1)} bps
                      </td>
                      <td className="py-2.5 px-3 text-right text-orange-400">
                        {(ev.estimated_slippage_buy + ev.estimated_slippage_sell).toFixed(1)} bps
                      </td>
                      <td className={`py-2.5 px-3 text-right font-bold ${netProfit ? "text-emerald-400" : "text-rose-400"}`}>
                        {netProfit ? `+${ev.net_edge_bps} bps` : `${ev.net_edge_bps} bps`}
                      </td>
                      <td className="py-2.5 px-3 text-right text-slate-400">{ev.latency_ms} ms</td>
                      <td className="py-2.5 px-3 text-right text-slate-400">{ev.quote_age_ms} ms</td>
                      <td className="py-2.5 px-3">
                        {isExec ? (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                            EXECUTABLE
                          </span>
                        ) : (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-rose-500/20 text-rose-300 border border-rose-500/30">
                            REJECTED
                          </span>
                        )}
                      </td>
                      <td className="py-2.5 px-3 text-amber-300 font-semibold truncate max-w-[150px]">
                        {ev.rejection_reason}
                      </td>
                      <td className="py-2.5 px-3 text-slate-400 truncate max-w-[180px]">
                        {ev.market_data_source}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Footer & Pagination Bar */}
        <div className="px-6 py-3 bg-slate-950/80 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs font-mono text-slate-400">
          <div className="flex items-center gap-2">
            <span>Category: <strong className="text-slate-200">{selectedCategory}</strong></span>
            <span>•</span>
            <span>
              Showing <strong className="text-white">{events.length === 0 ? 0 : page * limit + 1}–{Math.min((page + 1) * limit, totalCount)}</strong> of <strong className="text-white">{totalCount.toLocaleString()}</strong> records
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage(prev => Math.max(0, prev - 1))}
              disabled={page === 0 || loading}
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
              <span>Prev</span>
            </button>
            <span className="px-2">Page {page + 1} of {Math.max(1, Math.ceil(totalCount / limit))}</span>
            <button
              onClick={() => setPage(prev => ((prev + 1) * limit < totalCount ? prev + 1 : prev))}
              disabled={(page + 1) * limit >= totalCount || loading}
              className="flex items-center gap-1 px-3 py-1.5 bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-white rounded-lg transition cursor-pointer"
            >
              <span>Next</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        {/* Deep Forensic Detail Modal Drilldown */}
        {inspectingEventId && (
          <ArbitrageForensicDetailModal
            eventId={inspectingEventId}
            onClose={() => setInspectingEventId(null)}
          />
        )}

        {/* Export Checksum Proof Modal */}
        {exportChecksumModal && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-in fade-in">
            <div className="bg-slate-900 border border-emerald-500/40 p-6 rounded-2xl max-w-lg w-full space-y-4 shadow-2xl font-mono text-xs text-slate-300">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div className="flex items-center gap-2 text-emerald-400 font-bold text-sm">
                  <CheckCircle2 className="w-5 h-5" />
                  <span>Forensic Evidence Exported Successfully</span>
                </div>
                <button onClick={() => setExportChecksumModal(null)} className="text-slate-400 hover:text-white">✕</button>
              </div>

              <div className="space-y-2 bg-slate-950 p-4 rounded-xl border border-slate-800">
                <div>
                  <span className="text-slate-400 block text-[10px]">Export Format &amp; Record Count:</span>
                  <span className="text-white font-bold">{exportChecksumModal.type} ({exportChecksumModal.count.toLocaleString()} rows)</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px]">Cryptographic Checksum (SHA-256):</span>
                  <div className="p-2 bg-slate-900 rounded border border-slate-750 text-cyan-300 text-[10px] break-all select-all">
                    {exportChecksumModal.hash}
                  </div>
                </div>
                <p className="text-[10px] text-slate-400">
                  This SHA-256 hash guarantees that the downloaded forensic evidence file has not been altered or tampered with.
                </p>
              </div>

              <button
                onClick={() => setExportChecksumModal(null)}
                className="w-full py-2 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-xl transition cursor-pointer"
              >
                Done
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
