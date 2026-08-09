"use client";

import React from "react";

export default function StatArbPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Statistical Arbitrage & Pairs Trading</h1>
        <p className="text-gray-400 mt-1">Engle-Granger cointegration scanner, hedge ratio estimation, and z-score signals.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">COINTEGRATED PAIR</span>
            <h3 className="text-lg font-bold text-white mt-1">BTC/USDT vs ETH/USDT</h3>
            <p className="text-xs text-gray-400">Hedge Ratio: 15.2 | Z-Score: +2.15 | p-value: 0.018</p>
          </div>
          <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">SHORT SPREAD</span>
        </div>
      </div>
    </div>
  );
}
