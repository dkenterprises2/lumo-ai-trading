"use client";

import React from "react";

export default function AutonomousOperationsCenterPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Autonomous Operations Center & Incident Response</h1>
        <p className="text-gray-400 mt-1">Autonomous SRE assistant, API outage detection, FIX session recovery, & remediation playbooks.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-red-400 font-bold">INCIDENT: INC-P24-101 (HIGH SEVERITY)</span>
            <h3 className="text-lg font-bold text-white mt-1">OKX FIX Session Gateway Desynchronization</h3>
            <p className="text-xs text-gray-400">Suggested Action: Trigger FIX Session Recovery & Failover to Binance Route</p>
          </div>
          <button className="bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1 rounded text-xs font-bold">Approve Remediation</button>
        </div>
      </div>
    </div>
  );
}
