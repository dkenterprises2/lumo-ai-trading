"use client";

import React from "react";

export default function EnterpriseIntegrationsPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Integration Marketplace</h1>
        <p className="text-gray-400 mt-1">Pre-built connectors for Slack, Microsoft Teams, Telegram, Jira, Notion, & Zapier.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl flex justify-between items-center">
          <div>
            <span className="text-xs text-indigo-400 font-bold font-mono">ALERTS</span>
            <h3 className="text-lg font-bold text-white mt-1">Slack Integration</h3>
            <p className="text-xs text-gray-400">Order & Alert Notifications</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">INSTALLED</span>
        </div>

        <div className="bg-gray-900 border border-gray-800 p-6 rounded-xl flex justify-between items-center">
          <div>
            <span className="text-xs text-indigo-400 font-bold font-mono">NOTIFICATIONS</span>
            <h3 className="text-lg font-bold text-white mt-1">Telegram Bot</h3>
            <p className="text-xs text-gray-400">Mobile Signal Stream</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">INSTALLED</span>
        </div>
      </div>
    </div>
  );
}
