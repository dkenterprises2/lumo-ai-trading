"use client";

import React from "react";
import Link from "next/link";
import { ShieldAlert, Crosshair, Cpu, ArrowLeftRight, Newspaper, ArrowRight, Zap, Sparkles, Flame } from "lucide-react";

export interface InstitutionalModule {
  id: string;
  title: string;
  route: string;
  status: "LIVE" | "READY" | "BETA";
  statusColor: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  accentColor: string;
  gradient: string;
}

const INSTITUTIONAL_MODULES: InstitutionalModule[] = [
  {
    id: "spot-research",
    title: "Spot & Meme Coin Research",
    route: "/scanner",
    status: "LIVE",
    statusColor: "bg-cyan-500/20 text-cyan-300 border-cyan-500/40",
    description: "Autonomous new coin & meme token discovery across Binance & DEX streams with 8-vector risk scoring and paper validation.",
    icon: Sparkles,
    accentColor: "text-cyan-400",
    gradient: "from-cyan-500/10 via-slate-900 to-slate-900 hover:border-cyan-500/50"
  },
  {
    id: "risk",
    title: "Portfolio Risk Intelligence",
    route: "/risk",
    status: "READY",
    statusColor: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
    description: "Institutional risk analytics, Value at Risk (VaR), stress testing, drawdown budget & correlation filters.",
    icon: ShieldAlert,
    accentColor: "text-indigo-400",
    gradient: "from-indigo-500/10 via-slate-900 to-slate-900 hover:border-indigo-500/50"
  },
  {
    id: "execution",
    title: "OMS / EMS Execution Stack",
    route: "/execution",
    status: "READY",
    statusColor: "bg-purple-500/20 text-purple-400 border-purple-500/30",
    description: "Smart Order Router (SOR), TWAP, VWAP, POV & Iceberg algo execution across multi-broker venue gateways.",
    icon: Crosshair,
    accentColor: "text-purple-400",
    gradient: "from-purple-500/10 via-slate-900 to-slate-900 hover:border-purple-500/50"
  },
  {
    id: "shadow",
    title: "Shadow Trading & Market Replay",
    route: "/shadow",
    status: "READY",
    statusColor: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
    description: "Zero-risk institutional paper engine with orderbook tick replay, realistic slippage & fill quality analytics.",
    icon: Cpu,
    accentColor: "text-cyan-400",
    gradient: "from-cyan-500/10 via-slate-900 to-slate-900 hover:border-cyan-500/50"
  },
  {
    id: "arbitrage",
    title: "Cross-Exchange Arbitrage",
    route: "/arbitrage",
    status: "READY",
    statusColor: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    description: "Spatial price spread detector, triangular arbitrage, funding rate collector & basis spread tracking engine.",
    icon: ArrowLeftRight,
    accentColor: "text-amber-400",
    gradient: "from-amber-500/10 via-slate-900 to-slate-900 hover:border-amber-500/50"
  },
  {
    id: "news",
    title: "AI News & Event Intelligence",
    route: "/news",
    status: "LIVE",
    statusColor: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
    description: "Real-time crypto event detection, NLP sentiment scoring, whale transfers & influencer sentiment engine.",
    icon: Newspaper,
    accentColor: "text-emerald-400",
    gradient: "from-emerald-500/10 via-slate-900 to-slate-900 hover:border-emerald-500/50"
  }
];

export function InstitutionalModulesGrid() {
  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2">
            <Zap className="w-5 h-5 text-cyan-400" />
            Advanced Trading Intelligence
          </h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Production-grade quantitative risk, algorithmic execution, shadow replay, cross-exchange arbitrage &amp; news NLP engines
          </p>
        </div>
        <span className="text-[10px] font-mono font-extrabold px-2.5 py-1 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
          5 / 5 ACTIVE
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
        {INSTITUTIONAL_MODULES.map((mod) => {
          const Icon = mod.icon;
          return (
            <div
              key={mod.id}
              className={`group relative flex flex-col justify-between p-5 rounded-2xl bg-gradient-to-b ${mod.gradient} border border-slate-800/80 shadow-xl backdrop-blur-xl transition-all duration-300 hover:-translate-y-1`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2.5 rounded-xl bg-slate-950 border border-slate-800 ${mod.accentColor} shadow-inner`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded-md border ${mod.statusColor}`}>
                    {mod.status}
                  </span>
                </div>

                <h3 className="text-sm font-bold text-white group-hover:text-cyan-300 transition-colors">
                  {mod.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed line-clamp-3">
                  {mod.description}
                </p>
              </div>

              <div className="mt-5 pt-3 border-t border-slate-800/60 flex items-center justify-between">
                <span className="text-[10px] text-slate-500 font-mono">Route: {mod.route}</span>
                <Link
                  href={mod.route}
                  className="inline-flex items-center gap-1 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors"
                >
                  Open <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
