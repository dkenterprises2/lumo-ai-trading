"use client";

import React from "react";
import { PortfolioState, NewsSentiment } from "@/types/trading";
import { TradingConnectionState } from "@/hooks/useTradingStream";
import {
  Wallet,
  TrendingUp,
  Award,
  Flame,
  Bot,
  Activity,
  Wifi,
  Settings,
  Power,
  ShieldCheck,
  ShieldAlert
} from "lucide-react";

interface HeaderProps {
  portfolio: PortfolioState | null;
  newsSentiment: NewsSentiment | null;
  latency: number | null;
  connectionState: TradingConnectionState;
  onToggleBot: (enable: boolean) => void;
  onSelectStrategy: (strategy: string) => void;
}

import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export function Header({
  portfolio,
  newsSentiment,
  latency,
  connectionState,
  onToggleBot,
  onSelectStrategy
}: HeaderProps) {
  const { user } = useAuth();
  const [botState, setBotState] = React.useState<boolean | null>(null);
  const lastAutoBot = React.useRef<boolean | undefined>(undefined);

  React.useEffect(() => {
    if (portfolio?.auto_bot_enabled !== undefined && portfolio.auto_bot_enabled !== lastAutoBot.current) {
      lastAutoBot.current = portfolio.auto_bot_enabled;
      setBotState(portfolio.auto_bot_enabled);
    }
  }, [portfolio?.auto_bot_enabled]);




  const portVal = portfolio?.total_portfolio_value;
  const dailyPnlUsd = portfolio?.daily_pnl_usd;
  const dailyPnlPct = portfolio?.daily_pnl_pct;
  const winRate = portfolio?.win_rate;
  const totalTrades = portfolio?.total_closed_trades;
  const isBotActive = botState !== null ? botState : (portfolio?.auto_bot_enabled ?? false);


  const fearGreedVal = newsSentiment?.fear_greed.value;
  const fearGreedLabel = newsSentiment?.fear_greed.classification;
  const auditStatus = portfolio?.accounting_status ?? "PENDING";
  const isConnected = connectionState === "live";
  const formatMoney = (value: number | undefined) => value === undefined ? "—" : `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatSignedMoney = (value: number | undefined) => {

    if (value === undefined) return "—";
    if (value >= 0) return `+$${value.toFixed(2)}`;
    return `-$${Math.abs(value).toFixed(2)}`;
  };
  const formatSignedPercent = (value: number | undefined) => {
    if (value === undefined) return "—";
    if (value >= 0) return `+${value.toFixed(2)}%`;
    return `-${Math.abs(value).toFixed(2)}%`;
  };


  return (
    <header className="space-y-4 mb-6">
      {/* Top Controls & Strategic Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 shadow-xl">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Activity className="h-6 w-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-100 tracking-tight">Executive Trading Terminal</h1>
            <p className="text-xs text-slate-400">Real-time Quantitative Portfolio & Risk Engine</p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Latency & Connectivity */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono">
            <span className={`h-2 w-2 rounded-full ${isConnected ? "bg-emerald-500 animate-pulse" : "bg-rose-500"}`} />
            <span className="text-slate-300">{connectionState === "live" ? "WS LIVE" : connectionState.toUpperCase()}</span>
            <span className="text-slate-500">|</span>
            <Wifi className="h-3.5 w-3.5 text-cyan-400" />
            <span className="text-cyan-400">{latency === null ? "—" : `${latency}ms`}</span>
          </div>

          {/* Audit Badge */}
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-medium ${
              auditStatus === "PASS" 
              ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
              : "bg-rose-500/10 border-rose-500/30 text-rose-400 animate-bounce"
          }`}>
            {auditStatus === "PASS" ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
            <span>AUDIT: {auditStatus}{auditStatus === "PENDING" ? "" : " (0.01 USDT Tol)"}</span>
          </div>

          {/* Strategy Dropdown */}
          <div className="flex items-center gap-2 bg-slate-950 px-3 py-1.5 rounded-xl border border-slate-800">
            <span className="text-xs text-slate-400 font-medium">Strategy:</span>
            <select
              value={portfolio?.active_strategy || "AI Hybrid"}
              onChange={(e) => onSelectStrategy(e.target.value)}
              className="bg-transparent text-xs font-semibold text-cyan-400 focus:outline-none cursor-pointer"
            >
              <option value="AI Hybrid" className="bg-slate-900 text-slate-100">AI Hybrid</option>
              <option value="Trend Following" className="bg-slate-900 text-slate-100">Trend Following</option>
              <option value="Breakout" className="bg-slate-900 text-slate-100">Breakout</option>
              <option value="Scalping" className="bg-slate-900 text-slate-100">Scalping</option>
              <option value="Grid" className="bg-slate-900 text-slate-100">Grid</option>
              <option value="DCA" className="bg-slate-900 text-slate-100">DCA</option>
            </select>
          </div>

          {/* Stop / Start Bot Button */}
          <button
            onClick={async () => {
              const nextState = !isBotActive;
              lastAutoBot.current = nextState;
              setBotState(nextState);
              try {
                await onToggleBot(nextState);
              } catch (err) {
                lastAutoBot.current = !nextState;
                setBotState(!nextState);
              }
            }}




            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-semibold text-xs transition-all duration-200 shadow-lg ${
              isBotActive
                ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-emerald-500/20 hover:brightness-110"
                : "bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-cyan-500/20 hover:brightness-110"
            }`}
          >
            <Power className="h-4 w-4" />
            <span>{isBotActive ? "Auto-Bot: ACTIVE" : "Auto-Bot: OFF"}</span>
          </button>

          {/* User Profile Avatar */}
          {user ? (
            <Link
              href="/profile"
              className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 hover:border-cyan-500/50 transition-all duration-200"
            >
              <img
                src={user.avatar || "https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader"}
                alt={user.name}
                className="w-6 h-6 rounded-full border border-cyan-400/40 bg-slate-900"
              />
              <span className="text-xs font-medium text-slate-200 max-w-[100px] truncate">{user.name}</span>
            </Link>
          ) : (
            <Link
              href="/login"
              className="px-3 py-1.5 text-xs font-semibold rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 hover:bg-cyan-500/20 transition"
            >
              Sign In
            </Link>
          )}

          {/* Settings Quick Icon */}
          <Link href="/settings" className="p-2 rounded-xl bg-slate-950 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition">
            <Settings className="h-4 w-4" />
          </Link>
        </div>
      </div>


      {/* Top Overview Cards Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {/* Card 1: Portfolio Value */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-cyan-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Portfolio Value</span>
            <Wallet className="h-4 w-4 text-cyan-400" />
          </div>
          <div className="text-xl font-extrabold text-slate-100">
            {formatMoney(portVal)}
          </div>
          <div className="text-[10px] text-slate-400 mt-1 truncate">
            Avail: {formatMoney(portfolio?.available_balance)}
          </div>
        </div>

        {/* Card 2: Daily PnL */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-emerald-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Daily PnL</span>
            <TrendingUp className={`h-4 w-4 ${dailyPnlUsd === undefined || dailyPnlUsd >= 0 ? "text-emerald-400" : "text-rose-400"}`} />
          </div>
          <div className={`text-xl font-extrabold ${dailyPnlUsd === undefined || dailyPnlUsd >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
            {formatSignedMoney(dailyPnlUsd)}
          </div>
          <div className="text-[10px] font-medium text-slate-400 mt-1">
            {formatSignedPercent(dailyPnlPct)} today
          </div>
        </div>

        {/* Card 3: Win Rate */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-amber-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Win Rate</span>
            <Award className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-xl font-extrabold text-slate-100">
            {winRate === undefined ? "—" : `${winRate.toFixed(1)}%`}
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {totalTrades === undefined ? "Backend data pending" : `${totalTrades} Closed Trades`}
          </div>
        </div>

        {/* Card 4: Fear & Greed */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-purple-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Fear & Greed</span>
            <Flame className="h-4 w-4 text-purple-400" />
          </div>
          <div className="text-xl font-extrabold text-slate-100">
            {fearGreedVal ?? "—"} <span className="text-xs font-semibold text-purple-400">{fearGreedVal === undefined ? "" : "/100"}</span>
          </div>
          <div className="text-[10px] font-medium text-slate-400 mt-1 truncate">
            {fearGreedLabel ?? "Backend data pending"}
          </div>
        </div>

        {/* Card 5: Bot Status */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-blue-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Bot Status</span>
            <Bot className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-base font-extrabold text-slate-100 flex items-center gap-2">
            <span className={`h-2.5 w-2.5 rounded-full ${isBotActive ? "bg-emerald-400 animate-pulse" : "bg-slate-500"}`} />
            {isBotActive ? "ACTIVE" : "STANDBY"}
          </div>
          <div className="text-[10px] text-slate-400 mt-1 truncate">
            {portfolio?.risk_mode ? `${portfolio.risk_mode} Risk` : "Backend data pending"}
          </div>
        </div>

        {/* Card 6: Exchange Status */}
        <div className="p-4 rounded-2xl bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 hover:border-teal-500/30 transition-all duration-200">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Exchange</span>
            <Activity className="h-4 w-4 text-teal-400" />
          </div>
          <div className="text-base font-extrabold text-emerald-400 flex items-center gap-1.5">
            <span className={`h-2 w-2 rounded-full ${isConnected ? "bg-emerald-400" : "bg-slate-500"}`} />
            PAPER ENGINE
          </div>
          <div className="text-[10px] text-slate-400 mt-1">
            {isConnected ? "Backend stream connected" : "Backend stream unavailable"}
          </div>
        </div>
      </div>
    </header>
  );
}
