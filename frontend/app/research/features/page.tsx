"use client";

import React from "react";

export default function ResearchFeaturesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Time-Series Feature Store</h1>
        <p className="text-gray-400 mt-1">Registry-driven feature engineering, materialization pipelines, & online/offline parity.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">FEATURE: MOMENTUM_20D</span>
            <h3 className="text-lg font-bold text-white mt-1">close / lag(close, 20) - 1</h3>
            <p className="text-xs text-gray-400">Entity: symbol | Freshness: daily | Owner: quant_research</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs font-bold">Materialize Feature</button>
        </div>
      </div>
    </div>
  );
}
