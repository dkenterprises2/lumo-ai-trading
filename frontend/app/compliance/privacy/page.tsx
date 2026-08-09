"use client";

import React from "react";

export default function GDPRPrivacyPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">GDPR & DPDP Data Privacy Tooling</h1>
        <p className="text-gray-400 mt-1">Consent management, Data Subject Requests (DSR), and export tooling.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <h2 className="text-xl font-bold text-white mb-4">Data Subject Right Actions</h2>
        <div className="flex gap-4">
          <button className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Export Personal Data
          </button>
          <button className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
            Request Data Erasure
          </button>
        </div>
      </div>
    </div>
  );
}
