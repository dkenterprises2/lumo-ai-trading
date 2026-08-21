"use client";

import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchDiscoveredCoins, fetchPaperValidationTests, fetchResearchEvidence } from "@/services/api";
import { CoinResearchModal } from "./CoinResearchModal";
import { AutonomousSpotBotCard } from "./AutonomousSpotBotCard";
import {
  Sparkles,
  Flame,
  Zap,
  ShieldAlert,
  Eye,
  TestTube,
  FileText,
  RefreshCw,
  Search,
  Download,
  ExternalLink,
  TrendingUp,
  TrendingDown,
  Activity,
  Layers
} from "lucide-react";

export function NewAndMemeCoinResearchView() {
  const [activeTab, setActiveTab] = useState<"NEW" | "MEME" | "TOP_OPPORTUNITIES" | "HIGH_RISK" | "WATCHLIST" | "PAPER_TESTS" | "EVIDENCE">("TOP_OPPORTUNITIES");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCoin, setSelectedCoin] = useState<any>(null);
  const [watchlist, setWatchlist] = useState<string[]>(["PEPE/USDT", "FLOKI/USDT", "BONK/USDT"]);

  // Fetch Discovered Coins with 10s polling
  const coinsQuery = useQuery({
    queryKey: ["discovered-coins"],
    queryFn: () => fetchDiscoveredCoins(undefined, false),
    refetchInterval: 10000
  });

  // Fetch Paper Tests
  const paperTestsQuery = useQuery({
    queryKey: ["paper-tests"],
    queryFn: fetchPaperValidationTests,
    refetchInterval: 10000,
    enabled: activeTab === "PAPER_TESTS"
  });

  // Fetch Forensic Evidence
  const evidenceQuery = useQuery({
    queryKey: ["research-evidence"],
    queryFn: () => fetchResearchEvidence(50),
    refetchInterval: 15000,
    enabled: activeTab === "EVIDENCE"
  });

  const allCoins: any[] = coinsQuery.data?.coins || [];

  // Filter based on active tab & search query with defensive optional chaining
  const filteredCoins = allCoins.filter((item: any) => {
    if (!item || !item.coin) return false;
    const sym = (item.coin?.symbol || "").toLowerCase();
    const base = (item.coin?.base_asset || "").toLowerCase();
    const q = searchQuery.toLowerCase();
    const matchesSearch = !searchQuery || sym.includes(q) || base.includes(q);

    if (!matchesSearch) return false;

    if (activeTab === "NEW") return item.classification?.category === "NEW";
    if (activeTab === "MEME") return item.classification?.category === "MEME";
    if (activeTab === "HIGH_RISK") return item.risk_report?.overall_risk_level === "HIGH";
    if (activeTab === "TOP_OPPORTUNITIES") return (item.dossier?.opportunity_score ?? 0) >= 50.0;
    if (activeTab === "WATCHLIST") return watchlist.includes(item.coin?.symbol || "");

    return true;
  });

  const toggleWatchlist = (symbol: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!symbol) return;
    setWatchlist((prev) =>
      prev.includes(symbol) ? prev.filter((s) => s !== symbol) : [...prev, symbol]
    );
  };

  const handleExportCSV = () => {
    window.open("/api/spot/evidence/export/csv", "_blank");
  };

  const handleExportJSON = () => {
    window.open("/api/spot/evidence/export/json", "_blank");
  };

  const getRiskBadge = (level?: string) => {
    if (level === "HIGH") return "text-rose-400 bg-rose-500/10 border-rose-500/30";
    if (level === "MEDIUM") return "text-amber-400 bg-amber-500/10 border-amber-500/30";
    return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
  };

  const getRecBadge = (rec?: string) => {
    if (rec === "PAPER_TEST") return "bg-emerald-500/20 text-emerald-300 border-emerald-500/40";
    if (rec === "WATCH") return "bg-cyan-500/20 text-cyan-300 border-cyan-500/40";
    if (rec === "REJECT") return "bg-rose-500/20 text-rose-300 border-rose-500/40";
    return "bg-gray-500/20 text-gray-300 border-gray-500/40";
  };

  const topOppCount = allCoins.filter((c: any) => (c?.dossier?.opportunity_score ?? 0) >= 50).length;
  const newCoinsCount = allCoins.filter((c: any) => c?.classification?.category === "NEW").length;
  const memeCoinsCount = allCoins.filter((c: any) => c?.classification?.category === "MEME").length;
  const highRiskCount = allCoins.filter((c: any) => c?.risk_report?.overall_risk_level === "HIGH").length;

  return (
    <div className="space-y-6">
      
      {/* Autonomous Bot & Sub-Wallet Control Panel */}
      <AutonomousSpotBotCard />

      {/* Top Banner / Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none" />
        
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 relative z-10">
          <div>
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <Sparkles className="w-5 h-5" />
              </div>
              <h1 className="text-2xl font-bold text-white tracking-tight">New &amp; Meme Coin Discovery &amp; Research</h1>
            </div>
            <p className="text-xs text-slate-400 mt-1.5 max-w-2xl leading-relaxed">
              Autonomous real-time token discovery across Binance CEX &amp; Solana/Base DEX streams. Quantitative 8-vector risk scoring, multi-factor AI research, and gated paper validation.
            </p>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => coinsQuery.refetch()}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition border border-slate-700 flex items-center gap-2 text-xs font-semibold shadow-sm"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${coinsQuery.isFetching ? "animate-spin text-indigo-400" : ""}`} /> Refresh Live Feeds
            </button>
            <button
              onClick={handleExportCSV}
              className="p-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition border border-slate-700 flex items-center gap-2 text-xs font-semibold shadow-sm"
            >
              <Download className="w-3.5 h-3.5 text-cyan-400" /> Export CSV
            </button>
          </div>
        </div>

        {/* 7 Section Navigation Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pt-6 border-t border-slate-800/80 mt-6 scrollbar-none">
          {[
            { id: "TOP_OPPORTUNITIES", label: "Top Opportunities", icon: Zap, count: topOppCount },
            { id: "NEW", label: "New Coins", icon: Sparkles, count: newCoinsCount },
            { id: "MEME", label: "Meme Coins", icon: Flame, count: memeCoinsCount },
            { id: "HIGH_RISK", label: "High Risk", icon: ShieldAlert, count: highRiskCount },
            { id: "WATCHLIST", label: "Watchlist", icon: Eye, count: watchlist.length },
            { id: "PAPER_TESTS", label: "Paper Tests", icon: TestTube, count: paperTestsQuery.data?.active_count ?? 0 },
            { id: "EVIDENCE", label: "Forensic Evidence", icon: FileText, count: evidenceQuery.data?.total ?? 0 }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`px-4 py-2 rounded-xl text-xs font-semibold flex items-center gap-2 whitespace-nowrap transition-all border ${
                  isActive
                    ? "bg-indigo-600 text-white border-indigo-500 shadow-lg shadow-indigo-600/20"
                    : "bg-slate-950/60 text-slate-400 hover:text-slate-200 border-slate-800 hover:border-slate-700"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                {tab.label}
                <span className={`px-1.5 py-0.2 rounded-md text-[10px] font-bold ${isActive ? "bg-indigo-700 text-white" : "bg-slate-800 text-slate-400"}`}>
                  {tab.count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Search & Filter Bar (for Coin Grid views) */}
      {activeTab !== "PAPER_TESTS" && activeTab !== "EVIDENCE" && (
        <div className="flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by coin symbol or base asset..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 transition shadow-inner"
            />
          </div>
          <div className="text-xs text-slate-400 font-medium">
            Showing <span className="text-white font-bold">{filteredCoins.length}</span> of <span className="text-slate-200">{allCoins.length}</span> discovered tokens
          </div>
        </div>
      )}

      {/* Main Content Area */}
      {activeTab === "PAPER_TESTS" ? (
        /* Paper Validation Blotter */
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <TestTube className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-bold text-white">Active &amp; Completed Paper Validation Tests</h2>
            </div>
            <div className="text-xs text-slate-400">
              Active: <span className="text-emerald-400 font-bold">{paperTestsQuery.data?.active_count ?? 0}</span> | Closed: <span className="text-slate-300 font-bold">{paperTestsQuery.data?.closed_count ?? 0}</span>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Trade ID</th>
                  <th className="p-3.5">Symbol</th>
                  <th className="p-3.5">Status</th>
                  <th className="p-3.5">Side</th>
                  <th className="p-3.5">Entry Price</th>
                  <th className="p-3.5">Current / Exit</th>
                  <th className="p-3.5">Size (USDT)</th>
                  <th className="p-3.5">Sim. Slippage / Fee</th>
                  <th className="p-3.5">Unrealized / Realized PnL</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(paperTestsQuery.data?.trades ?? []).length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-slate-500 font-medium">
                      No paper validation tests executed yet. Click on any approved coin to start a test.
                    </td>
                  </tr>
                ) : (
                  (paperTestsQuery.data?.trades ?? []).map((tr: any) => (
                    <tr key={tr.trade_id} className="hover:bg-slate-800/40 transition">
                      <td className="p-3.5 font-mono text-indigo-400 font-medium">{tr.trade_id}</td>
                      <td className="p-3.5 font-bold text-white">{tr.symbol}</td>
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${tr.status === "ACTIVE" ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30" : "bg-slate-800 text-slate-400"}`}>
                          {tr.status}
                        </span>
                      </td>
                      <td className="p-3.5 font-semibold text-emerald-400">{tr.side}</td>
                      <td className="p-3.5 font-mono">${Number(tr.entry_price).toFixed(6)}</td>
                      <td className="p-3.5 font-mono">${Number(tr.current_price || tr.exit_price || tr.entry_price).toFixed(6)}</td>
                      <td className="p-3.5 font-mono">${Number(tr.allocation_usd).toFixed(2)}</td>
                      <td className="p-3.5 font-mono text-slate-400">${Number(tr.slippage_usd + tr.fees_usd).toFixed(3)}</td>
                      <td className="p-3.5 font-mono font-bold">
                        {tr.status === "ACTIVE" ? (
                          <span className={tr.unrealized_pnl_usd >= 0 ? "text-emerald-400" : "text-rose-400"}>
                            {tr.unrealized_pnl_usd >= 0 ? "+" : ""}${Number(tr.unrealized_pnl_usd).toFixed(2)} ({Number(tr.unrealized_pnl_pct).toFixed(2)}%)
                          </span>
                        ) : (
                          <span className={tr.realized_pnl_usd >= 0 ? "text-emerald-400" : "text-rose-400"}>
                            {tr.realized_pnl_usd >= 0 ? "+" : ""}${Number(tr.realized_pnl_usd).toFixed(2)}
                          </span>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : activeTab === "EVIDENCE" ? (
        /* Forensic Evidence Log Table */
        <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              <h2 className="text-sm font-bold text-white">Immutable Forensic Research Ledger</h2>
            </div>
            <div className="flex gap-2">
              <button onClick={handleExportCSV} className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-cyan-400 transition flex items-center gap-1.5 border border-slate-700">
                <Download className="w-3 h-3" /> CSV
              </button>
              <button onClick={handleExportJSON} className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-indigo-400 transition flex items-center gap-1.5 border border-slate-700">
                <Download className="w-3 h-3" /> JSON
              </button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-950/60 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3.5">Event ID</th>
                  <th className="p-3.5">Symbol</th>
                  <th className="p-3.5">Venue</th>
                  <th className="p-3.5">Category</th>
                  <th className="p-3.5">Price</th>
                  <th className="p-3.5">Opportunity</th>
                  <th className="p-3.5">Risk Score</th>
                  <th className="p-3.5">Decision</th>
                  <th className="p-3.5">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {(evidenceQuery.data?.events ?? []).length === 0 ? (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-slate-500 font-medium">
                      No forensic evidence records found in SQLite ledger.
                    </td>
                  </tr>
                ) : (
                  (evidenceQuery.data?.events ?? []).map((ev: any) => (
                    <tr key={ev.event_id} className="hover:bg-slate-800/40 transition">
                      <td className="p-3.5 font-mono text-slate-400 text-[11px]">{ev.event_id}</td>
                      <td className="p-3.5 font-bold text-white">{ev.symbol}</td>
                      <td className="p-3.5 text-slate-400">{ev.exchange}</td>
                      <td className="p-3.5 font-semibold text-slate-300">{ev.category}</td>
                      <td className="p-3.5 font-mono">${Number(ev.price_usd).toFixed(4)}</td>
                      <td className="p-3.5 font-mono text-cyan-400 font-bold">{ev.opportunity_score}/100</td>
                      <td className="p-3.5 font-mono text-amber-400 font-bold">{ev.risk_score}/100</td>
                      <td className="p-3.5">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRecBadge(ev.recommendation)}`}>
                          {ev.recommendation}
                        </span>
                      </td>
                      <td className="p-3.5 font-mono text-slate-400">{new Date(ev.timestamp * 1000).toLocaleTimeString()}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        /* Coin Cards Grid */
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {coinsQuery.isLoading ? (
            Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-56 rounded-2xl bg-slate-900/60 border border-slate-800 animate-pulse" />
            ))
          ) : filteredCoins.length === 0 ? (
            <div className="col-span-full py-16 text-center">
              <div className="p-4 rounded-full bg-slate-900 border border-slate-800 text-slate-500 w-16 h-16 mx-auto flex items-center justify-center mb-3">
                <Search className="w-8 h-8" />
              </div>
              <h3 className="text-base font-bold text-slate-300">No coins matching filters</h3>
              <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">Try clearing search filters or refreshing live market streams.</p>
            </div>
          ) : (
            filteredCoins.map((item: any) => {
              const { coin, classification, risk_report, dossier } = item;
              const isWatchlisted = watchlist.includes(coin?.symbol || "");
              const isPositiveChange = (coin?.price_change_24h_pct ?? 0) >= 0;

              return (
                <div
                  key={coin?.symbol}
                  onClick={() => setSelectedCoin(item)}
                  className="bg-slate-900/90 border border-slate-800 hover:border-indigo-500/50 rounded-2xl p-5 transition-all shadow-xl hover:shadow-indigo-500/10 cursor-pointer flex flex-col justify-between group relative overflow-hidden"
                >
                  <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/5 rounded-full blur-2xl group-hover:bg-indigo-500/10 transition pointer-events-none" />

                  {/* Header Row */}
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div className="p-2 rounded-xl bg-slate-800 border border-slate-700 group-hover:border-indigo-500/40 transition text-slate-200">
                          {classification?.category === "MEME" ? (
                            <Flame className="w-4 h-4 text-amber-400" />
                          ) : classification?.category === "NEW" ? (
                            <Sparkles className="w-4 h-4 text-cyan-400" />
                          ) : (
                            <Activity className="w-4 h-4 text-indigo-400" />
                          )}
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-base font-extrabold text-white group-hover:text-cyan-400 transition">{coin?.symbol}</h3>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRecBadge(dossier?.recommendation)}`}>
                              {dossier?.recommendation}
                            </span>
                          </div>
                          <span className="text-[11px] text-slate-400 font-mono">{coin?.exchange}</span>
                        </div>
                      </div>

                      <button
                        onClick={(e) => toggleWatchlist(coin?.symbol, e)}
                        className={`p-2 rounded-lg border transition ${
                          isWatchlisted
                            ? "bg-amber-500/20 text-amber-400 border-amber-500/40"
                            : "bg-slate-800/60 text-slate-500 hover:text-slate-300 border-slate-700/60"
                        }`}
                        title={isWatchlisted ? "Remove from Watchlist" : "Add to Watchlist"}
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    {/* Price & Metrics Row */}
                    <div className="mt-4 flex items-baseline justify-between">
                      <div className="text-xl font-extrabold text-white font-mono">
                        ${coin?.current_price !== null && coin?.current_price !== undefined ? (coin.current_price < 0.01 ? coin.current_price.toFixed(6) : coin.current_price.toFixed(2)) : "N/A"}
                      </div>
                      <div className={`flex items-center gap-1 text-xs font-bold font-mono ${isPositiveChange ? "text-emerald-400" : "text-rose-400"}`}>
                        {isPositiveChange ? <TrendingUp className="w-3.5 h-3.5" /> : <TrendingDown className="w-3.5 h-3.5" />}
                        {isPositiveChange ? "+" : ""}{coin?.price_change_24h_pct?.toFixed(2) ?? "0.00"}%
                      </div>
                    </div>

                    {/* 2-Column Key Metrics */}
                    <div className="grid grid-cols-2 gap-2 mt-4 text-[11px] font-medium bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80">
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">24h Volume</span>
                        <span className="text-slate-200 font-mono font-bold">
                          {coin?.volume_24h_usd ? `$${(coin.volume_24h_usd / 1e6).toFixed(2)}M` : "N/A"}
                        </span>
                      </div>
                      <div>
                        <span className="text-slate-500 block text-[10px] uppercase font-semibold">Liquidity Depth</span>
                        <span className="text-slate-200 font-mono font-bold">
                          {coin?.liquidity_usd ? `$${(coin.liquidity_usd / 1e3).toFixed(1)}k` : "N/A (CEX)"}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Footer Scores & Decision */}
                  <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                    <div className="flex items-center gap-2 text-[11px]">
                      <span className="text-slate-500 font-medium">Opp Score:</span>
                      <span className="font-mono font-bold text-cyan-400">{dossier?.opportunity_score ?? 0}/100</span>
                    </div>

                    <div className="flex items-center gap-1.5 text-[11px]">
                      <span className="text-slate-500 font-medium">Risk:</span>
                      <span className={`px-2 py-0.5 rounded font-bold border ${getRiskBadge(risk_report?.overall_risk_level)} text-[10px]`}>
                        {risk_report?.overall_risk_level || "UNKNOWN"} ({risk_report?.overall_risk_score ?? 0})
                      </span>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Deep Inspection Research Modal */}
      {selectedCoin && (
        <CoinResearchModal
          coinData={selectedCoin}
          onClose={() => setSelectedCoin(null)}
          onRefresh={async (sym) => {
            await coinsQuery.refetch();
          }}
        />
      )}

    </div>
  );
}
