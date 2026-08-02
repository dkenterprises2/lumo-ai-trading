"use client";

import React from "react";
import { Database, ShieldCheck, Cpu } from "lucide-react";
import { TradingConnectionState } from "@/hooks/useTradingStream";

interface FooterProps {
  dbSyncStatus?: string;
  lastValidationTime?: string;
  connectionState: TradingConnectionState;
}

export function Footer({ dbSyncStatus, lastValidationTime, connectionState }: FooterProps) {
  return (
    <footer className="mt-8 flex flex-col items-center justify-between gap-4 rounded-2xl border border-slate-800/60 bg-slate-900/40 px-6 py-4 text-xs text-slate-400 backdrop-blur-xl sm:flex-row">
      <div className="flex flex-wrap items-center gap-4">
        <div className="flex items-center gap-1.5">
          <Database className="h-3.5 w-3.5 text-cyan-400" />
          <span>DB Status:</span>
          <span className="font-semibold text-emerald-400">{dbSyncStatus ?? "PENDING"}</span>
        </div>
        <span className="text-slate-700">|</span>
        <div className="flex items-center gap-1.5">
          <ShieldCheck className="h-3.5 w-3.5 text-purple-400" />
          <span>Last Validation:</span>
          <span className="font-medium text-slate-300">{lastValidationTime ?? "PENDING"}</span>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <Cpu className="h-3.5 w-3.5 text-slate-500" />
        <span>Stream: {connectionState.toUpperCase()}</span>
      </div>
    </footer>
  );
}
