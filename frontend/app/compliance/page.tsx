"use client";

import React from "react";
import Link from "next/link";

export default function ComplianceOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise Compliance & Governance</h1>
        <p className="text-gray-400 mt-1">Immutable audit ledger, trade surveillance, regulatory reporting, and data privacy.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/compliance/audit" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Audit Ledger</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">VERIFIED</div>
          <div className="text-xs text-gray-500 mt-1">Append-Only Hash Chain</div>
        </Link>

        <Link href="/compliance/surveillance" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Surveillance Alerts</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">1 Open Alert</div>
          <div className="text-xs text-gray-500 mt-1">Wash Trading & Spoofing Rules</div>
        </Link>

        <Link href="/compliance/reports" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Regulatory Reports</div>
          <div className="text-2xl font-bold text-white mt-1">CSV / JSON</div>
          <div className="text-xs text-emerald-400 mt-1">Daily Trading Activity</div>
        </Link>

        <Link href="/security/compliance-status" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">SOC 2 Readiness</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">98.4%</div>
          <div className="text-xs text-gray-500 mt-1">ISO 27001: 96.8%</div>
        </Link>
      </div>
    </div>
  );
}
