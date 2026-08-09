"use client";

import React from "react";

export default function TickReplayPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Tick & Order Book Replay Engine</h1>
        <p className="text-gray-400 mt-1">Historical order book replay playback controls and depth scrubber.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-indigo-400 font-bold">REPLAY SESSION</span>
            <h3 className="text-lg font-bold text-white mt-1">BTC/USDT Historical L2 Replay</h3>
            <p className="text-xs text-gray-400">Speed: 1.0x | Status: RUNNING</p>
          </div>
          <div className="flex gap-2">
            <button className="bg-amber-600 hover:bg-amber-500 text-white px-3 py-1 rounded text-xs">Pause</button>
            <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1 rounded text-xs">Resume</button>
          </div>
        </div>
      </div>
    </div>
  );
}
