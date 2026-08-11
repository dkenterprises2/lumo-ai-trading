'use client';

import React, { useState, useEffect } from 'react';
import { Crown, Zap, Shield, Sparkles, Sliders, Save, RefreshCw, ChevronDown, ChevronUp, AlertCircle, CheckCircle2 } from 'lucide-react';
import { apiFetch } from '@/services/api';
import { UpgradePlanDialog } from './UpgradePlanDialog';

interface TradingPreferences {
  max_concurrent_trades: number;
  max_capital_per_trade_pct: number;
  daily_loss_limit_pct: number;
  symbol_cooldown_minutes: number;
  allowed_symbols: string[];
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
    allowed_symbols: ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'AVAX/USDT']
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
      const data = await res.json();
      const prefs = data?.preferences || data;
      if (prefs) {
        setPreferences({
          max_concurrent_trades: prefs.max_concurrent_trades ?? 10,
          max_capital_per_trade_pct: prefs.max_capital_per_trade_pct ?? 10,
          daily_loss_limit_pct: prefs.daily_loss_limit_pct ?? 5,
          symbol_cooldown_minutes: prefs.symbol_cooldown_minutes ?? 10,
          allowed_symbols: prefs.allowed_symbols || ['BTC/USDT', 'ETH/USDT']
        });
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

      const updated = data?.preferences || data;
      if (updated) {
        setPreferences({
          max_concurrent_trades: updated.max_concurrent_trades,
          max_capital_per_trade_pct: updated.max_capital_per_trade_pct,
          daily_loss_limit_pct: updated.daily_loss_limit_pct,
          symbol_cooldown_minutes: updated.symbol_cooldown_minutes,
          allowed_symbols: updated.allowed_symbols || preferences.allowed_symbols
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
        badgeClass: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        icon: Crown,
        iconClass: 'text-emerald-400'
      };
    }
    if (p.includes('PRO')) {
      return {
        label: 'PRO',
        badgeClass: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
        icon: Sparkles,
        iconClass: 'text-purple-400'
      };
    }
    if (p.includes('BASIC')) {
      return {
        label: 'BASIC',
        badgeClass: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        icon: Zap,
        iconClass: 'text-blue-400'
      };
    }
    return {
      label: 'FREE',
      badgeClass: 'bg-slate-800 text-slate-400 border-slate-700',
      icon: Shield,
      iconClass: 'text-slate-400'
    };
  };

  const badgeConfig = getPlanBadgeConfig(userPlan);
  const BadgeIcon = badgeConfig.icon;

  const allowedTradesOptions = [1, 2, 3, 5, 10, 20, 50];
  const cooldownOptions = [0, 5, 10, 15, 30, 60];

  return (
    <>
      <div className="flex flex-col h-full bg-slate-900/60 border border-slate-800/80 rounded-3xl p-5 shadow-xl backdrop-blur-md">
        {/* Header */}
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-800/80">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Sliders className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-100">Subscription & Trading Limits</h3>
              <p className="text-[11px] text-slate-400">Institutional Execution Guards</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <div
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[11px] font-bold tracking-wider uppercase ${badgeConfig.badgeClass}`}
            >
              <BadgeIcon className={`h-3.5 w-3.5 ${badgeConfig.iconClass}`} />
              <span>{badgeConfig.label}</span>
            </div>

            <button
              onClick={() => setIsUpgradeOpen(true)}
              className="px-2.5 py-1 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition"
            >
              Upgrade
            </button>
          </div>
        </div>

        {/* Mobile Accordion Summary */}
        <div className="block md:hidden mb-3">
          <button
            onClick={() => setIsMobileExpanded(!isMobileExpanded)}
            className="w-full flex items-center justify-between p-3 rounded-2xl bg-slate-950/60 border border-slate-800 text-xs font-semibold text-slate-300"
          >
            <span>
              {badgeConfig.label} • {preferences.max_concurrent_trades} Trades • {preferences.max_capital_per_trade_pct}% Risk
            </span>
            {isMobileExpanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </button>
        </div>

        {/* Main Controls Panel (Responsive: Always visible on desktop, toggleable on mobile) */}
        <div className={`space-y-4 ${isMobileExpanded ? 'block' : 'hidden md:block'}`}>
          {/* Active Capacity Bar */}
          <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800/80 space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="text-slate-400 font-medium">Open Positions Capacity</span>
              <span className="font-bold text-cyan-400">
                {activePositionsCount} / {preferences.max_concurrent_trades} Positions
              </span>
            </div>
            <div className="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-cyan-500 to-emerald-400 rounded-full transition-all duration-500"
                style={{
                  width: `${Math.min(100, (activePositionsCount / preferences.max_concurrent_trades) * 100)}%`
                }}
              />
            </div>
          </div>

          {/* Interactive Controls */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {/* Max Concurrent Trades */}
            <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-400 flex justify-between">
                <span>Max Concurrent Trades</span>
                <span className="text-cyan-400 font-bold">{preferences.max_concurrent_trades}</span>
              </label>
              <select
                value={preferences.max_concurrent_trades}
                onChange={(e) =>
                  setPreferences({ ...preferences, max_concurrent_trades: Number(e.target.value) })
                }
                className="w-full py-1.5 px-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 focus:outline-none focus:border-cyan-500/50"
              >
                {allowedTradesOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt} {opt === 1 ? 'Position' : 'Positions'}
                  </option>
                ))}
              </select>
            </div>

            {/* Capital Per Trade % */}
            <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-400 flex justify-between">
                <span>Capital per Trade</span>
                <span className="text-purple-400 font-bold">{preferences.max_capital_per_trade_pct}%</span>
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
                className="w-full accent-purple-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Daily Loss Limit % */}
            <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-400 flex justify-between">
                <span>Daily Loss Limit</span>
                <span className="text-rose-400 font-bold">{preferences.daily_loss_limit_pct}%</span>
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
                className="w-full accent-rose-500 bg-slate-800 h-1.5 rounded-lg appearance-none cursor-pointer"
              />
            </div>

            {/* Cooldown Minutes */}
            <div className="p-3 rounded-2xl bg-slate-950/40 border border-slate-800/60 space-y-1.5">
              <label className="text-[11px] font-semibold text-slate-400 flex justify-between">
                <span>Symbol Cooldown</span>
                <span className="text-emerald-400 font-bold">{preferences.symbol_cooldown_minutes}m</span>
              </label>
              <select
                value={preferences.symbol_cooldown_minutes}
                onChange={(e) =>
                  setPreferences({ ...preferences, symbol_cooldown_minutes: Number(e.target.value) })
                }
                className="w-full py-1.5 px-2.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-semibold text-slate-200 focus:outline-none focus:border-cyan-500/50"
              >
                {cooldownOptions.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt === 0 ? 'Disabled (0 mins)' : `${opt} Minutes`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Feedback messages */}
          {errorMessage && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {saveSuccess && (
            <div className="flex items-center gap-2 p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
              <CheckCircle2 className="h-4 w-4 shrink-0" />
              <span>Trading preferences updated and applied to Bot Engine!</span>
            </div>
          )}

          {/* Save Button */}
          <div className="pt-1">
            <button
              onClick={handleSave}
              disabled={saving}
              className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:brightness-110 text-white font-bold text-xs shadow-lg shadow-cyan-500/20 transition-all disabled:opacity-50"
            >
              {saving ? (
                <>
                  <RefreshCw className="h-4 w-4 animate-spin" />
                  <span>Saving Changes...</span>
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
