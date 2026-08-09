"use client";

import React from "react";

export default function HumanInTheLoopGovernancePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Human-in-the-Loop AI Action Approval Gate</h1>
        <p className="text-gray-400 mt-1">Review AI recommendations with supporting evidence, rationale, & rollback plans.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">ACTION_REQUEST: ACT_LIVE_DEPLOY_01</span>
            <h3 className="text-lg font-bold text-white mt-1">Promote alpha_momentum_v12 from SHADOW to LIVE</h3>
            <p className="text-xs text-gray-400">Evidence: 88% Robustness, Out-of-Sample Sharpe 2.18, 0 Rejections</p>
          </div>
          <div className="flex space-x-2">
            <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs font-bold">Approve Action</button>
            <button className="bg-red-600 hover:bg-red-500 text-white px-3 py-1 rounded text-xs font-bold">Reject</button>
          </div>
        </div>
      </div>
    </div>
  );
}
