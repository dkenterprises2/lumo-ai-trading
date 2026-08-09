"use client";

import React from "react";

export default function CollateralOptimizationPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Collateral & Margin Optimization</h1>
        <p className="text-gray-400 mt-1">Multi-venue collateral utilization ratio and excess reserve rebalancing.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Total Collateral Value</span>
            <div className="text-2xl font-bold text-white mt-1">$1,000,000.00</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Margin Utilized</span>
            <div className="text-2xl font-bold text-amber-400 mt-1">$400,000.00 (40%)</div>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-gray-400 font-medium">Free Collateral</span>
            <div className="text-2xl font-bold text-emerald-400 mt-1">$600,000.00</div>
          </div>
        </div>
      </div>
    </div>
  );
}
