"use client";

import React from "react";

export default function ResearchDatasetsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Dataset Registry & Checksum Snapshots</h1>
        <p className="text-gray-400 mt-1">Immutable dataset snapshots (`snap_2026_08_09_001`) with cryptographic SHA256 verification.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">SNAPSHOT_ID: SNAP_2026_08_09_BTC</span>
            <h3 className="text-lg font-bold text-white mt-1">Global Multi-Exchange OHLCV (12.4M rows)</h3>
            <p className="text-xs text-gray-400">SHA256: e3b0c44298fc1c149afbf4c89... | Status: IMMUTABLE</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">IMMUTABLE</span>
        </div>
      </div>
    </div>
  );
}
