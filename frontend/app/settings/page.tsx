"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, depositVirtualFunds, withdrawVirtualFunds, saveExecutionParameters, apiFetch } from "@/services/api";

import { useTheme, COLOR_THEMES, ColorThemeId } from "@/context/ThemeContext";
import { Wallet, PlusCircle, MinusCircle, CheckCircle2, AlertCircle, RefreshCw, Palette, Check, Globe } from "lucide-react";

const TIMEZONES = [
  { value: "UTC", label: "UTC - Coordinated Universal Time (+00:00)" },
  { value: "Asia/Kolkata", label: "Asia/Kolkata - IST (India Standard Time +05:30)" },
  { value: "America/New_York", label: "America/New_York - EST/EDT (US Eastern -05:00/-04:00)" },
  { value: "America/Chicago", label: "America/Chicago - CST/CDT (US Central -06:00/-05:00)" },
  { value: "America/Denver", label: "America/Denver - MST/MDT (US Mountain -07:00/-06:00)" },
  { value: "America/Los_Angeles", label: "America/Los_Angeles - PST/PDT (US Pacific -08:00/-07:00)" },
  { value: "America/Anchorage", label: "America/Anchorage - AKST/AKDT (Alaska -09:00/-08:00)" },
  { value: "Pacific/Honolulu", label: "Pacific/Honolulu - HST (Hawaii -10:00)" },
  { value: "America/Sao_Paulo", label: "America/Sao_Paulo - BRT (Brazil -03:00)" },
  { value: "Europe/London", label: "Europe/London - GMT/BST (UK +00:00/+01:00)" },
  { value: "Europe/Paris", label: "Europe/Paris - CET/CEST (Central Europe +01:00/+02:00)" },
  { value: "Europe/Berlin", label: "Europe/Berlin - CET/CEST (Germany +01:00/+02:00)" },
  { value: "Europe/Moscow", label: "Europe/Moscow - MSK (Moscow +03:00)" },
  { value: "Asia/Dubai", label: "Asia/Dubai - GST (Gulf Standard Time +04:00)" },
  { value: "Asia/Karachi", label: "Asia/Karachi - PKT (Pakistan Time +05:00)" },
  { value: "Asia/Dhaka", label: "Asia/Dhaka - BST (Bangladesh Time +06:00)" },
  { value: "Asia/Bangkok", label: "Asia/Bangkok - ICT (Indochina Time +07:00)" },
  { value: "Asia/Singapore", label: "Asia/Singapore - SGT (Singapore Time +08:00)" },
  { value: "Asia/Hong_Kong", label: "Asia/Hong_Kong - HKT (Hong Kong Time +08:00)" },
  { value: "Asia/Shanghai", label: "Asia/Shanghai - CST (China Standard Time +08:00)" },
  { value: "Asia/Tokyo", label: "Asia/Tokyo - JST (Japan Standard Time +09:00)" },
  { value: "Asia/Seoul", label: "Asia/Seoul - KST (Korea Standard Time +09:00)" },
  { value: "Australia/Sydney", label: "Australia/Sydney - AEST/AEDT (Sydney +10:00/+11:00)" },
  { value: "Pacific/Auckland", label: "Pacific/Auckland - NZST/NZDT (New Zealand +12:00/+13:00)" },
];

