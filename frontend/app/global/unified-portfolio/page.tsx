"use client";

import React from "react";

export default function UnifiedPortfolioPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Unified CeFi + DeFi Portfolio NAV</h1>
        <p className="text-gray-400 mt-1">Single global NAV aggregation across all exchanges, DeFi pools, & custody vaults.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">CeFi Portfolio NAV</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$2,100,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">DeFi Portfolio NAV</span>
            <div className="text-2xl font-bold text-indigo-400 mt-1">$850,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Total Global NAV</span>
            <div className="text-2xl font-bold text-white mt-1">$2,950,000.00</div>
          </div>
        </div>
      </div>
    </div>
  );
}
