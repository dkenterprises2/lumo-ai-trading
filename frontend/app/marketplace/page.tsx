"use client";

import React from "react";
import Link from "next/link";

export default function InstitutionalStrategyMarketplacePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Strategy Marketplace & Licensing</h1>
        <p className="text-gray-400 mt-1">Discover, license, and publish institutional alpha strategies with verified performance badges.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl space-y-2">
          <div className="flex justify-between items-center">
            <span className="font-mono text-xs text-indigo-400 font-bold">ALPHA_MOMENTUM_V12</span>
            <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CERTIFIED</span>
          </div>
          <h3 className="text-xl font-bold text-white mt-1">Institutional Momentum Alpha</h3>
          <p className="text-xs text-gray-400">Sharpe: 2.14 | Max DD: 11% | Robustness: 87%</p>
          <button className="w-full mt-2 bg-indigo-600 hover:bg-indigo-500 text-white py-2 rounded text-xs font-bold">License Strategy</button>
        </div>
      </div>
    </div>
  );
}
