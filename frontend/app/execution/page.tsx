"use client";

import React from "react";
import Link from "next/link";

export default function ExecutionOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Institutional Execution Algorithms</h1>
        <p className="text-gray-400 mt-1">TWAP, VWAP, POV, Iceberg, Smart Liquidity Seeking, & Transaction Cost Analysis (TCA).</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/execution/twap" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">TWAP Algorithm</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">Time-Sliced</div>
          <div className="text-xs text-gray-500 mt-1">Randomized Interval Slicing</div>
        </Link>

        <Link href="/execution/vwap" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">VWAP Algorithm</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">Volume Curve</div>
          <div className="text-xs text-gray-500 mt-1">U-Shaped Intraday Benchmark</div>
        </Link>

        <Link href="/execution/iceberg" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Iceberg Engine</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">Hidden Reserve</div>
          <div className="text-xs text-gray-500 mt-1">Anti-Detection Replenishment</div>
        </Link>

        <Link href="/execution/tca" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">TCA Engine</div>
          <div className="text-2xl font-bold text-white mt-1">Shortfall 1.85 bps</div>
          <div className="text-xs text-emerald-400 mt-1">98.15 Efficiency Score</div>
        </Link>
      </div>
    </div>
  );
}
