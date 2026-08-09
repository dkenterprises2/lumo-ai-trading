"use client";

import React from "react";

export default function OrderBookL2Page() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Level-2 Order Book Stream</h1>
        <p className="text-gray-400 mt-1">Real-time bids, asks, and incremental depth resynchronization.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-emerald-400 mb-4">Bids (Buying Liquidity)</h2>
          <div className="space-y-2 font-mono text-xs text-gray-300">
            <div className="flex justify-between bg-emerald-950/40 p-2 rounded"><span>$64,810.00</span><span>1.50 BTC</span></div>
            <div className="flex justify-between bg-emerald-950/30 p-2 rounded"><span>$64,809.50</span><span>2.20 BTC</span></div>
          </div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h2 className="text-lg font-bold text-red-400 mb-4">Asks (Selling Liquidity)</h2>
          <div className="space-y-2 font-mono text-xs text-gray-300">
            <div className="flex justify-between bg-red-950/40 p-2 rounded"><span>$64,810.50</span><span>1.20 BTC</span></div>
            <div className="flex justify-between bg-red-950/30 p-2 rounded"><span>$64,811.00</span><span>3.40 BTC</span></div>
          </div>
        </div>
      </div>
    </div>
  );
}
