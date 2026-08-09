"use client";

import React from "react";

export default function ResearchFactorsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Factor Research Library</h1>
        <p className="text-gray-400 mt-1">Momentum, Parkinson volatility, Amihud illiquidity, & Crypto on-chain factor suites.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-indigo-400 font-bold">MOMENTUM_20D</span>
          <h3 className="text-lg font-bold text-white">20-Day Risk-Adjusted Momentum</h3>
          <p className="text-xs text-emerald-400">IC Mean: 0.082 | Sharpe: 2.15</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <span className="font-mono text-xs text-amber-400 font-bold">EXCHANGE_NETFLOW</span>
          <h3 className="text-lg font-bold text-white">Crypto On-Chain Netflow</h3>
          <p className="text-xs text-emerald-400">IC Mean: 0.091 | Sharpe: 2.68</p>
        </div>
      </div>
    </div>
  );
}
