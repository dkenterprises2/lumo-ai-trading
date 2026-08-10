'use client';

import React from 'react';
import Link from 'next/link';
import { ShieldAlert, ArrowLeft, Lock } from 'lucide-react';

export default function AccessDeniedPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-12 text-slate-100">
      <div className="w-full max-w-md space-y-6 rounded-2xl border border-slate-800 bg-slate-900/80 p-8 text-center backdrop-blur-xl shadow-2xl shadow-purple-950/20">
        <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          <ShieldAlert className="h-8 w-8" />
        </div>

        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-rose-500/30 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-300">
            <Lock className="h-3.5 w-3.5" />
            HTTP 403 FORBIDDEN
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-white">403 — Access Denied</h1>
          <p className="text-sm text-slate-400">
            You do not have permission to access the Lumo Super Admin Console.
          </p>
        </div>

        <div className="rounded-xl border border-slate-800 bg-slate-950/60 p-4 text-xs text-slate-400">
          Super Admin privileges (<span className="font-mono text-purple-400">SUPER_ADMIN</span>) are required to access enterprise platform infrastructure, system health, and governance controls.
        </div>

        <div className="pt-2">
          <Link
            href="/dashboard"
            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-600 px-5 py-3 font-semibold text-white shadow-lg shadow-blue-600/20 transition-all hover:from-blue-500 hover:to-cyan-500"
          >
            <ArrowLeft className="h-4 w-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    </div>
  );
}
