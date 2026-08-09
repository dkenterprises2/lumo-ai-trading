"use client";

import React from "react";

export default function FootprintPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Footprint / Bid-Ask Delta</h1>
        <p className="text-gray-400 mt-1">Traded volume delta per price level and aggressive flow detection.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">CUMULATIVE DELTA</span>
            <h3 className="text-lg font-bold text-white mt-1">+42.50 BTC (Aggressive Buying Imbalance)</h3>
            <p className="text-xs text-gray-400">Ask Volume: 73.0 BTC | Bid Volume: 30.5 BTC</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">BUYING DELTA</span>
        </div>
      </div>
    </div>
  );
}
