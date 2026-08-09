"use client";

import React from "react";

export default function SubscriptionBillingPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Subscription Plans & Stripe Billing</h1>
        <p className="text-gray-400 mt-1">Manage subscription plan tiers, seat allocation, invoices, and payment history.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white">Free Simulator</h3>
          <div className="text-3xl font-bold text-white mt-2">$0 <span className="text-xs text-gray-500 font-normal">/ mo</span></div>
          <ul className="text-xs text-gray-400 space-y-2 mt-4">
            <li>10,000 API requests / mo</li>
            <li>1 Team Seat</li>
            <li>Paper Trading Only</li>
          </ul>
        </div>

        <div className="bg-gray-900 border border-indigo-500 rounded-xl p-6 relative">
          <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-0.5 rounded absolute top-4 right-4">POPULAR</span>
          <h3 className="text-lg font-bold text-white">Pro Trader</h3>
          <div className="text-3xl font-bold text-white mt-2">$199 <span className="text-xs text-gray-500 font-normal">/ mo</span></div>
          <ul className="text-xs text-gray-400 space-y-2 mt-4">
            <li>100,000 API requests / mo</li>
            <li>5 Team Seats</li>
            <li>Live Exchange Integration</li>
          </ul>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-bold text-white">Institutional Enterprise</h3>
          <div className="text-3xl font-bold text-white mt-2">$999 <span className="text-xs text-gray-500 font-normal">/ mo</span></div>
          <ul className="text-xs text-gray-400 space-y-2 mt-4">
            <li>1,000,000 API requests / mo</li>
            <li>25 Team Seats</li>
            <li>Dedicated SLA & Support</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
