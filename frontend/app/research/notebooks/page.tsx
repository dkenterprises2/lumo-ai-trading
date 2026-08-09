"use client";

import React from "react";

export default function ResearchNotebooksPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Interactive Research Notebook Execution</h1>
        <p className="text-gray-400 mt-1">Jupyter sandbox execution service and automated script runner.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">JOB-NB-2026</span>
            <h3 className="text-base font-semibold text-white mt-1">alpha_research_pipeline.ipynb</h3>
            <p className="text-xs text-gray-400">Execution Time: 3.42s | Outputs: 8 Graphs</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">COMPLETED</span>
        </div>
      </div>
    </div>
  );
}
