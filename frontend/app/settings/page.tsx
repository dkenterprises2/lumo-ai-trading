"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, depositVirtualFunds, withdrawVirtualFunds, saveExecutionParameters } from "@/services/api";

import { useTheme, COLOR_THEMES, ColorThemeId } from "@/context/ThemeContext";
import { Wallet, PlusCircle, MinusCircle, ArrowDownRight, ArrowUpRight, CheckCircle2, AlertCircle, RefreshCw, Palette, Check } from "lucide-react";

export default function SettingsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();
  const { theme, setTheme, currentThemeOption } = useTheme();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.isConnected && stream.portfolio ? stream.portfolio : portfolioQuery.data ?? null;

  // Deposit & Withdrawal State
  const [depositAmount, setDepositAmount] = useState<string>("5000");
  const [withdrawAmount, setWithdrawAmount] = useState<string>("1000");
  const [isDepositing, setIsDepositing] = useState(false);
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Default Execution Parameters State
  const [defaultAllocation, setDefaultAllocation] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('lumo_default_allocation') || '1000';
    }
    return '1000';
  });
  const [defaultLeverage, setDefaultLeverage] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('lumo_default_leverage') || '1';
    }
    return '1';
  });
  const [paramFeedback, setParamFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  React.useEffect(() => {
    if (currentPortfolio) {
      if (currentPortfolio.default_allocation_usd) {
        setDefaultAllocation(currentPortfolio.default_allocation_usd.toString());
      }
      if (currentPortfolio.default_leverage) {
        setDefaultLeverage(currentPortfolio.default_leverage.toString());
      }
    }
  }, [currentPortfolio?.default_allocation_usd, currentPortfolio?.default_leverage]);

  const handleApplyParameters = async () => {
    const alloc = parseFloat(defaultAllocation);
    const lev = parseInt(defaultLeverage, 10);

    if (isNaN(alloc) || alloc <= 0) {
      setParamFeedback({ type: 'error', message: 'Please enter a valid default allocation amount greater than 0.' });
      return;
    }
    if (isNaN(lev) || lev < 1 || lev > 25) {
      setParamFeedback({ type: 'error', message: 'Default leverage multiplier must be between 1x and 25x.' });
      return;
    }

    if (typeof window !== 'undefined') {
      localStorage.setItem('lumo_default_allocation', alloc.toString());
      localStorage.setItem('lumo_default_leverage', lev.toString());
    }

    try {
      const res = await saveExecutionParameters(alloc, lev);
      setParamFeedback({
        type: 'success',
        message: res.message || `Execution parameters applied successfully! Default Allocation: $${alloc.toLocaleString()} USDT | Leverage: ${lev}x`
      });
      portfolioQuery.refetch();
    } catch (err: any) {
      setParamFeedback({
        type: 'error',
        message: err.message || `Failed to sync parameters with AI trading engine.`
      });
    }
  };




  const handleDeposit = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(depositAmount);
    if (isNaN(val) || val <= 0) {
      setFeedback({ type: "error", message: "Please enter a valid deposit amount greater than 0." });
      return;
    }
    setIsDepositing(true);
    setFeedback(null);
    try {
      const res = await depositVirtualFunds(val);
      setFeedback({ type: "success", message: res.message });
      portfolioQuery.refetch();
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Failed to deposit virtual funds." });
    } finally {
      setIsDepositing(false);
    }
  };

  const handleWithdraw = async (e: React.FormEvent) => {
    e.preventDefault();
    const val = parseFloat(withdrawAmount);
    if (isNaN(val) || val <= 0) {
      setFeedback({ type: "error", message: "Please enter a valid withdrawal amount greater than 0." });
      return;
    }
    setIsWithdrawing(true);
    setFeedback(null);
    try {
      const res = await withdrawVirtualFunds(val);
      setFeedback({ type: "success", message: res.message });
      portfolioQuery.refetch();
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Failed to withdraw virtual funds." });
    } finally {
      setIsWithdrawing(false);
    }
  };

  return (
    <div className="flex min-h-screen transition-colors duration-300 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />
        
        <main className="space-y-6 max-w-5xl">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Enterprise Settings & Customization</h1>
              <p className="text-sm opacity-70 mt-1">Manage color themes, virtual paper trading capital, and execution rules</p>
            </div>
          </div>

          {feedback && (
            <div className={`p-4 rounded-xl border flex items-center space-x-3 transition-all duration-300 ${feedback.type === "success" ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" : "bg-rose-500/10 border-rose-500/30 text-rose-400"}`}>
              {feedback.type === "success" ? <CheckCircle2 className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
              <span className="text-sm font-medium">{feedback.message}</span>
            </div>
          )}

          {/* Terminal Color Theme Options */}
          <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl backdrop-blur-xl space-y-6">
            <div className="flex items-center space-x-3 border-b border-slate-800/80 pb-4">
              <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                <Palette className="w-6 h-6" />
              </div>
              <div>
                <h2 className="text-lg font-semibold">Terminal Color Theme Options</h2>
                <p className="text-xs opacity-70">Select your preferred color theme for optimal contrast and visual clarity</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {COLOR_THEMES.map((item) => {
                const isActive = theme === item.id;
                const isLightCard = item.id === "fluent-light";
                const textColor = isLightCard ? "#0f172a" : "#f8fafc";
                const descColor = isLightCard ? "#334155" : "#cbd5e1";
                const metaColor = isLightCard ? "#475569" : "#94a3b8";
                const cardBorder = isActive 
                  ? (isLightCard ? "2px solid #0284c7" : "2px solid #06b6d4") 
                  : (isLightCard ? "1px solid #cbd5e1" : "1px solid #1e293b");

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setTheme(item.id)}
                    className={`p-4 rounded-xl text-left transition-all relative overflow-hidden flex flex-col justify-between space-y-3 cursor-pointer shadow-md ${
                      isActive
                        ? "ring-2 ring-cyan-500/40 shadow-lg scale-[1.02]"
                        : "hover:border-slate-700 hover:scale-[1.01]"
                    }`}
                    style={{
                      backgroundColor: item.bgHex,
                      border: cardBorder,
                      color: textColor
                    }}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <span className="w-4 h-4 rounded-full border border-black/20 inline-block shadow-sm flex-shrink-0" style={{ backgroundColor: item.accentColor }} />
                        <span className="font-bold text-sm tracking-tight" style={{ color: textColor }}>{item.name}</span>
                      </div>
                      {isActive && (
                        <span className="px-2.5 py-0.5 rounded-full text-white text-[10px] font-bold tracking-wider flex items-center space-x-1 shadow-sm" style={{ backgroundColor: item.accentColor }}>
                          <Check className="w-3 h-3" />
                          <span>ACTIVE</span>
                        </span>
                      )}
                    </div>
                    <p className="text-xs leading-relaxed font-medium" style={{ color: descColor }}>{item.description}</p>
                    <div className="flex items-center justify-between pt-2 border-t text-[11px] font-mono" style={{ borderColor: isLightCard ? "rgba(0,0,0,0.15)" : "rgba(255,255,255,0.15)", color: metaColor }}>
                      <span className="font-semibold">ACCENT: {item.accentColor}</span>
                      <div className="flex items-center space-x-1.5">
                        <span className="w-3 h-3 rounded-full border border-black/20" style={{ backgroundColor: item.bgHex }} />
                        <span className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: item.accentColor }} />
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

          </div>


          {/* Virtual Capital Management Card */}
          <div className="p-6 rounded-2xl bg-gradient-to-b from-slate-900/80 to-slate-900/40 border border-slate-800 shadow-xl backdrop-blur-xl space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
              <div className="flex items-center space-x-3">
                <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400">
                  <Wallet className="w-6 h-6" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-slate-100">Paper Trading Virtual Wallet</h2>
                  <p className="text-xs text-slate-400">Add or withdraw demo USDT capital to simulate larger portfolio strategies</p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block">Available Balance</span>
                <span className="text-2xl font-bold font-mono text-cyan-400">
                  ${currentPortfolio?.usdt_balance?.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) ?? "0.00"} <span className="text-xs font-sans text-slate-400">USDT</span>
                </span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Deposit Section */}
              <form onSubmit={handleDeposit} className="p-5 rounded-xl bg-slate-950/60 border border-emerald-500/20 space-y-4">
                <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
                  <ArrowDownRight className="w-4 h-4" />
                  <span>Deposit Virtual Funds</span>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-1">Amount (USDT)</label>
                  <input
                    type="number"
                    min="1"
                    step="any"
                    value={depositAmount}
                    onChange={(e) => setDepositAmount(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-emerald-500/50"
                    placeholder="e.g. 5000"
                  />
                </div>
                <div className="flex space-x-2">
                  {[1000, 5000, 10000].map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      onClick={() => setDepositAmount(amt.toString())}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:border-emerald-500/40 hover:text-emerald-400 transition-all"
                    >
                      +${amt.toLocaleString()}
                    </button>
                  ))}
                </div>
                <button
                  type="submit"
                  disabled={isDepositing}
                  className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                >
                  {isDepositing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
                  <span>{isDepositing ? "Processing..." : "Add Virtual Funds"}</span>
                </button>
              </form>

              {/* Withdrawal Section */}
              <form onSubmit={handleWithdraw} className="p-5 rounded-xl bg-slate-950/60 border border-rose-500/20 space-y-4">
                <div className="flex items-center space-x-2 text-rose-400 font-semibold text-sm">
                  <ArrowUpRight className="w-4 h-4" />
                  <span>Withdraw Virtual Funds</span>
                </div>
                <div>
                  <label className="text-xs font-semibold text-slate-400 block mb-1">Amount (USDT)</label>
                  <input
                    type="number"
                    min="1"
                    step="any"
                    value={withdrawAmount}
                    onChange={(e) => setWithdrawAmount(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-slate-900 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-rose-500/50"
                    placeholder="e.g. 1000"
                  />
                </div>
                <div className="flex space-x-2">
                  {[500, 1000, 5000].map((amt) => (
                    <button
                      key={amt}
                      type="button"
                      onClick={() => setWithdrawAmount(amt.toString())}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:border-rose-500/40 hover:text-rose-400 transition-all"
                    >
                      -${amt.toLocaleString()}
                    </button>
                  ))}
                </div>
                <button
                  type="submit"
                  disabled={isWithdrawing}
                  className="w-full py-2.5 px-4 rounded-xl bg-rose-600 hover:bg-rose-500 text-slate-100 font-semibold text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                >
                  {isWithdrawing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <MinusCircle className="w-4 h-4" />}
                  <span>{isWithdrawing ? "Processing..." : "Withdraw Virtual Funds"}</span>
                </button>
              </form>
            </div>
          </div>

          {/* Platform General Preferences & Execution Parameters */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div>
                <h2 className="text-md font-semibold text-slate-200">Default Execution Parameters</h2>
                <p className="text-xs text-slate-400 mt-0.5">Configure default trade sizing and leverage applied across quick order forms</p>
              </div>
              <button
                type="button"
                onClick={handleApplyParameters}
                className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-500/20 flex items-center gap-1.5 cursor-pointer"
              >
                <Check className="w-4 h-4" />
                <span>Apply Parameters</span>
              </button>
            </div>

            {paramFeedback && (
              <div className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border ${
                paramFeedback.type === "success" 
                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
                  : "bg-rose-500/10 border-rose-500/20 text-rose-400"
              }`}>
                {paramFeedback.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                <span>{paramFeedback.message}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400">Default Allocation USD per Trade ($ USDT)</label>
                <input
                  type="number"
                  value={defaultAllocation}
                  onChange={(e) => setDefaultAllocation(e.target.value)}
                  placeholder="1000"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400">Default Leverage Multiplier (1x - 25x)</label>
                <input
                  type="number"
                  value={defaultLeverage}
                  onChange={(e) => setDefaultLeverage(e.target.value)}
                  min={1}
                  max={25}
                  placeholder="1"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}


