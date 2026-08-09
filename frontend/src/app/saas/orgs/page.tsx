"use client";

import React from "react";

export default function OrganizationsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Organization & Workspace Management</h1>
        <p className="text-gray-400 mt-1">Multi-tenant workspace isolation, team roles, and settings.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Your Organizations</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Create Organization
          </button>
        </div>

        <div className="border border-gray-800 rounded-lg p-4 bg-black/40">
          <div className="flex justify-between items-center">
            <div>
              <span className="font-mono text-xs text-indigo-400 font-bold">ORG-101</span>
              <h3 className="text-lg font-bold text-white mt-1">Alpha Quant Capital</h3>
              <p className="text-sm text-gray-400">Slug: alpha-quant | Owner: admin@alphaquant.com</p>
            </div>
            <span className="text-xs bg-emerald-900/60 text-emerald-300 px-3 py-1 rounded-full border border-emerald-700">ENTERPRISE TENANT</span>
          </div>
        </div>
      </div>
    </div>
  );
}
