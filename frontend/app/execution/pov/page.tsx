"use client";

import React from "react";

export default function POVConsolePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">POV (Participation of Volume) Console</h1>
        <p className="text-gray-400 mt-1">Real-time market participation cap and volume tracking engine.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">POV 10% TARGET</span>
            <h3 className="text-lg font-bold text-white mt-1">Current Participation: 9.8% (Capped at 20%)</h3>
            <p className="text-xs text-gray-400">Market Volume: 142.5 BTC / 5m</p>
          </div>
          <span className="text-xs bg-indigo-950 text-indigo-300 border border-indigo-700 px-3 py-1 rounded">ACTIVE SLICING</span>
        </div>
      </div>
    </div>
  );
}
