"use client";

import React from "react";

export default function DatasetCatalogPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Dataset Versioning & Parquet Catalog</h1>
        <p className="text-gray-400 mt-1">Immutable dataset snapshots, SHA-256 checksums, and version history.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">DS-BTC-1H-V1</span>
            <h3 className="text-base font-semibold text-white mt-1">BTC/USDT (1-Hour Timeframe)</h3>
            <p className="text-xs text-gray-400 font-mono">Row Count: 8,760 | Checksum: f8a9b1c2...</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">IMMUTABLE</span>
        </div>
      </div>
    </div>
  );
}
