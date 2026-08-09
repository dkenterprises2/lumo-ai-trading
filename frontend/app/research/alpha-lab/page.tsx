"use client";

import React from "react";

export default function ResearchAlphaLabPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Alpha Discovery Lab</h1>
        <p className="text-gray-400 mt-1">Alpha signal candidate funnel, validation metrics, & shadow deployment promotion.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">ALPHA: DOM Imbalance Alpha</span>
            <h3 className="text-lg font-bold text-white mt-1">Orderbook Level-2 Imbalance Signal</h3>
            <p className="text-xs text-gray-400">Information Coefficient (IC): 0.088 | Sharpe: 2.45</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">SHADOW APPROVED</span>
        </div>
      </div>
    </div>
  );
}
