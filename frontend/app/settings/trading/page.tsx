'use client';

import React, { useState, useEffect } from 'react';
import { 
  Sliders, 
  ShieldAlert, 
  CheckCircle2, 
  AlertTriangle, 
  Sparkles, 
  Zap, 
  Layers, 
  Clock, 
  DollarSign, 
  Percent,
  TrendingDown,
  RefreshCw,
  Save,
  Lock,
  Unlock,
  Check
} from 'lucide-react';

interface TradingPreferences {
  id: number;
  user_id: number;
  max_concurrent_trades: number;
  max_capital_per_trade_pct: number;
  daily_loss_limit_pct: number;
  symbol_cooldown_minutes: number;
  allowed_symbols: string[];
  plan_tier: string;
  plan_max_concurrent_trades: number;
}

const ALL_AVAILABLE_SYMBOLS = [
  'BTC/USDT',
  'ETH/USDT',
  'SOL/USDT',
  'AVAX/USDT',
  'BNB/USDT',
  'LINK/USDT',
  'DOT/USDT',
  'ADA/USDT',
  'NEAR/USDT',
  'MATIC/USDT',
  'XRP/USDT'
];

export default function TradingPreferencesPage() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  const [prefs, setPrefs] = useState<TradingPreferences>({
    id: 0,
    user_id: 1,
    max_concurrent_trades: 3,
    max_capital_per_trade_pct: 10.0,
    daily_loss_limit_pct: 5.0,
    symbol_cooldown_minutes: 15,
    allowed_symbols: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'AVAX/USDT'],
    plan_tier: 'PRO',
    plan_max_concurrent_trades: 10
  });

  useEffect(() => {
    fetchPreferences();
  }, []);

  const fetchPreferences = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/preferences/trading');
      if (res.ok) {
        const json = await res.json();
        if (json.status === 'success' && json.data) {
          setPrefs(json.data);
        }
      }
    } catch (err) {
      console.error('Failed to fetch trading preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setToast(null);
    try {
      const res = await fetch('/api/preferences/trading', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          max_concurrent_trades: prefs.max_concurrent_trades,
          max_capital_per_trade_pct: prefs.max_capital_per_trade_pct,
          daily_loss_limit_pct: prefs.daily_loss_limit_pct,
          symbol_cooldown_minutes: prefs.symbol_cooldown_minutes,
          allowed_symbols: prefs.allowed_symbols
        })
      });

      const json = await res.json();
      if (res.ok && json.status === 'success') {
        setPrefs(json.data);
        setToast({ message: 'Trading preferences saved successfully!', type: 'success' });
      } else {
        setToast({ message: json.detail || json.message || 'Failed to update preferences.', type: 'error' });
      }
    } catch (err: any) {
      setToast({ message: err.message || 'Network error while saving.', type: 'error' });
    } finally {
      setSaving(false);
      setTimeout(() => setToast(null), 5000);
    }
  };

  const toggleSymbol = (sym: string) => {
    if (prefs.allowed_symbols.includes(sym)) {
      if (prefs.allowed_symbols.length <= 1) {
        setToast({ message: 'At least one trading symbol must remain allowed.', type: 'error' });
        setTimeout(() => setToast(null), 3000);
        return;
      }
      setPrefs({
        ...prefs,
        allowed_symbols: prefs.allowed_symbols.filter(s => s !== sym)
      });
    } else {
      setPrefs({
        ...prefs,
        allowed_symbols: [...prefs.allowed_symbols, sym]
      });
    }
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <RefreshCw className="h-8 w-8 animate-spin text-cyan-400" />
      </div>
    );
  }

  const getTierColor = (tier: string) => {
    switch (tier.toUpperCase()) {
      case 'INSTITUTIONAL': return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'PRO': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
      case 'BASIC': return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      default: return 'bg-gray-500/20 text-gray-300 border-gray-500/40';
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-8 p-6 text-slate-100">
      {/* Header & Plan Banner */}
      <div className="flex flex-col justify-between gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-6 backdrop-blur-xl md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-cyan-500/10 p-2.5 text-cyan-400 border border-cyan-500/20">
              <Sliders className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Trading Risk Preferences</h1>
              <p className="text-sm text-slate-400">Configure position concurrency limits, trade sizing caps, and symbol whitelist.</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <span className={`inline-flex items-center gap-1.5 rounded-full border px-3.5 py-1 text-xs font-semibold uppercase tracking-wider ${getTierColor(prefs.plan_tier)}`}>
            <Sparkles className="h-3.5 w-3.5" />
            {prefs.plan_tier} Plan
          </span>

          <button
            onClick={handleSave}
            disabled={saving}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2.5 font-semibold text-white shadow-lg shadow-cyan-500/20 hover:from-cyan-400 hover:to-blue-500 disabled:opacity-50"
          >
            {saving ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
            Save Changes
          </button>
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className={`flex items-center gap-3 rounded-xl border p-4 text-sm font-medium transition-all ${
          toast.type === 'success' ? 'border-emerald-500/30 bg-emerald-500/10 text-emerald-300' : 'border-red-500/30 bg-red-500/10 text-red-300'
        }`}>
          {toast.type === 'success' ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
          {toast.message}
        </div>
      )}

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-2">
        {/* Left Column: Concurrency & Risk Limits */}
        <div className="space-y-6">
          {/* Max Concurrent Trades Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Layers className="h-5 w-5 text-cyan-400" />
                <h3 className="font-semibold text-white">Max Concurrent Trades</h3>
              </div>
              <span className="text-xl font-bold text-cyan-400">{prefs.max_concurrent_trades} Positions</span>
            </div>

            <p className="text-xs text-slate-400">
              Maximum simultaneous open positions allowed by auto-bot scanner.
            </p>

            <input
              type="range"
              min={1}
              max={prefs.plan_max_concurrent_trades}
              value={prefs.max_concurrent_trades}
              onChange={(e) => setPrefs({ ...prefs, max_concurrent_trades: Number(e.target.value) })}
              className="h-2 w-full cursor-pointer rounded-lg bg-slate-800 accent-cyan-400"
            />

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>1 Position</span>
              <span className="font-medium text-slate-300">Plan Tier Cap: {prefs.plan_max_concurrent_trades}</span>
            </div>
          </div>

          {/* Max Capital Per Trade (%) Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Percent className="h-5 w-5 text-blue-400" />
                <h3 className="font-semibold text-white">Max Capital Per Trade (%)</h3>
              </div>
              <span className="text-xl font-bold text-blue-400">{prefs.max_capital_per_trade_pct.toFixed(1)}%</span>
            </div>

            <p className="text-xs text-slate-400">
              Maximum portfolio balance percentage allocated to a single trade entry.
            </p>

            <input
              type="range"
              min={1.0}
              max={50.0}
              step={0.5}
              value={prefs.max_capital_per_trade_pct}
              onChange={(e) => setPrefs({ ...prefs, max_capital_per_trade_pct: Number(e.target.value) })}
              className="h-2 w-full cursor-pointer rounded-lg bg-slate-800 accent-blue-400"
            />

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>1.0%</span>
              <span>50.0%</span>
            </div>
          </div>

          {/* Daily Loss Limit (%) Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <TrendingDown className="h-5 w-5 text-rose-400" />
                <h3 className="font-semibold text-white">Daily Loss Circuit Breaker Limit</h3>
              </div>
              <span className="text-xl font-bold text-rose-400">{prefs.daily_loss_limit_pct.toFixed(1)}%</span>
            </div>

            <p className="text-xs text-slate-400">
              Automatic circuit breaker threshold. Halts all auto-bot trading if daily drawdown hits this level.
            </p>

            <input
              type="range"
              min={1.0}
              max={25.0}
              step={0.5}
              value={prefs.daily_loss_limit_pct}
              onChange={(e) => setPrefs({ ...prefs, daily_loss_limit_pct: Number(e.target.value) })}
              className="h-2 w-full cursor-pointer rounded-lg bg-slate-800 accent-rose-400"
            />

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>1.0%</span>
              <span>25.0%</span>
            </div>
          </div>
        </div>

        {/* Right Column: Symbol Cooldown & Whitelist */}
        <div className="space-y-6">
          {/* Symbol Cooldown Window Card */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Clock className="h-5 w-5 text-amber-400" />
                <h3 className="font-semibold text-white">Symbol Re-Entry Cooldown</h3>
              </div>
              <span className="text-xl font-bold text-amber-400">{prefs.symbol_cooldown_minutes} mins</span>
            </div>

            <p className="text-xs text-slate-400">
              Time delay required before re-opening a position on a symbol that was recently exited.
            </p>

            <input
              type="range"
              min={0}
              max={120}
              step={5}
              value={prefs.symbol_cooldown_minutes}
              onChange={(e) => setPrefs({ ...prefs, symbol_cooldown_minutes: Number(e.target.value) })}
              className="h-2 w-full cursor-pointer rounded-lg bg-slate-800 accent-amber-400"
            />

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>0 mins (No Delay)</span>
              <span>120 mins (2 Hours)</span>
            </div>
          </div>

          {/* Allowed Symbols Whitelist Grid */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <Zap className="h-5 w-5 text-emerald-400" />
                <h3 className="font-semibold text-white">Allowed Symbols Whitelist</h3>
              </div>
              <span className="text-xs font-semibold text-slate-400">{prefs.allowed_symbols.length} Selected</span>
            </div>

            <p className="text-xs text-slate-400">
              Only symbols enabled below will be evaluated for trading signals by the AI scanner engine.
            </p>

            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
              {ALL_AVAILABLE_SYMBOLS.map((sym) => {
                const isSelected = prefs.allowed_symbols.includes(sym);
                return (
                  <button
                    key={sym}
                    onClick={() => toggleSymbol(sym)}
                    className={`flex items-center justify-between rounded-xl border px-3.5 py-2.5 text-xs font-semibold transition-all ${
                      isSelected
                        ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300 shadow-md shadow-emerald-500/10'
                        : 'border-slate-800 bg-slate-950/40 text-slate-500 hover:border-slate-700 hover:text-slate-400'
                    }`}
                  >
                    <span>{sym}</span>
                    {isSelected ? <Check className="h-4 w-4 text-emerald-400" /> : <div className="h-4 w-4 rounded-full border border-slate-700" />}
                  </button>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
