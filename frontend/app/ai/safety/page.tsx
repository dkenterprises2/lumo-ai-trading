"use client";

import React from "react";

export default function AISafetyPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">AI Safety Controls & Guardrails</h1>
        <p className="text-gray-400 mt-1">Loss circuit breakers, drawdown limits, & automatic shadow demotion events.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">SAFETY EVENT SAFE-101</span>
            <h3 className="text-base font-semibold text-white mt-1">Rule: MAX_DAILY_LOSS_EXCEEDED</h3>
            <p className="text-xs text-gray-400">Agent: AGENT-VOL-01 | Severity: WARNING</p>
          </div>
          <span className="text-xs bg-amber-950 text-amber-300 border border-amber-700 px-3 py-1 rounded">GUARDRAIL TRIGGERED</span>
        </div>
      </div>
    </div>
  );
}
