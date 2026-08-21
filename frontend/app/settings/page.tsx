"use client";

import React, { useState, useEffect } from "react";
import { Sidebar } from "@/components/layout/Sidebar";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import { useTradingStream } from "@/hooks/useTradingStream";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { fetchPortfolio, fetchNewsSentiment, toggleBot, setStrategy, depositVirtualFunds, withdrawVirtualFunds, saveExecutionParameters, resetPaperAccount, apiFetch } from "@/services/api";
import { useCurrency, SUPPORTED_CURRENCIES } from "@/context/CurrencyContext";

import { useTheme, COLOR_THEMES, ColorThemeId } from "@/context/ThemeContext";
import { Wallet, PlusCircle, MinusCircle, CheckCircle2, AlertCircle, RefreshCw, Palette, Check, Globe, Coins, ArrowRightLeft, RotateCcw, ShieldAlert } from "lucide-react";

const TIMEZONES = [
  { value: "Asia/Kolkata", label: "Asia/Kolkata - IST (India Standard Time +05:30)" },
  { value: "UTC", label: "UTC - Coordinated Universal Time (+00:00)" },
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
  const queryClient = useQueryClient();
  const { theme, setTheme } = useTheme();
  const { currency, setCurrency, formatCurrency, currentCurrency } = useCurrency();

  const portfolioQuery = useQuery({ queryKey: ["portfolio"], queryFn: fetchPortfolio, refetchInterval: 5000 });
  const newsQuery = useQuery({ queryKey: ["news-sentiment"], queryFn: fetchNewsSentiment, refetchInterval: 300000 });

  const currentPortfolio = stream.portfolio ?? portfolioQuery.data ?? null;

  // Deposit & Withdrawal State
  const [depositAmount, setDepositAmount] = useState<string>("5000");
  const [withdrawAmount, setWithdrawAmount] = useState<string>("1000");
  const [isDepositing, setIsDepositing] = useState(false);
  const [isWithdrawing, setIsWithdrawing] = useState(false);
  const [feedback, setFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

  // Currency Selection State
  const [selectedCurrency, setSelectedCurrency] = useState<string>(currency);
  const [currencyFeedback, setCurrencyFeedback] = useState<{ type: "success" | "error"; message: string } | null>(null);

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

  // Paper Account Reset State
  const [isResetting, setIsResetting] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [resetFeedback, setResetFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  useEffect(() => {
    if (currency) {
      setSelectedCurrency(currency);
    }
  }, [currency]);

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
      setParamFeedback({ type: 'error', message: 'Please enter a valid leverage multiplier between 1x and 100x.' });
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
        message: res.message || `Default allocation ($${alloc.toLocaleString()}) & leverage (${lev}x) updated successfully!`
      });
      portfolioQuery.refetch();
    } catch (err: any) {
      setParamFeedback({
        type: 'error',
        message: err.message || `Failed to sync parameters with AI trading engine.`
      });
    }
  };

  const handleSaveCurrency = async (newCode: string) => {
    setSelectedCurrency(newCode);
    setCurrency(newCode);
    try {
      await apiFetch('/api/auth/profile', {
        method: 'PUT',
        body: JSON.stringify({ currency: newCode })
      });
      setCurrencyFeedback({
        type: 'success',
        message: `Platform currency updated to ${newCode} (${SUPPORTED_CURRENCIES.find(c => c.code === newCode)?.symbol}) successfully!`
      });
    } catch (err: any) {
      setCurrencyFeedback({
        type: 'success',
        message: `Currency set to ${newCode} locally!`
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
      setFeedback({ type: "success", message: res.message || `Successfully deposited $${val.toLocaleString()} USDT into paper wallet!` });
      await queryClient.invalidateQueries({ queryKey: ["portfolio"] });
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
    setFeedback(null);
    try {
      const res = await withdrawVirtualFunds(val);
      setFeedback({ type: "success", message: res.message || `Successfully withdrawn $${val.toLocaleString()} USDT from paper wallet!` });
      await queryClient.invalidateQueries({ queryKey: ["portfolio"] });
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

  const handleResetPaperAccount = async () => {
    try {
      setIsResetting(true);
      setResetFeedback(null);
      const res = await resetPaperAccount();
      setResetFeedback({
        type: 'success',
        message: res.message || 'Full Platform Account successfully reset to $10,000 USDT.'
      });
      setShowResetModal(false);
      
      // Clear cached local items
      try {
        localStorage.removeItem('lumo_portfolio_cache');
        localStorage.removeItem('lumo_shadow_cache');
      } catch (e) {}

      // Invalidate all active UI queries
      await queryClient.invalidateQueries();
      portfolioQuery.refetch();
    } catch (err: any) {
      setResetFeedback({
        type: 'error',
        message: err.message || 'Failed to reset paper trading account.'
      });
    } finally {
      setIsResetting(false);
    }
  };

  const activeCurrencyConfig = SUPPORTED_CURRENCIES.find(c => c.code === selectedCurrency) || currentCurrency;
  const balanceUsd = currentPortfolio?.usdt_balance ?? 10000.0;
  const convertedBalance = balanceUsd * activeCurrencyConfig.rate;

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 selection:bg-cyan-500/30">
      <Sidebar collapsed={sidebarCollapsed} setCollapsed={setSidebarCollapsed} connectionState={stream.connectionState} />
      <div className={`flex-1 min-w-0 p-4 transition-all duration-300 lg:p-6 ${sidebarCollapsed ? "ml-20" : "ml-64"}`}>
        <Header portfolio={currentPortfolio} newsSentiment={newsQuery.data ?? null} latency={stream.latency} connectionState={stream.connectionState} onToggleBot={(enable) => toggleBot(enable)} onSelectStrategy={(s) => setStrategy(s)} />

        <main className="space-y-6">
          {/* Header title banner */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-4">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                <span>Platform Settings &amp; Multi-Currency Preferences</span>
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-mono">
                  {activeCurrencyConfig.flag} {activeCurrencyConfig.code}
                </span>
              </h1>
              <p className="text-xs text-slate-400 mt-1">
                Customize your display currency (INR ₹, USD $, EUR €, GBP £, etc.), theme palettes, execution parameters, and timezones
              </p>
            </div>
          </div>

          {/* Multi-Currency Selection Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5 shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  <Coins className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-md font-semibold text-slate-200">Global Display Currency (INR, USD, EUR, GBP, etc.)</h2>
                  <p className="text-xs text-slate-400 mt-0.5">
                    Select your preferred fiat currency for viewing portfolio equity, trade profits, and prices across all dashboards
                  </p>
                </div>
              </div>

              {/* Conversion Preview Badge */}
              <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono">
                <span className="text-slate-400">1 USD =</span>
                <span className="text-emerald-400 font-bold">
                  {activeCurrencyConfig.symbol} {activeCurrencyConfig.rate.toLocaleString()} {activeCurrencyConfig.code}
                </span>
              </div>
            </div>

            {currencyFeedback && (
              <div className="p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border bg-emerald-500/10 border-emerald-500/20 text-emerald-400">
                <CheckCircle2 className="w-4 h-4" />
                <span>{currencyFeedback.message}</span>
              </div>
            )}

            {/* Currency Grid Buttons */}
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-7 gap-2.5">
              {SUPPORTED_CURRENCIES.map((c) => {
                const isSelected = selectedCurrency === c.code;
                return (
                  <button
                    key={c.code}
                    type="button"
                    onClick={() => handleSaveCurrency(c.code)}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col gap-1 ${
                      isSelected
                        ? "bg-emerald-500/15 border-emerald-400 text-emerald-300 ring-1 ring-emerald-500/40 shadow-lg shadow-emerald-500/10"
                        : "bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-lg">{c.flag}</span>
                      <span className="font-bold text-xs font-mono">{c.symbol}</span>
                    </div>
                    <div className="font-bold text-xs text-white">{c.code}</div>
                    <div className="text-[10px] text-slate-400 truncate">{c.name}</div>
                  </button>
                );
              })}
            </div>

            {/* Live Balance Conversion Preview Box */}
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2 text-slate-300">
                <ArrowRightLeft className="w-4 h-4 text-cyan-400" />
                <span>Live Portfolio Value Conversion:</span>
              </div>
              <div className="flex items-center gap-2 font-mono">
                <span className="text-slate-400">${balanceUsd.toLocaleString(undefined, { minimumFractionDigits: 2 })} USDT =</span>
                <span className="text-emerald-400 font-bold text-sm">
                  {activeCurrencyConfig.symbol} {convertedBalance.toLocaleString(activeCurrencyConfig.locale, { minimumFractionDigits: 2, maximumFractionDigits: 2 })} {activeCurrencyConfig.code}
                </span>
              </div>
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
                        ? "bg-cyan-500/10 border-cyan-500 text-white shadow-lg shadow-cyan-500/10"
                        : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700 hover:text-slate-200"
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-3.5 h-3.5 rounded-full border border-slate-700" style={{ backgroundColor: th.accentColor }} />
                      <span className="text-xs font-semibold">{th.name}</span>
                    </div>
                    {isActive && <Check className="w-4 h-4 text-cyan-400" />}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Paper Trading Balance Controls */}
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
                    <p className="text-xs text-slate-400 mt-0.5">Add virtual margin capital to your paper wallet</p>
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
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:border-emerald-500/40 hover:text-emerald-400 transition-all cursor-pointer"
                    >
                      +${amt.toLocaleString()}
                    </button>
                  ))}
                </div>
                <button
                  type="submit"
                  disabled={isDepositing}
                  className="w-full py-2.5 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-100 font-semibold text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50 cursor-pointer"
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
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-slate-300 hover:border-rose-500/40 hover:text-rose-400 transition-all cursor-pointer"
                    >
                      -${amt.toLocaleString()}
                    </button>
                  ))}
                </div>
                <button
                  type="submit"
                  disabled={isWithdrawing}
                  className="w-full py-2.5 px-4 rounded-xl bg-rose-600 hover:bg-rose-500 text-slate-100 font-semibold text-sm flex items-center justify-center space-x-2 transition-all disabled:opacity-50 cursor-pointer"
                >
                  {isWithdrawing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <MinusCircle className="w-4 h-4" />}
                  <span>{isWithdrawing ? "Processing..." : "Withdraw Virtual Funds"}</span>
                </button>
              </form>
            </div>
          </div>

          {/* AI Execution & Risk Parameters */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  <Wallet className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-md font-semibold text-slate-200">Default Execution &amp; Risk Parameters</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Configure default capital allocation and leverage for manual &amp; automated trades</p>
                </div>
              </div>
              <button
                type="button"
                onClick={handleApplyParameters}
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:brightness-110 text-white font-bold rounded-xl text-xs uppercase tracking-wider transition shadow-lg shadow-cyan-500/20 flex items-center gap-1.5 cursor-pointer"
              >
                <Check className="w-4 h-4" />
                <span>Save Parameters</span>
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

          {/* Reset Paper Trading Account Card */}
          <div className="p-6 rounded-2xl bg-slate-900/60 border border-rose-900/30 space-y-5 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
              <div className="flex items-center gap-3">
                <div className="p-2.5 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
                  <RotateCcw className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-md font-semibold text-slate-200">Reset Paper Trading Account</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Wipe all simulated open positions, orders, trade history, and restore initial $10,000 USDT balance</p>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setShowResetModal(true)}
                className="px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/40 text-rose-300 font-bold rounded-xl text-xs uppercase tracking-wider transition shadow-lg shadow-rose-500/10 flex items-center gap-1.5 cursor-pointer"
              >
                <RotateCcw className="w-4 h-4" />
                <span>Reset Account</span>
              </button>
            </div>

            {resetFeedback && (
              <div className={`p-3 rounded-xl text-xs font-semibold flex items-center gap-2 border ${resetFeedback.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-rose-500/10 border-rose-500/20 text-rose-400'}`}>
                {resetFeedback.type === 'success' ? <CheckCircle2 className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
                <span>{resetFeedback.message}</span>
              </div>
            )}

            <p className="text-xs text-slate-500 leading-relaxed">
              Resetting will clear all stale or active simulated positions across Spot, Arbitrage, and Shadow trading engines. Your balance will be cleanly reset to $10,000.00 USDT.
            </p>
          </div>

        </main>

        <Footer dbSyncStatus={currentPortfolio?.database_sync_status} lastValidationTime={currentPortfolio?.last_validation_time} connectionState={stream.connectionState} />
      </div>

      {/* Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="max-w-md w-full rounded-2xl bg-slate-900 border border-slate-800 p-6 shadow-2xl space-y-4">
            <div className="flex items-center gap-3 text-rose-400">
              <ShieldAlert className="w-6 h-6 shrink-0" />
              <h3 className="text-base font-bold text-slate-100">Confirm Paper Account Reset</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Are you sure you want to reset your paper trading account? This will permanently delete all current open positions, active orders, and historical trade logs, and reset your wallet balance to <strong className="text-cyan-300">$10,000.00 USDT</strong>.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                type="button"
                onClick={() => setShowResetModal(false)}
                disabled={isResetting}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-300 transition"
              >
                Cancel
              </button>
              <button
                type="button"
                onClick={handleResetPaperAccount}
                disabled={isResetting}
                className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-xs font-bold text-white shadow-lg shadow-rose-600/30 transition flex items-center gap-2 disabled:opacity-50"
              >
                {isResetting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <RotateCcw className="w-4 h-4" />}
                <span>{isResetting ? "Resetting..." : "Yes, Reset Everything"}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
