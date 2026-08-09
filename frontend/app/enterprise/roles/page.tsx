"use client";

import React from "react";

export default function EnterpriseRolesPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Declarative RBAC & Permission Matrix</h1>
        <p className="text-gray-400 mt-1">Granular action permissions for Super Admin, Org Owner, Trader, Quant, & Compliance roles.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-indigo-400 font-bold font-mono">ORG_ADMIN</span>
            <h3 className="text-base font-semibold text-white mt-1">Full Tenant Admin</h3>
            <p className="text-xs text-gray-400 mt-1">All Org, Member, & Billing Permissions</p>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-emerald-400 font-bold font-mono">TRADER</span>
            <h3 className="text-base font-semibold text-white mt-1">Execution & Market Data</h3>
            <p className="text-xs text-gray-400 mt-1">Execution Orders, Algos, AI Signal Controls</p>
          </div>
          <div className="bg-black/50 p-4 rounded-lg border border-gray-800">
            <span className="text-xs text-amber-400 font-bold font-mono">COMPLIANCE_OFFICER</span>
            <h3 className="text-base font-semibold text-white mt-1">Audit & Surveillance</h3>
            <p className="text-xs text-gray-400 mt-1">Immutable Audit Trail & Regulatory Exports</p>
          </div>
        </div>
      </div>
    </div>
  );
}
