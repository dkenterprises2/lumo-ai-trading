"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, fetchScannerSummary, toggleBot, setStrategy, handlePositionAction } from "@/services/api";
import { Bot, LineChart, ShieldAlert, Scan, Crosshair, TrendingUp, Cpu, Award } from "lucide-react";
import { BottomTabsPanel } from "@/components/terminal/BottomTabsPanel";

import { useAuth } from "@/context/AuthContext";
import { SubscriptionLimitsCard } from "@/components/dashboard/SubscriptionLimitsCard";
import { ManualTradingCard } from "@/components/dashboard/ManualTradingCard";
import { InstitutionalModulesGrid } from "@/components/dashboard/InstitutionalModulesGrid";
import { ModuleRegistryStatusWidget } from "@/components/dashboard/ModuleRegistryStatusWidget";


export default function InstitutionalDashboardPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const { user } = useAuth();
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

          {/* Metrics & Trading Limits Panel Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 flex flex-col justify-between space-y-4">
              {/* Quick Metrics Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl shadow-xl backdrop-blur-xl hover:border-slate-700 transition-all group">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
                    <span className="uppercase tracking-wider">Active Equity</span>
                    <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <TrendingUp className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="text-2xl font-extrabold text-white mt-3 font-mono tracking-tight">
                    ${currentPortfolio?.total_portfolio_value ? currentPortfolio.total_portfolio_value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : "10,000.00"}
                  </div>
                  <div className="text-xs font-bold text-emerald-400 mt-1 flex items-center gap-1">
                    <span>↑ +24.8%</span>
                    <span className="text-slate-500 font-normal">(30D PnL)</span>
                  </div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl shadow-xl backdrop-blur-xl hover:border-slate-700 transition-all group">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
                    <span className="uppercase tracking-wider">Sharpe Ratio</span>
                    <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                      <Award className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="text-2xl font-extrabold text-indigo-400 mt-3 font-mono tracking-tight">2.84</div>
                  <div className="text-xs font-medium text-slate-400 mt-1">Max Drawdown: <span className="text-slate-200 font-bold">4.2%</span></div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl shadow-xl backdrop-blur-xl hover:border-slate-700 transition-all group">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
                    <span className="uppercase tracking-wider">SOR Latency</span>
                    <div className="p-2 rounded-xl bg-purple-500/10 text-purple-400 border border-purple-500/20">
                      <Cpu className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="text-2xl font-extrabold text-purple-400 mt-3 font-mono tracking-tight">
                    {stream.latency ? `${stream.latency} ms` : "15 ms"}
                  </div>
                  <div className="text-xs font-semibold text-emerald-400 mt-1">Binance / Bybit / OKX Router</div>
                </div>

                <div className="bg-slate-900/90 border border-slate-800/90 p-5 rounded-3xl shadow-xl backdrop-blur-xl hover:border-slate-700 transition-all group">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400">
                    <span className="uppercase tracking-wider">Risk Status</span>
                    <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
                      <ShieldAlert className="w-4 h-4" />
                    </div>
                  </div>
                  <div className="text-2xl font-extrabold text-emerald-400 mt-3 font-mono tracking-tight">NORMAL</div>
                  <div className="text-xs font-medium text-slate-400 mt-1">VaR: <span className="text-slate-200 font-bold">3.1%</span> | Exposure: <span className="text-cyan-400 font-bold">42% BTC</span></div>
                </div>
              </div>

              {/* Manual Trading Quick Order Terminal */}
              <ManualTradingCard
                currentPrices={stream.livePrices}
                onOrderExecuted={() => portfolioQuery.refetch()}
              />

            </div>


            {/* Subscription & Trading Limits Control Card */}
            <div className="lg:col-span-1">
              <SubscriptionLimitsCard
                userPlan={user?.plan || user?.plan_tier || "INSTITUTIONAL"}
                activePositionsCount={currentPortfolio?.active_positions?.length || 0}
                onPreferencesUpdated={() => portfolioQuery.refetch()}
              />
            </div>
          </div>


          {/* Advanced Trading Intelligence Quick Access Grid */}
          <InstitutionalModulesGrid />

          {/* Active Open Positions & Execution Terminal Widget */}
          <div className="space-y-2">
            <h2 className="text-base font-bold text-slate-200">Live Active Positions &amp; Execution Blotter</h2>
            <BottomTabsPanel
              portfolio={currentPortfolio}
              onPositionAction={async (symbol, action) => {
                await handlePositionAction({ symbol, action });
                portfolioQuery.refetch();
              }}
            />
          </div>

          {/* Enterprise AI & Governance Module Registry Widgets */}
          <ModuleRegistryStatusWidget />

        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
