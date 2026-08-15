"use client";

import React from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { BookOpen, Zap, ShieldAlert, Award, ExternalLink } from "lucide-react";

async function fetchModuleRegistry(): Promise<Record<string, string>> {
  const res = await fetch("/api/system/module-registry");
  if (!res.ok) {
    throw new Error("Failed to fetch module registry");
  }
  return res.json();
}

interface EnterpriseWidgetConfig {
  key: string;
  title: string;
  route: string;
  description: string;
  icon: React.ComponentType<{ className?: string }>;
  defaultStatus: "REAL" | "BETA" | "MOCK" | "DISABLED";
}

const ENTERPRISE_WIDGETS: EnterpriseWidgetConfig[] = [
  {
    key: "rag_knowledge_base",
    title: "RAG Knowledge Base",
    route: "/rag-library",
    description: "Vector search index, financial market doc embeddings & dynamic prompt context retrieval engine.",
    icon: BookOpen,
    defaultStatus: "REAL"
  },
  {
    key: "agentic_workflow_bus",
    title: "Agentic Workflow Bus",
    route: "/orchestration",
    description: "Multi-agent coordination protocol, task queue serialization, state machine & pub-sub event bus.",
    icon: Zap,
    defaultStatus: "BETA"
  },
  {
    key: "incident_response",
    title: "Incident Response (SRE)",
    route: "/operations-ai",
    description: "Automated anomaly detection, latency spike remediation, circuit breaker & self-healing operation AI.",
    icon: ShieldAlert,
    defaultStatus: "REAL"
  },
  {
    key: "human_approval_gate",
    title: "Human Approval Gate",
    route: "/governance/ai-actions",
    description: "Human-in-the-loop governance gate for large allocations, risk override & emergency stop execution.",
    icon: Award,
    defaultStatus: "REAL"
  }
];

export function ModuleRegistryStatusWidget() {
  const { data: registry } = useQuery({
    queryKey: ["module-registry"],
    queryFn: fetchModuleRegistry,
    refetchInterval: 10000,
    staleTime: 5000
  });

  const getStatusBadgeClass = (status: string) => {
    switch (status.toUpperCase()) {
      case "REAL":
        return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
      case "BETA":
        return "bg-amber-500/20 text-amber-400 border-amber-500/30";
      case "MOCK":
        return "bg-purple-500/20 text-purple-400 border-purple-500/30";
      case "DISABLED":
      default:
        return "bg-rose-500/20 text-rose-400 border-rose-500/30";
    }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-bold text-slate-200">Enterprise AI &amp; Governance Registry</h3>
        <span className="text-[10px] text-slate-400 font-mono">Status API: /api/system/module-registry</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {ENTERPRISE_WIDGETS.map((widget) => {
          const Icon = widget.icon;
          const status = registry?.[widget.key] || widget.defaultStatus;
          const badgeClass = getStatusBadgeClass(status);

          return (
            <Link
              key={widget.key}
              href={widget.route}
              className="bg-slate-900/60 border border-slate-800/80 p-4 rounded-2xl hover:border-slate-700 transition-all duration-200 flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className="w-4 h-4 text-slate-300 group-hover:text-cyan-400 transition-colors" />
                    <span className="font-bold text-white text-xs truncate">{widget.title}</span>
                  </div>
                  <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded border ${badgeClass}`}>
                    {status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 leading-normal line-clamp-2">
                  {widget.description}
                </p>
              </div>

              <div className="mt-3 pt-2 border-t border-slate-800/40 flex items-center justify-between text-[10px] text-slate-500 group-hover:text-cyan-400 transition-colors">
                <span>View Dashboard</span>
                <ExternalLink className="w-3 h-3" />
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
