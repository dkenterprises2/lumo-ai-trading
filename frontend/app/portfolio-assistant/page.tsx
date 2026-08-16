"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, apiFetch } from "@/services/api";
import { TrendingUp, PieChart, ShieldCheck, DollarSign, Layers, RefreshCw, AlertCircle } from "lucide-react";

export default function ConversationalPortfolioAssistantPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const portfolioAssistantQuery = useQuery({
    queryKey: ["portfolio-assistant-data"],
    queryFn: async () => {
      const res = await apiFetch("/api/portfolio-assistant/summary");
      if (!res.ok) throw new Error("Failed to fetch portfolio assistant explanation");
      return res.json();
    },
    refetchInterval: 5000
  });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const assistantData = portfolioAssistantQuery.data ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6 max-w-7xl">
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2.5">
                <TrendingUp className="w-7 h-7 text-cyan-400" />
                Portfolio Intelligence Assistant
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Real-time position concentration, factor exposure drift, margin utilization, &amp; risk rebalancing logic.
              </p>
            </div>
            <button
              onClick={() => portfolioAssistantQuery.refetch()}
              className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl flex items-center gap-1.5 cursor-pointer"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${portfolioAssistantQuery.isFetching ? "animate-spin" : ""}`} />
              <span>Refresh Portfolio AI</span>
            </button>
          </div>

          {assistantData?.has_data === false ? (
            <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl text-center space-y-3">
              <AlertCircle className="w-10 h-10 text-slate-500 mx-auto" />
              <h2 className="text-base font-bold text-slate-300 uppercase tracking-wider">NO PORTFOLIO DATA AVAILABLE</h2>
              <p className="text-xs text-slate-400 max-w-md mx-auto">
                No active open positions exist for this trader account. As new positions are filled by the Spot/Arbitrage engine, real-time risk exposure and concentration intelligence will appear here.
              </p>
            </div>
          ) : (
            <>
              {/* Portfolio Key Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                    <DollarSign className="w-4 h-4 text-emerald-400" />
                    <span>Total Portfolio Value</span>
                  </div>
                  <div className="text-lg font-bold font-mono text-white">
                    ${assistantData?.total_value_usd?.toLocaleString() ?? "0.00"} USDT
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span>Active Open Positions</span>
                  </div>
                  <div className="text-lg font-bold font-mono text-cyan-400">
                    {assistantData?.active_positions_count ?? 0} Positions
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                    <PieChart className="w-4 h-4 text-purple-400" />
                    <span>Top Concentration Asset</span>
                  </div>
                  <div className="text-lg font-bold font-mono text-purple-400">
                    {assistantData?.top_asset ?? "N/A"} ({assistantData?.top_asset_concentration_pct ?? 0}%)
                  </div>
                </div>

                <div className="p-4 bg-slate-900 border border-slate-800 rounded-2xl space-y-1">
                  <div className="text-xs text-slate-400 flex items-center gap-1.5 font-medium">
                    <ShieldCheck className="w-4 h-4 text-amber-400" />
                    <span>Unrealized PnL</span>
                  </div>
                  <div className={`text-lg font-bold font-mono ${
                    (assistantData?.total_unrealized_pnl ?? 0) >= 0 ? "text-emerald-400" : "text-rose-400"
                  }`}>
                    ${assistantData?.total_unrealized_pnl?.toLocaleString() ?? "0.00"} USDT
                  </div>
                </div>
              </div>

              {/* Portfolio Narrative & Recommendations */}
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <TrendingUp className="w-5 h-5 text-cyan-400" />
                  Portfolio Risk &amp; Exposure Analysis Narrative
                </h2>

                <div className="p-4 bg-slate-950 border border-slate-800/80 rounded-xl space-y-2 text-xs font-mono text-slate-200">
                  <p>{assistantData?.summary}</p>
                </div>

                <h3 className="text-xs font-bold text-slate-300 uppercase tracking-wider mt-4">Automated Risk &amp; Allocation Recommendations</h3>
                <div className="space-y-2">
                  {assistantData?.recommended_actions?.map((rec: string, idx: number) => (
                    <div key={idx} className="p-3 bg-slate-950 border border-cyan-500/20 rounded-xl text-xs text-cyan-300 font-semibold flex items-center gap-2">
                      <ShieldCheck className="w-4 h-4 text-cyan-400 shrink-0" />
                      <span>{rec}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Asset Concentration Table */}
              <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h2 className="text-base font-bold text-white flex items-center gap-2">
                  <PieChart className="w-5 h-5 text-purple-400" />
                  Real-time Position Concentration Breakdown
                </h2>

                <div className="overflow-x-auto">
                  <table className="w-full text-xs text-left font-mono">
                    <thead className="bg-slate-950 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
                      <tr>
                        <th className="p-3">Symbol</th>
                        <th className="p-3">Side</th>
                        <th className="p-3">Margin USD</th>
                        <th className="p-3">Concentration (%)</th>
                        <th className="p-3">Unrealized PnL</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {assistantData?.concentration?.map((item: any) => (
                        <tr key={item.symbol} className="hover:bg-slate-950/50 transition-colors">
                          <td className="p-3 font-bold text-white">{item.symbol}</td>
                          <td className="p-3">
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              item.side === "BUY" ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"
                            }`}>
                              {item.side}
                            </span>
                          </td>
                          <td className="p-3 text-slate-200">${item.margin_usd?.toLocaleString()}</td>
                          <td className="p-3 text-purple-400 font-bold">{item.concentration_pct}%</td>
                          <td className={`p-3 font-bold ${item.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
                            ${item.unrealized_pnl?.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
