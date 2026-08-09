"use client";

import React from "react";

export default function DriftDetectionPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Model & Feature Drift Detection</h1>
        <p className="text-gray-400 mt-1">Population Stability Index (PSI), regime shifts, and retraining triggers.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-4">
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">Population Stability Index (PSI)</span>
          <span className="text-amber-400 font-bold">0.12 (Moderate Drift)</span>
        </div>
        <div className="flex justify-between items-center border-b border-gray-800 pb-3">
          <span className="text-white font-medium">Volatility Regime Shift</span>
          <span className="text-emerald-400 font-bold">0.18 (Normal)</span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-white font-medium">Retraining Recommendation</span>
          <span className="bg-amber-500/20 text-amber-300 text-xs font-bold px-3 py-1 rounded border border-amber-500/40">TRIGGER RETRAINING</span>
        </div>
      </div>
    </div>
  );
}
