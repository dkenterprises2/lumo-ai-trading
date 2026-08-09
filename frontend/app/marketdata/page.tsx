"use client";

import React from "react";
import Link from "next/link";

export default function MarketDataOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Real-Time Market Data & Order Book Intelligence</h1>
        <p className="text-gray-400 mt-1">Level-2 order book streaming, Depth-of-Market (DOM), volume profiles, & spoofing detection.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/marketdata/orderbook" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Order Book L2</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">10 Depth Levels</div>
          <div className="text-xs text-gray-500 mt-1">Sub-Second Incremental Streams</div>
        </Link>

        <Link href="/marketdata/dom" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Depth-of-Market (DOM)</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">Spread: 0.50 (0.08 bps)</div>
          <div className="text-xs text-gray-500 mt-1">Depth Imbalance: 0.68</div>
        </Link>

        <Link href="/marketdata/volume-profile" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Volume Profile (POC)</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">POC: $64,810.00</div>
          <div className="text-xs text-gray-500 mt-1">VAH: $64,920 | VAL: $64,700</div>
        </Link>

        <Link href="/marketdata/microstructure" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Microstructure Alpha</div>
          <div className="text-2xl font-bold text-white mt-1">BULLISH_PRESSURE</div>
          <div className="text-xs text-emerald-400 mt-1">Confidence: 82% (30s horizon)</div>
        </Link>
      </div>
    </div>
  );
}
