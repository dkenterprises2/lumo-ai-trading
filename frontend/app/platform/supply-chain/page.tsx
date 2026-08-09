"use client";

import React from "react";

export default function PlatformSupplyChainPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Software Supply-Chain Security & SBOM</h1>
        <p className="text-gray-400 mt-1">SPDX SBOM generation, Cosign image signing, & container CVE scanning.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">SPDX SBOM 2.2</span>
            <h3 className="text-lg font-bold text-white mt-1">lumotrade/lumo-api:v3.6.0</h3>
            <p className="text-xs text-gray-400">Cosign Signed: True | CVEs: 0 Critical, 0 High, 2 Medium</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">COSIGN SIGNED</span>
        </div>
      </div>
    </div>
  );
}
