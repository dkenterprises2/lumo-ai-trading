"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy } from "@/services/api";
import { ChessKnight, CheckCircle2 } from "lucide-react";

export default function StrategiesPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;
  const activeStrat = currentPortfolio?.active_strategy ?? "AI Hybrid";

  const strategies = [
    { name: "AI Hybrid", desc: "Combines 50% Technical Score + 50% Sentiment Analysis for balanced signals." },
    { name: "Trend Following", desc: "Focuses on EMA crossovers, MACD momentum, and trend continuation." },
    { name: "Breakout", desc: "Detects Bollinger Band squeeze breakouts and high volume spikes." },
    { name: "Scalping", desc: "Fast-execution strategy utilizing short timeframe RSI oversold/overbought rebounds." },
    { name: "Grid", desc: "Automated grid placement across support and resistance boundaries." },
    { name: "DCA", desc: "Dollar Cost Averaging engine for recurring positional accumulation." }
  ];

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="flex items-center justify-between">
            <h1 className="text-xl font-bold tracking-tight text-slate-100">AI Quantitative Strategy Manager</h1>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {strategies.map((strat) => (
              <div key={strat.name} className={`p-5 rounded-2xl border transition ${activeStrat === strat.name ? "bg-cyan-500/10 border-cyan-500/40" : "bg-slate-900/60 border-slate-800"}`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <ChessKnight className="h-5 w-5 text-cyan-400" />
                    <h3 className="font-bold text-slate-100">{strat.name}</h3>
                  </div>
                  {activeStrat === strat.name && <CheckCircle2 className="h-5 w-5 text-cyan-400" />}
                </div>
                <p className="text-xs text-slate-400 mb-4">{strat.desc}</p>
                <button onClick={() => setStrategy(strat.name, currentPortfolio?.risk_mode ?? "Moderate")} className="px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-semibold text-slate-200 hover:border-cyan-500/40">
                  Select Strategy
                </button>
              </div>
            ))}
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