export default function SettingsPage() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const stream = useTradingStream();
  const { theme, setTheme } = useTheme();

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

  // Timezone State
  const [selectedTimezone, setSelectedTimezone] = useState<string>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('lumo_user_timezone') || 'Asia/Kolkata';
    }
    return 'Asia/Kolkata';
  });
  const [timezoneFeedback, setTimezoneFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

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
    if (isNaN(lev) || lev < 1 || lev > 100) {
      setParamFeedback({ type: 'error', message: 'Default leverage multiplier must be between 1x and 100x.' });
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
    try {
      const res = await depositVirtualFunds(val);
      setFeedback({ type: "success", message: res.message || `Successfully deposited $${val.toLocaleString()} USDT into paper wallet!` });
      portfolioQuery.refetch();
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Failed to process virtual deposit." });
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
    try {
      const res = await withdrawVirtualFunds(val);
      setFeedback({ type: "success", message: res.message || `Successfully withdrawn $${val.toLocaleString()} USDT from paper wallet!` });
      portfolioQuery.refetch();
    } catch (err: any) {
      setFeedback({ type: "error", message: err.message || "Failed to process virtual withdrawal." });
    } finally {
      setIsWithdrawing(false);
    }
  };

  const handleSaveTimezone = async () => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('lumo_user_timezone', selectedTimezone);
    }
    try {
      await apiFetch('/api/auth/profile', {
        method: 'PUT',
        body: JSON.stringify({ timezone: selectedTimezone })
      });
      setTimezoneFeedback({
        type: 'success',
        message: `System timezone updated to ${selectedTimezone} successfully!`
      });
    } catch (err: any) {
      setTimezoneFeedback({
        type: 'success',
        message: `Timezone saved locally to ${selectedTimezone}!`
      });
    }
  };

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6">
          {/* Header title banner */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Platform Settings &amp; Execution Preferences</h1>
              <p className="text-xs text-slate-400 mt-1">Manage virtual balances, theme palettes, execution parameters, and global timezones</p>
            </div>
          </div>

          {/* Theme Palette Switcher */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
            <div className="flex items-center gap-3 border-b border-slate-800/80 pb-3">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Palette className="w-5 h-5" />
              </div>
              <div>
                <h2 className="text-md font-semibold text-slate-200">Terminal Theme &amp; Color Palette</h2>
                <p className="text-xs text-slate-400 mt-0.5">Customize the visual styling, accent colors, and dark mode interface</p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
              {COLOR_THEMES.map((th) => {
                const isActive = theme === th.id;
                return (
                  <button
                    key={th.id}
                    onClick={() => setTheme(th.id as ColorThemeId)}
                    className={`flex items-center justify-between p-3 rounded-xl border text-left transition-all ${
                      isActive
                        ? "bg-slate-800 border-cyan-500 shadow-md shadow-cyan-500/10 ring-1 ring-cyan-500/40"
                        : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <span className="h-3.5 w-3.5 rounded-full border border-white/20" style={{ backgroundColor: th.accentColor }} />
                      <span className="text-xs font-semibold text-slate-200">{th.name}</span>
                    </div>

                    {isActive && <Check className="w-4 h-4 text-cyan-400" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Deposit & Withdraw Capital Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Deposit Virtual Funds */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                    <PlusCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-md font-semibold text-slate-200">Deposit Virtual USDT</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Top up paper trading wallet capital</p>
                  </div>
                </div>
              </div>

              {feedback && (
                <div className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border ${
                  feedback.type === "success" 
                    ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400" 
                    : "bg-rose-500/10 border-rose-500/20 text-rose-400"
                }`}>
                  {feedback.type === "success" ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                  <span>{feedback.message}</span>
                </div>
              )}

              <form onSubmit={handleDeposit} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Deposit Amount ($ USDT)</label>
                  <div className="relative flex items-center">
                    <span className="absolute left-3 text-slate-500 font-bold text-xs">$</span>
                    <input
                      type="number"
                      value={depositAmount}
                      onChange={(e) => setDepositAmount(e.target.value)}
                      min="1"
                      step="1"
                      className="w-full pl-7 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                      placeholder="1000"
                    />
                  </div>
                </div>
                <div className="flex space-x-2">
                  {[1000, 5000, 10000, 50000].map((amt) => (
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
                  className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-100 font-semibold text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
                >
                  {isDepositing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <PlusCircle className="w-4 h-4" />}
                  <span>{isDepositing ? "Processing..." : "Deposit Virtual Funds"}</span>
                </button>
              </form>
            </div>

            {/* Withdraw Virtual Funds */}
            <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                    <MinusCircle className="w-5 h-5" />
                  </div>
                  <div>
                    <h2 className="text-md font-semibold text-slate-200">Withdraw Virtual USDT</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Deduct virtual capital from wallet</p>
                  </div>
                </div>
              </div>

              <form onSubmit={handleWithdraw} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold text-slate-400">Withdrawal Amount ($ USDT)</label>
                  <div className="relative flex items-center">
                    <span className="absolute left-3 text-slate-500 font-bold text-xs">$</span>
                    <input
                      type="number"
                      value={withdrawAmount}
                      onChange={(e) => setWithdrawAmount(e.target.value)}
                      min="1"
                      step="1"
                      className="w-full pl-7 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                      placeholder="1000"
                    />
                  </div>
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
                <div className="relative flex items-center">
                  <span className="absolute left-3 text-slate-500 font-bold text-xs">$</span>
                  <input
                    type="number"
                    value={defaultAllocation}
                    onChange={(e) => setDefaultAllocation(e.target.value)}
                    placeholder="1000"
                    className="w-full pl-7 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-xs font-semibold text-slate-400">Default Leverage Multiplier (1x - 100x)</label>
                <input
                  type="number"
                  value={defaultLeverage}
                  onChange={(e) => setDefaultLeverage(e.target.value)}
                  min={1}
                  max={100}
                  placeholder="1"
                  className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-mono text-slate-100 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Global Timezones & Regional Localization Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <Globe className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-md font-semibold text-slate-200">Global Timezone &amp; Regional Localization</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Select your local timezone for chart timestamps, trade execution logs, and reporting</p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleSaveTimezone}
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:brightness-110 text-white font-bold rounded-xl text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-500/20 flex items-center gap-1.5 cursor-pointer"
              >
                <Check className="w-4 h-4" />
                <span>Save Timezone</span>
              </button>
            </div>

            {timezoneFeedback && (
              <div className="p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>{timezoneFeedback.message}</span>
              </div>
            )}

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">System Timezone</label>
              <select
                value={selectedTimezone}
                onChange={(e) => setSelectedTimezone(e.target.value)}
                className="w-full px-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-sm font-semibold text-slate-100 focus:outline-none focus:border-cyan-500"
              >
                {TIMEZONES.map((tz) => (
                  <option key={tz.value} value={tz.value} className="bg-slate-900 text-slate-100">
                    {tz.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>
    </div>
  );
}
