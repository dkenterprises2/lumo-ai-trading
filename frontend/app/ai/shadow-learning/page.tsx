"use client";

import React from "react";

export default function AIShadowLearningPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Shadow-Learning Mode</h1>
        <p className="text-gray-400 mt-1">Counterfactual paper-trading observation without live execution access.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">SHADOW-TRADE-101</span>
            <h3 className="text-lg font-bold text-white mt-1">Hypothetical Action: BUY_SMALL @ $64,810.00</h3>
            <p className="text-xs text-gray-400">Real Market Outcome PnL: +$125.40</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">RECORDED (NO LIVE ORDER)</span>
        </div>
      </div>
    </div>
  );
}
