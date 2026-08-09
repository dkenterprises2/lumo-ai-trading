"use client";

import React from "react";
import Link from "next/link";

export default function AdminConsoleOverview() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Super Admin Platform Console</h1>
        <p className="text-gray-400 mt-1">Global tenant management, revenue analytics, system health, and backup controls.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/admin/tenants" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Tenants</div>
          <div className="text-2xl font-bold text-white mt-1">48 Orgs</div>
          <div className="text-xs text-emerald-400 mt-1">46 Active | 2 Suspended</div>
        </Link>

        <Link href="/admin/revenue" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Monthly Revenue</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">$48,200</div>
          <div className="text-xs text-gray-500 mt-1">ARR: $578,400</div>
        </Link>

        <Link href="/admin/system-health" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">System Health</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">99.99%</div>
          <div className="text-xs text-emerald-400 mt-1">All Systems Operational</div>
        </Link>

        <Link href="/admin/backups" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Backups</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">Snapshot OK</div>
          <div className="text-xs text-gray-500 mt-1">RPO &lt; 5 seconds</div>
        </Link>
      </div>
    </div>
  );
}
