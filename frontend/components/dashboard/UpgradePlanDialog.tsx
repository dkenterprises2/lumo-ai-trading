'use client';

import React from 'react';
import { Crown, Check, X, Shield, Zap, Sparkles, Building2 } from 'lucide-react';

interface UpgradePlanDialogProps {
  isOpen: boolean;
  onClose: () => void;
  currentPlan?: string;
}

export const UpgradePlanDialog: React.FC<UpgradePlanDialogProps> = ({
  isOpen,
  onClose,
  currentPlan = 'INSTITUTIONAL'
}) => {
  if (!isOpen) return null;

  const normalizedPlan = (currentPlan || 'FREE').toUpperCase();

  const plans = [
    {
      name: 'FREE',
      title: 'Free Tier',
      price: '$0',
      badgeColor: 'bg-slate-800 text-slate-400 border-slate-700',
      icon: Shield,
      maxTrades: 2,
      maxRisk: '2%',
      cooldown: '30 mins',
      features: ['2 Concurrent Trades', '1x Leverage', 'Standard Support', 'Basic Bot Signals']
    },
    {
      name: 'BASIC',
      title: 'Basic Plan',
      price: '$49/mo',
      badgeColor: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      icon: Zap,
      maxTrades: 5,
      maxRisk: '5%',
      cooldown: '15 mins',
      features: ['5 Concurrent Trades', 'up to 5x Leverage', 'Priority Execution', 'Standard Risk Guard']
    },
    {
      name: 'PRO',
      title: 'Pro Trader',
      price: '$199/mo',
      badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      icon: Sparkles,
      maxTrades: 10,
      maxRisk: '15%',
      cooldown: '5 mins',
      features: ['10 Concurrent Trades', 'up to 20x Leverage', 'AI Copilot Assistant', 'Custom Webhooks']
    },
    {
      name: 'INSTITUTIONAL',
      title: 'Enterprise / Institutional',
      price: 'Custom',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      icon: Crown,
      maxTrades: 50,
      maxRisk: '25%',
      cooldown: '0 mins',
      features: ['50 Concurrent Trades', 'Unlimited Leverage', 'Multi-Portfolio Engine', 'Institutional Sor & TCA', '24/7 Dedicated Quant Support']
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="relative w-full max-w-4xl bg-slate-900 border border-slate-800 rounded-3xl shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-800/80 bg-slate-900/60">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 text-white shadow-lg shadow-cyan-500/20">
              <Building2 className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
                Subscription & Plan Upgrade Matrix
              </h2>
              <p className="text-xs text-slate-400">
                Unlock institutional execution limits, higher concurrent positions, and dedicated AI Copilot controls.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Plans Grid */}
        <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 max-h-[70vh] overflow-y-auto">
          {plans.map((p) => {
            const isCurrent = normalizedPlan.includes(p.name);
            const Icon = p.icon;

            return (
              <div
                key={p.name}
                className={`relative flex flex-col justify-between p-5 rounded-2xl border transition-all ${
                  isCurrent
                    ? 'bg-slate-800/80 border-cyan-500/50 shadow-xl shadow-cyan-500/10 ring-1 ring-cyan-500/30'
                    : 'bg-slate-900/40 border-slate-800/80 hover:border-slate-700'
                }`}
              >
                {isCurrent && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 rounded-full bg-cyan-500 text-[10px] font-bold tracking-wider text-slate-950 uppercase shadow-md shadow-cyan-500/30">
                    Current Active Plan
                  </div>
                )}

                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className={`p-2.5 rounded-xl ${p.badgeColor}`}>
                      <Icon className="h-5 w-5" />
                    </div>
                    <span className="text-sm font-bold text-slate-200">{p.price}</span>
                  </div>

                  <h3 className="font-bold text-slate-100 text-base">{p.title}</h3>
                  <div className="mt-2 mb-4 p-2.5 rounded-xl bg-slate-950/60 border border-slate-800/60 space-y-1 text-xs">
                    <div className="flex justify-between text-slate-300">
                      <span className="text-slate-500">Max Trades:</span>
                      <span className="font-bold text-cyan-400">{p.maxTrades} Positions</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span className="text-slate-500">Max Risk / Trade:</span>
                      <span className="font-bold text-purple-400">{p.maxRisk}</span>
                    </div>
                    <div className="flex justify-between text-slate-300">
                      <span className="text-slate-500">Cooldown:</span>
                      <span className="font-bold text-emerald-400">{p.cooldown}</span>
                    </div>
                  </div>

                  <ul className="space-y-2 mb-6">
                    {p.features.map((feat, idx) => (
                      <li key={idx} className="flex items-center gap-2 text-xs text-slate-300">
                        <Check className="h-3.5 w-3.5 text-cyan-400 shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  {isCurrent ? (
                    <button
                      disabled
                      className="w-full py-2.5 px-4 rounded-xl bg-slate-800 border border-slate-700 text-xs font-bold text-slate-400 cursor-default"
                    >
                      Active Plan
                    </button>
                  ) : (
                    <a
                      href="mailto:admin@lumo.trade?subject=Request%20Plan%20Upgrade"
                      className="w-full inline-flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 text-xs font-bold text-white shadow-lg shadow-cyan-500/20 hover:brightness-110 transition"
                    >
                      Upgrade Plan
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="p-6 border-t border-slate-800/80 bg-slate-900/60 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-slate-400 text-center sm:text-left">
            Need custom API rate limits, private VPC execution nodes, or white-label SaaS access?
          </p>
          <a
            href="mailto:admin@lumo.trade?subject=Enterprise%20Subscription%20Inquiry"
            className="w-full sm:w-auto px-6 py-2.5 rounded-xl bg-slate-800 border border-slate-700 hover:bg-slate-700 text-xs font-bold text-slate-200 transition text-center shrink-0"
          >
            Contact Administrator for Upgrade
          </a>
        </div>
      </div>
    </div>
  );
};
