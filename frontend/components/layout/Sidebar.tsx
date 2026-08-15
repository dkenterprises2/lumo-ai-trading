"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TradingConnectionState } from "@/hooks/useTradingStream";
import {
  LayoutDashboard,
  Brain,
  Scan,
  LineChart,
  ClipboardList,
  Crosshair,
  History,
  TrendingUp,
  BookOpen,
  Award,
  Bot,
  ChessKnight,
  ShieldAlert,
  Newspaper,
  FileSpreadsheet,
  Bell,
  Settings,
  Key,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  Zap,
  Cpu,
  ArrowLeftRight,
  LogOut,
  User as UserIcon
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";

interface SidebarProps {
  activeTab?: string;
  setActiveTab?: (tab: string) => void;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  connectionState: TradingConnectionState;
}

export interface SidebarItem {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  category: "Core" | "Institutional Intelligence" | "Analytics" | "Enterprise" | "Settings";
  badge?: string;
}

export const sidebarItems: SidebarItem[] = [
  { id: "dashboard", label: "Dashboard", href: "/dashboard", icon: LayoutDashboard, category: "Core" },
  { id: "learning", label: "Self-Learning AI", href: "/learning", icon: Brain, category: "Core" },
  { id: "copilot", label: "AI Copilot", href: "/copilot", icon: Bot, category: "Core" },

  // Institutional Intelligence
  { id: "risk", label: "Portfolio Risk", href: "/risk", icon: ShieldAlert, category: "Institutional Intelligence", badge: "READY" },
  { id: "execution", label: "Execution OMS/EMS", href: "/execution", icon: Crosshair, category: "Institutional Intelligence", badge: "READY" },
  { id: "shadow", label: "Shadow Trading", href: "/shadow", icon: Cpu, category: "Institutional Intelligence", badge: "READY" },
  { id: "arbitrage", label: "Arbitrage Intelligence", href: "/arbitrage", icon: ArrowLeftRight, category: "Institutional Intelligence", badge: "READY" },
  { id: "news", label: "News Intelligence", href: "/news", icon: Newspaper, category: "Institutional Intelligence", badge: "LIVE" },

  // Analytics & Trading
  { id: "scanner", label: "Market Scanner", href: "/scanner", icon: Scan, category: "Analytics" },
  { id: "charts", label: "Charts", href: "/charts", icon: LineChart, category: "Analytics" },
  { id: "orders", label: "Orders", href: "/orders", icon: ClipboardList, category: "Analytics" },
  { id: "positions", label: "Positions", href: "/positions", icon: Crosshair, category: "Analytics" },
  { id: "trade-history", label: "Trade History", href: "/history", icon: History, category: "Analytics" },
  { id: "pnl-history", label: "PnL History", href: "/pnl", icon: TrendingUp, category: "Analytics" },
  { id: "wallet-ledger", label: "Wallet Ledger", href: "/ledger", icon: BookOpen, category: "Analytics" },
  { id: "performance", label: "Performance", href: "/performance", icon: Award, category: "Analytics" },
  { id: "bots", label: "Bots", href: "/bots", icon: Bot, category: "Analytics" },

  // Enterprise AI & Governance
  { id: "nl-strategy", label: "NL Strategy Builder", href: "/nl-strategy-builder", icon: ChessKnight, category: "Enterprise" },
  { id: "portfolio-assistant", label: "Portfolio Assistant", href: "/portfolio-assistant", icon: TrendingUp, category: "Enterprise" },
  { id: "investigations", label: "Trade RCA", href: "/investigations", icon: Crosshair, category: "Enterprise" },
  { id: "operations-ai", label: "Operations AI (SRE)", href: "/operations-ai", icon: ShieldAlert, category: "Enterprise" },
  { id: "rag-library", label: "RAG Knowledge", href: "/rag-library", icon: BookOpen, category: "Enterprise" },
  { id: "orchestration", label: "Agent Orchestration", href: "/orchestration", icon: Zap, category: "Enterprise" },
  { id: "ai-actions", label: "AI Governance", href: "/governance/ai-actions", icon: Award, category: "Enterprise" },

  // Settings
  { id: "settings", label: "Settings", href: "/settings", icon: Settings, category: "Settings" },
  { id: "api-keys", label: "API Keys", href: "/api-keys", icon: Key, category: "Settings" }
];

export function Sidebar({ activeTab, setActiveTab, collapsed, setCollapsed, connectionState }: SidebarProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  const categories: Array<SidebarItem["category"]> = [
    "Core",
    "Institutional Intelligence",
    "Analytics",
    "Enterprise",
    "Settings"
  ];

  return (
    <aside
      className={`fixed left-0 top-0 z-40 h-screen transition-all duration-300 border-r border-slate-800/80 bg-slate-950/90 backdrop-blur-xl flex flex-col justify-between ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div>
        <div className="flex h-16 items-center justify-between px-4 border-b border-slate-800/80">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
              <Zap className="h-5 w-5 text-white" />
            </div>
            {!collapsed && (
              <div className="flex flex-col">
                <span className="font-bold text-lg tracking-wider text-slate-100 bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                  LUMO AI
                </span>
                <span className="text-[10px] tracking-widest text-slate-400 uppercase font-semibold">
                  Enterprise v4.8
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setCollapsed(!collapsed)}
            className="flex h-8 w-8 items-center justify-center rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 hover:border-slate-700 transition"
          >
            {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          </button>
        </div>

        {/* Navigation List */}
        <nav className="p-3 space-y-3 overflow-y-auto max-h-[calc(100vh-140px)] scrollbar-thin scrollbar-thumb-slate-800">
          {(user?.role?.toUpperCase() === 'SUPER_ADMIN' || user?.role?.toUpperCase() === 'SUPERADMIN' || user?.email?.toLowerCase() === 'jiodkd@gmail.com') && (
            <Link
              href="/admin"
              title={collapsed ? "Super Admin Console" : undefined}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-bold transition-all duration-200 ${
                pathname?.startsWith("/admin")
                  ? "bg-gradient-to-r from-purple-500/30 to-blue-500/20 text-purple-300 border border-purple-500/40 shadow-lg shadow-purple-500/20"
                  : "bg-purple-500/10 text-purple-400 border border-purple-500/20 hover:bg-purple-500/20"
              }`}
            >
              <ShieldCheck className="h-5 w-5 shrink-0 text-purple-400" />
              {!collapsed && <span className="truncate">Super Admin Console</span>}
            </Link>
          )}

          {categories.map((cat) => {
            const items = sidebarItems.filter((i) => i.category === cat);
            if (items.length === 0) return null;

            return (
              <div key={cat} className="space-y-1">
                {!collapsed && (
                  <div className="px-3 pt-2 pb-1 text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center justify-between">
                    <span>{cat}</span>
                    {cat === "Institutional Intelligence" && (
                      <span className="bg-cyan-500/15 text-cyan-400 px-1.5 py-0.5 rounded text-[9px] border border-cyan-500/30 font-mono font-bold">v4.8</span>
                    )}
                  </div>
                )}
                {items.map((item) => {
                  const Icon = item.icon;
                  const isActive = pathname === item.href || (item.href !== "/" && pathname?.startsWith(item.href));
                  return (
                    <Link
                      key={item.id}
                      href={item.href}
                      onClick={() => setActiveTab && setActiveTab(item.id)}
                      title={collapsed ? item.label : undefined}
                      className={`w-full flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold transition-all duration-200 ${
                        isActive
                          ? "bg-gradient-to-r from-cyan-500/20 to-blue-500/20 text-cyan-400 border border-cyan-500/35 shadow-md shadow-cyan-500/10 font-bold"
                          : "text-slate-400 hover:bg-slate-900/80 hover:text-slate-100 border border-transparent"
                      }`}
                    >
                      <div className="flex items-center gap-3 truncate">
                        <Icon className={`h-4 w-4 shrink-0 ${isActive ? "text-cyan-400" : "text-slate-400"}`} />
                        {!collapsed && <span className="truncate">{item.label}</span>}
                      </div>
                      {!collapsed && item.badge && (
                        <span className={`text-[9px] px-1.5 py-0.5 rounded-md font-mono font-bold ${
                          item.badge === "LIVE"
                            ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                            : "bg-cyan-500/15 text-cyan-400 border border-cyan-500/30"
                        }`}>
                          {item.badge}
                        </span>
                      )}
                    </Link>
                  );
                })}
              </div>
            );
          })}
        </nav>
      </div>


      {/* Footer / Account Profile & Logout */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-900/40">
        {user ? (
          <div className="flex items-center justify-between">
            <Link href="/profile" className="flex items-center gap-3 overflow-hidden">
              <img
                src={user.avatar || "https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader"}
                alt={user.name}
                className="h-9 w-9 shrink-0 rounded-full border border-cyan-500/30 bg-slate-900"
              />
              {!collapsed && (
                <div className="flex flex-col overflow-hidden">
                  <span className="text-xs font-semibold text-slate-200 truncate">{user.name}</span>
                  <span className="text-[10px] text-cyan-400 truncate flex items-center gap-1">
                    {user.trading_mode} • <span className="text-purple-400 font-bold uppercase tracking-wider">{user.plan || user.plan_tier || 'ENTERPRISE'}</span>
                  </span>
                </div>
              )}

            </Link>
            <button
              onClick={logout}
              title="Sign Out"
              className="p-2 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20 hover:bg-rose-500/20 transition-colors"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <Link
            href="/login"
            className="w-full flex items-center justify-center gap-2 py-2 px-3 bg-cyan-500/10 border border-cyan-500/20 rounded-xl text-xs font-semibold text-cyan-400 hover:bg-cyan-500/20 transition-colors"
          >
            <UserIcon className="h-4 w-4" />
            {!collapsed && <span>Sign In</span>}
          </Link>
        )}
      </div>
    </aside>
  );
}

