"use client";

import React from "react";

export default function ResearchFeatureLineagePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Feature Lineage & Dependency Graph</h1>
        <p className="text-gray-400 mt-1">Upstream data lake dependencies, transformation lineage, & downstream model usage.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">LINEAGE GRAPH</span>
            <h3 className="text-base font-semibold text-white mt-1">market_data.close &rarr; momentum_20d &rarr; RL Portfolio Agent</h3>
            <p className="text-xs text-gray-400">Upstream: 1 Table | Downstream: 3 Models</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">LINEAGE VERIFIED</span>
        </div>
      </div>
    </div>
  );
}
