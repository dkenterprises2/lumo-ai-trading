"use client";

import React from "react";

export default function GlobalRiskPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Global Cross-Asset Risk Aggregation</h1>
        <p className="text-gray-400 mt-1">Gross/Net exposures, cross-asset VaR 95%, leverage ratios, & stress scenario tests.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Gross Exposure</span>
            <div className="text-2xl font-bold text-white mt-1">$4,500,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Net Exposure</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$2,100,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Leverage Ratio</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">1.45x</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Cross-Asset VaR 95%</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">$85,000.00</div>
          </div>
        </div>
      </div>
    </div>
  );
}
