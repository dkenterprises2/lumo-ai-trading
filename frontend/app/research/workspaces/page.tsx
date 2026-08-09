"use client";

import React from "react";

export default function ResearchWorkspacesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Collaborative Quant Workspaces</h1>
        <p className="text-gray-400 mt-1">Shared research threads, dataset bookmarking, & code review discussions.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">WS_QUANT_ALPHA</span>
            <h3 className="text-lg font-bold text-white mt-1">Alpha Discovery Workspace</h3>
            <p className="text-xs text-gray-400">Collaborators: 4 Quants | Active Threads: 12</p>
          </div>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs font-bold">Open Workspace</button>
        </div>
      </div>
    </div>
  );
}
