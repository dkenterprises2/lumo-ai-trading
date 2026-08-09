"use client";

import React from "react";

export default function EnterpriseUsersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Tenant User Directory</h1>
        <p className="text-gray-400 mt-1">Multi-tenant user provisioning, invitations, & role assignments.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Workspace</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-white font-bold">admin@acmecapital.com</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">ORG_ADMIN</td>
                <td className="px-4 py-3">Trading Desk</td>
                <td className="px-4 py-3 text-emerald-400 font-bold">ACTIVE</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
