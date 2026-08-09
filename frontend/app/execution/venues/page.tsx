"use client";

import React from "react";

export default function VenueQualityPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Venue Quality Ranking & Latency Benchmarks</h1>
        <p className="text-gray-400 mt-1">Fill quality percentile ranking, ack-to-fill latency, & venue failover manager.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">VENUE: BINANCE INSTITUTIONAL</span>
            <h3 className="text-lg font-bold text-white mt-1">Quality Score: 96.5 / 100</h3>
            <p className="text-xs text-gray-400">Order-to-Ack Latency: 12.4 ms | Fill Rate: 99.2%</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">CONNECTED</span>
        </div>
      </div>
    </div>
  );
}
