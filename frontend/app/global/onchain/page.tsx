"use client";

import React from "react";

export default function OnChainAnalyticsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">On-Chain Analytics & Whale Monitoring</h1>
        <p className="text-gray-400 mt-1">Exchange inflow/outflow, stablecoin mints, & large whale movement alerts.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center mb-4">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">WHALE ALERT (WHALE-101)</span>
            <h3 className="text-lg font-bold text-white mt-1">2,500 BTC ($162,000,000 USD) Transfer</h3>
            <p className="text-xs text-gray-400">From: 0x111...aaa &rarr; To: Binance Hot Wallet</p>

          </div>
          <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">EXCHANGE INFLOW</span>
        </div>
      </div>
    </div>
  );
}
