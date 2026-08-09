"use client";

import React from "react";

export default function TeamMembersPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Team Members & RBAC Permissions</h1>
        <p className="text-gray-400 mt-1">Manage team invitations, roles (Owner, Admin, Trader, Viewer), and seat allocation.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-white">Active Members (3 / 5 Seats)</h2>
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Invite Member
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-black/50 text-gray-300 uppercase text-xs">
              <tr>
                <th className="px-4 py-3">Member ID</th>
                <th className="px-4 py-3">Email</th>
                <th className="px-4 py-3">Role</th>
                <th className="px-4 py-3">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-gray-800">
                <td className="px-4 py-3 font-mono text-white">MEM-1</td>
                <td className="px-4 py-3 text-white">admin@alphaquant.com</td>
                <td className="px-4 py-3 text-indigo-400 font-bold">OWNER</td>
                <td className="px-4 py-3 text-emerald-400 font-semibold">ACTIVE</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
