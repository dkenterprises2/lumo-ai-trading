"use client";

import React from "react";
import Link from "next/link";

export default function QuantResearchOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Hedge-Fund Grade Quantitative Research</h1>
        <p className="text-gray-400 mt-1">Factor research, statistical arbitrage, Monte Carlo simulation, & Bayesian tuning.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/research/factors" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Factor Engine</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">4 Categories</div>
          <div className="text-xs text-gray-500 mt-1">Momentum, Value, Vol, Liquidity</div>
        </Link>

        <Link href="/research/stat-arb" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Statistical Arbitrage</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">Engle-Granger</div>
          <div className="text-xs text-gray-500 mt-1">Cointegrated Pairs Scanning</div>
        </Link>

        <Link href="/research/monte-carlo" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Monte Carlo Engine</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">1,000 Runs</div>
          <div className="text-xs text-gray-500 mt-1">VaR / CVaR 95% Distribution</div>
        </Link>

        <Link href="/research/walk-forward" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Walk-Forward Opt</div>
          <div className="text-2xl font-bold text-white mt-1">OOS Sharpe 2.12</div>
          <div className="text-xs text-emerald-400 mt-1">86.5% Efficiency Ratio</div>
        </Link>
      </div>
    </div>
  );
}
