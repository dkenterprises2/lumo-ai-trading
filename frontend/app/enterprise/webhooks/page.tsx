"use client";

import React from "react";

export default function EnterpriseWebhooksPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Webhook Delivery & Event Subscriptions</h1>
        <p className="text-gray-400 mt-1">Signed payload webhooks, retry policies, & dead-letter queue inspection.</p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
        <div className="border border-gray-800 p-4 rounded-lg bg-black/40 flex justify-between items-center">
          <div>
            <span className="font-mono text-xs text-emerald-400 font-bold">WH_101 (SLACK HOOK)</span>
            <h3 className="text-base font-semibold text-white mt-1">https://hooks.slack.com/services/T000/B000/XXXX</h3>
            <p className="text-xs text-gray-400">Events: order_filled, alert_generated, quota_threshold_reached</p>
          </div>
          <span className="text-xs bg-emerald-950 text-emerald-300 border border-emerald-700 px-3 py-1 rounded">ACTIVE</span>
        </div>
      </div>
    </div>
  );
}
