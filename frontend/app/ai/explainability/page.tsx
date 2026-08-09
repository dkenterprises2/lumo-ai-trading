"use client";

import React from "react";

export default function AIExplainabilityPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Explainability & Feature Importance</h1>
        <p className="text-gray-400 mt-1">Human-readable decision rationale, confidence scores, & feature attribution.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">DECISION DEC-101 (BUY_SMALL)</span>
            <h3 className="text-base font-semibold text-white mt-1">Confidence: 81%</h3>
            <p className="text-xs text-gray-400">Top Features: orderbook_imbalance, momentum_30m, spread_compression</p>
            <p className="text-xs text-gray-300 mt-2">"Bull regime detected with persistent positive order-flow imbalance and improving short-term momentum."</p>
          </div>
        </div>
      </div>
    </div>
  );
}
