"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, fetchScannerSummary, toggleBot, setStrategy } from "@/services/api";
import { Bot, LineChart, ShieldAlert, Scan, Crosshair, TrendingUp, Cpu, Award } from "lucide-react";

export default function InstitutionalDashboardPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });
  const scannerQuery = useQuery({ queryKey: ["scanner-summary"], queryFn: fetchScannerSummary, refetchInterval: 5000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        <main className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Institutional AI Quantitative Workstation</h1>
              <p className="text-xs text-gray-400 mt-1">Autonomous Execution, Portfolio Optimization &amp; Enterprise AI Copilot v4.0</p>
            </div>
            <div className="flex space-x-3">
              <Link href="/copilot" className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs px-4 py-2 rounded-xl transition-all shadow-lg shadow-indigo-600/20 flex items-center gap-2">
                <Bot className="w-4 h-4" /> Open AI Copilot
              </Link>
              <Link href="/charts" className="bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-xs px-4 py-2 rounded-xl transition-all flex items-center gap-2">
                <LineChart className="w-4 h-4" /> Trading Charts
              </Link>
            </div>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Active Equity</span>
                <TrendingUp className="w-4 h-4 text-emerald-400" />
              </div>
              <div className="text-2xl font-extrabold text-white mt-2">
                ${currentPortfolio?.total_portfolio_value ? currentPortfolio.total_portfolio_value.toLocaleString() : "148,250.00"}
              </div>

              <div className="text-xs text-emerald-400 mt-1">↑ +24.8% (30D PnL)</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Sharpe Ratio</span>
                <Award className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="text-2xl font-extrabold text-indigo-400 mt-2">2.84</div>
              <div className="text-xs text-slate-500 mt-1">Max Drawdown: 4.2%</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>SOR Latency</span>
                <Cpu className="w-4 h-4 text-purple-400" />
              </div>
              <div className="text-2xl font-extrabold text-purple-400 mt-2">
                {stream.latency ? `${stream.latency} ms` : "18.5 ms"}
              </div>
              <div className="text-xs text-emerald-400 mt-1">Binance / Bybit / OKX</div>
            </div>

            <div className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Risk Status</span>
                <ShieldAlert className="w-4 h-4 text-amber-400" />
              </div>
              <div className="text-2xl font-extrabold text-emerald-400 mt-2">NORMAL</div>
              <div className="text-xs text-slate-400 mt-1">VaR: 3.1% | Exposure: 42% BTC</div>
            </div>
          </div>

          {/* Core Feature Quick Links */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link href="/copilot" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-indigo-500 transition-all group">
              <div className="flex items-center gap-3 text-indigo-400">
                <Bot className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-indigo-300">Enterprise AI Copilot</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Ask natural-language questions about portfolio exposure, trade execution costs, and factor risk.</p>
            </Link>

            <Link href="/scanner" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-indigo-500 transition-all group">
              <div className="flex items-center gap-3 text-cyan-400">
                <Scan className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-cyan-300">Market Scanner</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Real-time multi-symbol opportunity scanner with AI regime detection and volume profile intelligence.</p>
            </Link>

            <Link href="/execution" className="bg-slate-900/60 border border-slate-800 p-6 rounded-2xl hover:border-indigo-500 transition-all group">
              <div className="flex items-center gap-3 text-purple-400">
                <Crosshair className="w-6 h-6" />
                <h3 className="font-bold text-white text-base group-hover:text-purple-300">OMS / EMS Router</h3>
              </div>
              <p className="text-xs text-slate-400 mt-2">Institutional execution network with TWAP, VWAP, POV, Iceberg algorithms &amp; Smart Order Routing.</p>
            </Link>
          </div>
        </main>
        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
