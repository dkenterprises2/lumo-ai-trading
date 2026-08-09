"use client";

import React from "react";

export default function MonteCarloPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Monte Carlo Simulation Engine</h1>
        <p className="text-gray-400 mt-1">Equity curve fan charts, bootstrapped returns, VaR / CVaR, & Risk-of-Ruin.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">95th Percentile Equity</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">$142,800</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">5th Percentile Equity (Worst)</div>
          <div className="text-2xl font-bold text-red-400 mt-1">$91,200</div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Conditional VaR (CVaR 95%)</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">11.4%</div>
        </div>
      </div>
    </div>
  );
}
