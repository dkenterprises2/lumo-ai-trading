"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery, useMutation } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { Crosshair, Search, FileText, CheckCircle2, AlertTriangle, RefreshCw, Layers } from "lucide-react";

export default function TradeInvestigationsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [selectedTradeId, setSelectedTradeId] = useState<string>("");
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const recentTradesQuery = useQuery({
    queryKey: ["rca-recent-trades"],
    queryFn: async () => {
      const res = await apiFetch("/api/investigation/recent-trades");
      if (!res.ok) throw new Error("Failed to fetch recent trades for RCA");
      return res.json();
    },
    refetchInterval: 5000
  });

  const rcaMutation = useMutation({
    mutationFn: async (tradeId: string) => {
      const res = await apiFetch(`/api/investigation/trades/${tradeId}`, { method: "POST" });
      if (!res.ok) throw new Error("RCA analysis failed");
      return res.json();
    }
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const recentTrades = recentTradesQuery.data ?? [];
  const rcaReport = rcaMutation.data ?? null;

  const handleAnalyze = (tradeId: string) => {
    setSelectedTradeId(tradeId);
    rcaMutation.mutate(tradeId);
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <Crosshair className="w-7 h-7 text-purple-400" />
                Trade Root Cause Analysis (RCA)
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Automated evidence reconstruction across Signal $\rightarrow$ Strategy $\rightarrow$ Risk Gate $\rightarrow$ Execution $\rightarrow$ Fill &amp; PnL.
              </p>
            </div>
            <button
              onClick={() => recentTradesQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${recentTradesQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Trade Log</span>
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Recent Completed Trades Selector */}
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4">
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                <Layers className="w-4 h-4 text-purple-400" />
                Select Trade for RCA ({recentTrades.length})
              </h2>

              {recentTrades.length === 0 ? (
                <div className="p-6 text-center text-slate-500 text-xs font-mono">
                  INSUFFICIENT EVIDENCE FOR RCA (No completed trades found)
                </div>
              ) : (
                <div className="space-y-2 max-h-[450px] overflow-y-auto pr-1">
                  {recentTrades.map((t: any) => (
                    <button
                      key={t.trade_id}
                      onClick={() => handleAnalyze(t.trade_id)}
                      className={`w-full p-3 rounded-xl border text-left transition-all cursor-pointer ${
                        selectedTradeId === t.trade_id
                          ? "bg-purple-950/40 border-purple-500/80 text-white"
                          : "bg-slate-950 hover:bg-slate-900 border-slate-800 text-slate-300"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs text-purple-300">{t.symbol}</span>
                        <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          t.realized_pnl >= 0 ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                        }`}>
                          ${t.realized_pnl?.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1 text-[11px] text-slate-400 font-mono">
                        <span>{t.side}</span>
                        <span>{t.exit_reason}</span>
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* RCA Audit Evidence Display */}
            <div className="lg:col-span-2 bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-5">
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                <FileText className="w-5 h-5 text-purple-400" />
                Root Cause Analysis Evidence Timeline
              </h2>

              {!rcaReport ? (
                <div className="p-12 text-center text-slate-500 text-xs font-mono space-y-2">
                  <Search className="w-8 h-8 mx-auto text-slate-600" />
                  <p>Select a trade from the left panel to execute automated Root Cause Analysis.</p>
                </div>
              ) : rcaReport.has_evidence === false ? (
                <div className="p-8 bg-slate-950 border border-slate-800 rounded-xl text-center space-y-2">
                  <AlertTriangle className="w-8 h-8 text-amber-400 mx-auto" />
                  <h3 className="text-sm font-bold text-amber-400">INSUFFICIENT EVIDENCE FOR RCA</h3>
                  <p className="text-xs text-slate-400">{rcaReport.message}</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* RCA Overview Box */}
                  <div className="p-4 bg-slate-950 border border-purple-500/30 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs text-purple-400 font-bold">REPORT: {rcaReport.report_id}</span>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5" /> RCA COMPLETE (100% CONFIDENCE)
                      </span>
                    </div>
                    <h3 className="text-sm font-bold text-white">{rcaReport.root_cause}</h3>
                    <div className="text-xs text-slate-400 font-mono">
                      Target Symbol: {rcaReport.symbol} | Realized PnL: ${rcaReport.realized_pnl?.toFixed(2)} USDT
                    </div>
                  </div>

                  {/* Evidence Chain Reconstructed Steps */}
                  <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider">Reconstructed Evidence Chain</h3>
                  <div className="space-y-2">
                    {rcaReport.evidence_items?.map((item: string, idx: number) => (
                      <div key={idx} className="p-3 bg-slate-950 border border-slate-800/80 rounded-xl text-xs font-mono text-slate-200">
                        {item}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
