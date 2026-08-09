"use client";

import React from "react";

export default function AIMemoryDecisionProvenancePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Decision Provenance & Memory Explorer</h1>
        <p className="text-gray-400 mt-1">Provenance graph linking prompts &rarr; retrieved knowledge &rarr; recommendation &rarr; approved action.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">PROVENANCE: WS_QUANT_TEAM</span>
            <h3 className="text-base font-semibold text-white mt-1">Prompt &rarr; RAG Ingestion &rarr; Risk Evaluation &rarr; Action Approved</h3>
            <p className="text-xs text-gray-400">Provenance Chain Length: 14 Nodes | Purge Policy: 90 Days</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">PROVENANCE VERIFIED</span>
        </div>
      </div>
    </div>
  );
}
