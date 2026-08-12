'use client';

import React, { useState, useEffect } from 'react';
import { Crown, Zap, Shield, Sparkles, Sliders, Save, RefreshCw, ChevronDown, ChevronUp, AlertCircle, CheckCircle2, DollarSign, Percent, Lock, Activity } from 'lucide-react';
import { apiFetch } from '@/services/api';
import { UpgradePlanDialog } from './UpgradePlanDialog';

interface TradingPreferences {
  max_concurrent_trades: number;
  max_capital_per_trade_pct: number;
  daily_loss_limit_pct: number;
  symbol_cooldown_minutes: number;
  allowed_symbols: string[];
  default_allocation_usd: number;
  default_leverage: number;
}

interface SubscriptionLimitsCardProps {
  userPlan?: string;
  activePositionsCount?: number;
  onPreferencesUpdated?: () => void;
}

export const SubscriptionLimitsCard: React.FC<SubscriptionLimitsCardProps> = ({
  userPlan = 'INSTITUTIONAL',
  activePositionsCount = 0,
  onPreferencesUpdated
}) => {
  const [preferences, setPreferences] = useState<TradingPreferences>({
    max_concurrent_trades: 10,
    max_capital_per_trade_pct: 10,
    daily_loss_limit_pct: 5,
    symbol_cooldown_minutes: 10,
    allowed_symbols: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'AVAX/USDT'],
    default_allocation_usd: 1000,
    default_leverage: 1
  });

  const [loading, setLoading] = useState<boolean>(true);
  const [saving, setSaving] = useState<boolean>(false);
  const [saveSuccess, setSaveSuccess] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isUpgradeOpen, setIsUpgradeOpen] = useState<boolean>(false);
  const [isMobileExpanded, setIsMobileExpanded] = useState<boolean>(false);

  const fetchPreferences = async () => {
    try {
      setLoading(true);
      const res = await apiFetch('/api/preferences/trading');
      if (res.ok) {
        const data = await res.json();
        const prefs = data?.preferences || data;
        if (prefs && typeof prefs.max_concurrent_trades === 'number') {
          setPreferences({
            max_concurrent_trades: prefs.max_concurrent_trades ?? 10,
            max_capital_per_trade_pct: prefs.max_capital_per_trade_pct ?? 10,
            daily_loss_limit_pct: prefs.daily_loss_limit_pct ?? 5,
            symbol_cooldown_minutes: prefs.symbol_cooldown_minutes ?? 10,
            allowed_symbols: prefs.allowed_symbols || ['BTC/USDT', 'ETH/USDT'],
            default_allocation_usd: prefs.default_allocation_usd ?? 1000,
            default_leverage: prefs.default_leverage ?? 1
          });
        }
      }
    } catch (err: any) {
      console.warn('Failed to load trading preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPreferences();
  }, []);

  const handleSave = async () => {
    try {
      setSaving(true);
      setSaveSuccess(false);
      setErrorMessage(null);

      const res = await apiFetch('/api/preferences/trading', {
        method: 'PUT',
        body: JSON.stringify(preferences)
      });
      const data = await res.json();

      if (!res.ok) {
        const detail = data?.detail || `Backend error (${res.status}).`;
        if (res.status === 401) {
          setErrorMessage('Session expired. Please sign out and log back in.');
        } else {
          setErrorMessage(detail);
        }
        return;
      }

      const updated = data?.preferences || data;
      if (updated) {
        setPreferences({
          max_concurrent_trades: updated.max_concurrent_trades ?? preferences.max_concurrent_trades,
          max_capital_per_trade_pct: updated.max_capital_per_trade_pct ?? preferences.max_capital_per_trade_pct,
          daily_loss_limit_pct: updated.daily_loss_limit_pct ?? preferences.daily_loss_limit_pct,
          symbol_cooldown_minutes: updated.symbol_cooldown_minutes ?? preferences.symbol_cooldown_minutes,
          allowed_symbols: updated.allowed_symbols || preferences.allowed_symbols,
          default_allocation_usd: updated.default_allocation_usd ?? preferences.default_allocation_usd,
          default_leverage: updated.default_leverage ?? preferences.default_leverage
        });
      }

      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
      if (onPreferencesUpdated) onPreferencesUpdated();
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to update preferences.');
    } finally {
      setSaving(false);
    }
  };

  const getPlanBadgeConfig = (planStr: string) => {
    const p = (planStr || 'FREE').toUpperCase();
    if (p.includes('INSTITUTIONAL') || p.includes('ENTERPRISE')) {
      return {
        label: 'INSTITUTIONAL',
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 shadow-emerald-500/10',
        icon: Crown,
        iconClass: 'text-emerald-400'
      };
    }
    if (p.includes('PRO')) {
      return {
        label: 'PRO',
        badgeClass: 'bg-purple-500/10 text-purple-400 border-purple-500/30 shadow-purple-500/10',
        icon: Sparkles,
        iconClass: 'text-purple-400'
      };
    }
    if (p.includes('BASIC')) {
      return {
        label: 'BASIC',
        badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30 shadow-blue-500/10',
        icon: Zap,
        iconClass: 'text-blue-400'
      };
    }
    return {
      label: 'FREE',
      badgeClass: 'bg-slate-800/80 text-slate-400 border-slate-700',
      icon: Shield,
      iconClass: 'text-slate-400'
    };
  };

  const badgeConfig = getPlanBadgeConfig(userPlan);
  const BadgeIcon = badgeConfig.icon;

  const allowedTradesOptions = [1, 2, 3, 5, 10, 15, 20, 25, 30, 40, 50];

  const cooldownOptions = [0, 5, 10, 15, 30, 60];
  const leverageOptions = [1, 2, 3, 5, 10, 20, 50, 100];

  return (
    <>
      <div className="flex flex-col h-full bg-slate-900/90 border border-slate-800/90 rounded-3xl p-5 shadow-2xl backdrop-blur-xl relative overflow-hidden group">
        {/* Subtle Ambient Background Glow */}
        <div className="absolute -top-24 -right-24 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        {/* Card Header */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80 relative z-10">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-600/20 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10">
              <Sliders className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-extrabold text-sm text-white tracking-wide flex items-center gap-1.5">
                Subscription &amp; Trading Limits
              </h3>
              <p className="text-[11px] text-slate-400 font-medium">Institutional Risk Guards &amp; Sizing</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div
              className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full border text-[10px] font-extrabold tracking-widest uppercase shadow-sm ${badgeConfig.badgeClass}`}
            >
              <BadgeIcon className={`h-3.5 w-3.5 ${badgeConfig.iconClass}`} />
              <span>{badgeConfig.label}</span>
            </div>

            <button
              onClick={() => setIsUpgradeOpen(true)}
              className="px-3 py-1 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 text-xs font-bold border border-cyan-500/30 transition-all shadow-sm cursor-pointer"
            >
              Upgrade
            </button>
          </div>
        </div>

        {/* Mobile Accordion Toggle */}
        <div className="block md:hidden mb-3 relative z-10">
          <button
            onClick={() => setIsMobileExpanded(!isMobileExpanded)}
            className="w-full flex items-center justify-between p-3 rounded-2xl bg-slate-950/80 border border-slate-800 text-xs font-bold text-slate-200"
          >
            <span>
              {badgeConfig.label} • {preferences.max_concurrent_trades} Trades • ${preferences.default_allocation_usd.toLocaleString()} USDT • {preferences.default_leverage}x
            </span>
            {isMobileExpanded ? <ChevronUp className="h-4 w-4 text-cyan-400" /> : <ChevronDown className="h-4 w-4 text-cyan-400" />}
          </button>
        </div>

        {/* Main Controls Grid */}
        <div className={`space-y-4 relative z-10 ${isMobileExpanded ? 'block' : 'hidden md:block'}`}>
          {/* Active Capacity Bar */}
          <div className="p-3.5 rounded-2xl bg-slate-950/80 border border-slate-800/90 shadow-inner space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 font-semibold flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-cyan-400" />
                <span>Open Positions Capacity</span>
              </span>
              <span className="font-extrabold text-cyan-400 tracking-wide">
                {activePositionsCount} / {preferences.max_concurrent_trades} Positions
              </span>
            </div>
            <div className="w-full h-2.5 rounded-full bg-slate-900 overflow-hidden border border-slate-800/60">
              <div
                className="h-full bg-gradient-to-r from-cyan-400 via-blue-500 to-emerald-400 rounded-full transition-all duration-500 shadow-[0_0_12px_rgba(6,182,212,0.4)]"
                style={{
                  width: `${Math.min(100, (activePositionsCount / preferences.max_concurrent_trades) * 100)}%`
                }}
              />
            </div>
          </div>

          {/* Interactive Controls Grid (6 Fields) */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Max Concurrent Trades */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Max Concurrent Trades</span>
                <span className="text-cyan-400 font-extrabold">{preferences.max_concurrent_trades}</span>
              </label>
              <select
                value={preferences.max_concurrent_trades}
                onChange={(e) =>
                  setPreferences({ ...preferences, max_concurrent_trades: Number(e.target.value) })
                }
                className="w-full py-2 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/30 transition-all cursor-pointer"
              >
                {allowedTradesOptions.map((opt) => (
                  <option key={opt} value={opt} className="bg-slate-900 text-slate-100 font-bold">
                    {opt} {opt === 1 ? 'Position' : 'Positions'}
                  </option>
                ))}
              </select>
            </div>

            {/* Amount Per Trade ($ USDT) */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Amount Per Trade</span>
                <span className="text-emerald-400 font-extrabold">${preferences.default_allocation_usd.toLocaleString()}</span>
              </label>
              <div className="relative flex items-center">
                <span className="absolute left-3 text-slate-500 font-extrabold text-xs">$</span>
                <input
                  type="number"
                  min="10"
                  max="100000"
                  step="100"
                  value={preferences.default_allocation_usd}
                  onChange={(e) =>
                    setPreferences({ ...preferences, default_allocation_usd: Number(e.target.value) })
                  }
                  className="w-full py-2 pl-7 pr-14 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono font-bold text-slate-100 focus:outline-none focus:border-emerald-500/80 focus:ring-1 focus:ring-emerald-500/30 transition-all"
                  placeholder="1000"
                />
                <span className="absolute right-3 text-[10px] font-bold text-slate-500 tracking-wider">USDT</span>
              </div>
            </div>

            {/* Leverage Multiplier (1x - 100x) */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Leverage Multiplier</span>
                <span className="text-amber-400 font-extrabold">{preferences.default_leverage}x</span>
              </label>
              <select
                value={preferences.default_leverage}
                onChange={(e) =>
                  setPreferences({ ...preferences, default_leverage: Number(e.target.value) })
                }
                className="w-full py-2 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold text-slate-100 focus:outline-none focus:border-amber-500/80 focus:ring-1 focus:ring-amber-500/30 transition-all cursor-pointer"
              >
                {leverageOptions.map((opt) => (
                  <option key={opt} value={opt} className="bg-slate-900 text-slate-100 font-bold">
                    {opt}x Leverage
                  </option>
                ))}
              </select>
            </div>

            {/* Capital Per Trade % */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Capital per Trade (%)</span>
                <span className="text-purple-400 font-extrabold">{preferences.max_capital_per_trade_pct}%</span>
              </label>
              <input
                type="range"
                min="1"
                max="25"
                step="1"
                value={preferences.max_capital_per_trade_pct}
                onChange={(e) =>
                  setPreferences({ ...preferences, max_capital_per_trade_pct: Number(e.target.value) })
                }
                className="w-full accent-purple-500 bg-slate-900 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Daily Loss Limit % */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Daily Loss Limit (%)</span>
                <span className="text-rose-400 font-extrabold">{preferences.daily_loss_limit_pct}%</span>
              </label>
              <input
                type="range"
                min="1"
                max="20"
                step="1"
                value={preferences.daily_loss_limit_pct}
                onChange={(e) =>
                  setPreferences({ ...preferences, daily_loss_limit_pct: Number(e.target.value) })
                }
                className="w-full accent-rose-500 bg-slate-900 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Cooldown Minutes */}
            <div className="p-3.5 rounded-2xl bg-slate-950/70 hover:bg-slate-950/90 border border-slate-800/80 hover:border-slate-700/80 space-y-2 transition-all duration-200 shadow-md">
              <label className="text-[11px] font-bold text-slate-300 uppercase tracking-wider flex justify-between items-center">
                <span>Symbol Cooldown</span>
                <span className="text-cyan-400 font-extrabold">{preferences.symbol_cooldown_minutes}m</span>
              </label>
              <select
                value={preferences.symbol_cooldown_minutes}
                onChange={(e) =>
                  setPreferences({ ...preferences, symbol_cooldown_minutes: Number(e.target.value) })
                }
                className="w-full py-2 px-3 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold text-slate-100 focus:outline-none focus:border-cyan-500/80 focus:ring-1 focus:ring-cyan-500/30 transition-all cursor-pointer"
              >
                {cooldownOptions.map((opt) => (
                  <option key={opt} value={opt} className="bg-slate-900 text-slate-100 font-bold">
                    {opt === 0 ? 'Disabled (0 mins)' : `${opt} Minutes`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Feedback Messages */}
          {errorMessage && (
            <div className="flex items-center gap-2 p-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold shadow-md">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {saveSuccess && (
            <div className="flex items-center gap-2 p-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold shadow-md">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Trading preferences updated and applied to Bot Engine!</span>
            </div>
          )}

          {/* Save Changes CTA Button */}
          <div className="pt-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full flex items-center justify-center gap-2.5 py-3.5 px-5 rounded-2xl bg-gradient-to-r from-cyan-500 via-blue-600 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 active:scale-[0.99] text-white font-extrabold text-xs uppercase tracking-wider shadow-lg shadow-cyan-500/25 border border-cyan-400/30 transition-all duration-200 cursor-pointer disabled:opacity-50"
            >
              {saving ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Syncing Parameters...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Upgrade Plan Modal */}
      <UpgradePlanDialog
        isOpen={isUpgradeOpen}
        onClose={() => setIsUpgradeOpen(false)}
        currentPlan={userPlan}
      />
    </>
  );
};
