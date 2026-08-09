"use client";

import React from "react";

export default function AdminSecurityPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Security & Audit Event Logs</h1>
        <p className="text-gray-400 mt-1">Super admin authentication, privilege escalations, and audit logs.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="bg-black/50 border border-gray-800 rounded-lg p-4 font-mono text-xs text-gray-300">
          <div className="text-emerald-400 font-bold mb-1">[SEC-EVT-101] SUPER_ADMIN_AUTHENTICATED</div>
          <div>User ID: 1 | Email: jiodkd@gmail.com</div>
          <div>IP: 127.0.0.1 | Role: SUPER_ADMIN</div>
        </div>
      </div>
    </div>
  );
}
