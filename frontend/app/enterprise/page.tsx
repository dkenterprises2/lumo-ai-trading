"use client";

import React from "react";
import Link from "next/link";

export default function EnterpriseSaaSOverviewPage() {
  return (
    <div className="p-8 max-w-7xl mx-auto space-y-6">
      <div className="border-b border-gray-800 pb-4">
        <h1 className="text-3xl font-bold text-white tracking-tight">Enterprise SaaS, Multi-Tenant & White-Label Hub</h1>
        <p className="text-gray-400 mt-1">Tenant isolation, SAML SSO, subscriptions, usage metering, white-labeling, & custom domains.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Link href="/enterprise/organizations" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Active Tenants</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">12 Enterprise Orgs</div>
          <div className="text-xs text-gray-500 mt-1">Acme Capital, Alpha Hedge...</div>
        </Link>

        <Link href="/enterprise/sso" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Enterprise SSO</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">SAML 2.0 & OAuth</div>
          <div className="text-xs text-gray-500 mt-1">Google, Entra ID, Okta</div>
        </Link>

        <Link href="/enterprise/subscription" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Subscription Plan</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">ENTERPRISE TIER</div>
          <div className="text-xs text-emerald-400 mt-1">$4,999.00 / Mo (50 Seats)</div>
        </Link>

        <Link href="/enterprise/custom-domains" className="bg-gray-900 border border-gray-800 p-6 rounded-xl hover:border-indigo-500 transition-colors">
          <div className="text-xs text-gray-400 font-medium">Custom Domains</div>
          <div className="text-2xl font-bold text-white mt-1">SSL ACTIVE</div>
          <div className="text-xs text-gray-500 mt-1">trade.acmecapital.com</div>
        </Link>
      </div>
    </div>
  );
}
