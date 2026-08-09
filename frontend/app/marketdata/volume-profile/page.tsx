"use client";

import React from "react";

export default function VolumeProfilePage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Volume Profile Analytics</h1>
        <p className="text-gray-400 mt-1">Point of Control (POC), Value Area High (VAH), and Value Area Low (VAL).</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-amber-400 font-bold">POINT OF CONTROL (POC)</span>
            <h3 className="text-lg font-bold text-white mt-1">POC: $64,810.00 (450.2 BTC Traded)</h3>
            <p className="text-xs text-gray-400">Value Area: $64,700.00 – $64,920.00 (70% Volume)</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">HIGH NODE</span>
        </div>
      </div>
    </div>
  );
}
