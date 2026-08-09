"use client";

import React from "react";

export default function MarketplaceReputationPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Strategy Reputation & Performance Badges</h1>
        <p className="text-gray-400 mt-1">Audit verification badges, Sharpe stability scores, & out-of-sample track record.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">REPUTATION SCORE: 98/100</span>
            <h3 className="text-lg font-bold text-white mt-1">quant_research_team (Verified Publisher)</h3>
            <p className="text-xs text-gray-400">Total Published: 4 Strategies | Average Sharpe: 2.32</p>
          </div>
          <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">PLATINUM PUBLISHER</span>
        </div>
      </div>
    </div>
  );
}
