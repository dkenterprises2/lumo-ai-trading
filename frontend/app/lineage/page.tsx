"use client";

import React from "react";

export default function AlphaLineagePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Alpha Lineage & Provenance Graph</h1>
        <p className="text-gray-400 mt-1">Dataset snapshot &rarr; feature version &rarr; AutoML trial &rarr; deployment version lineage.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">LINEAGE: ALPHA_MOMENTUM_V12</span>
            <h3 className="text-base font-semibold text-white mt-1">snap_2026_08_09_BTC &rarr; Feature v1 &rarr; Cand cand_automl_101 &rarr; Git c3f98a2</h3>
            <p className="text-xs text-gray-400">Provenance Verified: 100% Cryptographic Match</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">100% VERIFIED</span>
        </div>
      </div>
    </div>
  );
}
