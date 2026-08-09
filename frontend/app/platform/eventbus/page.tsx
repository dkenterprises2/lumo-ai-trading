"use client";

import React from "react";

export default function EventBusStatusPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Event Bus & Message Streams</h1>
        <p className="text-gray-400 mt-1">Kafka primary event bus & Redis Streams fallback monitoring.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Primary Event Bus</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">Apache Kafka / NATS</div>
          <div className="text-xs text-gray-500 mt-1">Status: OPERATIONAL</div>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <div className="text-sm text-gray-400 font-medium">Fallback Message Bus</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">Redis Streams</div>
          <div className="text-xs text-gray-500 mt-1">Status: READY</div>
        </div>
      </div>
    </div>
  );
}
