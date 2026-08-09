"use client";

import React from "react";

export default function ResearchDataLakePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Parquet Data Lake & DuckDB Engine</h1>
        <p className="text-gray-400 mt-1">Vectorized SQL execution over partitioned market data, orderbook ticks, & on-chain data.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">DUCKDB VECTORIZED QUERY ENGINE</span>
            <h3 className="text-lg font-bold text-white mt-1">market_data.close (ZSTD Parquet)</h3>
            <p className="text-xs text-gray-400">Partitions Scanned: 365 | Query Execution: 4.2ms</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">VECTORIZED</span>
        </div>
      </div>
    </div>
  );
}
