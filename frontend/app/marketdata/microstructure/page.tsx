"use client";

import React from "react";

export default function MicrostructurePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Microstructure Alpha & Spoofing Alerts</h1>
        <p className="text-gray-400 mt-1">Short-term order book momentum signals and spoofing/layering detection queue.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center mb-4">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">ALPHA SIGNAL</span>
            <h3 className="text-lg font-bold text-white mt-1">SHORT_TERM_BULLISH (82% Confidence)</h3>
            <p className="text-xs text-gray-400">Horizon: 30 Seconds | Imbalance: 0.68</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">ACTIVE SIGNAL</span>
        </div>

        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">SPOOFING ALERT</span>
            <h3 className="text-base font-semibold text-white mt-1">Large Non-Executing Bid Cancel ($64,805.00)</h3>
            <p className="text-xs text-gray-400">Quantity: 25.0 BTC | Severity: HIGH</p>
          </div>
          <span className="text-xs bg-red-950 text-red-300 border border-red-700 px-3 py-1 rounded">HIGH SEVERITY</span>
        </div>
      </div>
    </div>
  );
}
