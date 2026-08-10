'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Building2, 
  Users, 
  Activity, 
  Brain, 
  LineChart, 
  BookOpen, 
  ShieldAlert, 
  Database, 
  Settings, 
  Search, 
  Bell, 
  Sparkles, 
  ChevronRight, 
  Menu, 
  X, 
  LogOut, 
  ShieldCheck, 
  RefreshCw,
  Server,
  Zap
} from 'lucide-react';
import { AdminUser } from '@/hooks/useAdminGuard';

interface AdminLayoutProps {
  children: React.ReactNode;
  user: AdminUser | null;
}

const sidebarItems = [
  { id: 'dashboard', label: 'Dashboard', href: '/admin', icon: LayoutDashboard },
  { id: 'tenants', label: 'Tenants', href: '/admin/tenants', icon: Building2 },
  { id: 'users', label: 'Users', href: '/admin/users', icon: Users },
  { id: 'system', label: 'System Health', href: '/admin/system', icon: Activity },
  { id: 'ai-governance', label: 'AI Governance', href: '/admin/ai-governance', icon: Brain },
  { id: 'trading-monitoring', label: 'Trading Monitoring', href: '/admin/platform-metrics', icon: LineChart },
  { id: 'learning-loop', label: 'Learning Loop', href: '/learning', icon: Zap },
  { id: 'audit-logs', label: 'Audit Logs', href: '/admin/security', icon: ShieldAlert },
  { id: 'backups', label: 'Backups', href: '/admin/backups', icon: Database },
  { id: 'settings', label: 'Settings', href: '/settings', icon: Settings }
];

export function AdminLayout({ children, user }: AdminLayoutProps) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [quickActionsOpen, setQuickActionsOpen] = useState(false);

  // Generate breadcrumbs from pathname
  const pathSegments = pathname.split('/').filter(Boolean);

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Mobile Drawer Overlay */}
      {mobileOpen && (
        <div 
          className="fixed inset-0 z-40 bg-slate-950/80 backdrop-blur-sm lg:hidden"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Left Sidebar */}
      <aside className={`fixed top-0 bottom-0 left-0 z-50 flex w-64 flex-col border-r border-slate-800 bg-slate-950/95 backdrop-blur-xl transition-transform duration-300 lg:translate-x-0 ${
        mobileOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        {/* Brand Header */}
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-6">
          <Link href="/admin" className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-purple-600 via-cyan-500 to-emerald-400 p-0.5 shadow-lg shadow-purple-500/20">
              <div className="flex h-full w-full items-center justify-center rounded-[10px] bg-slate-950">
                <ShieldCheck className="h-5 w-5 text-purple-400" />
              </div>
            </div>
            <div>
              <span className="font-bold text-white tracking-wide">Lumo<span className="text-purple-400">Admin</span></span>
              <span className="block text-[10px] font-medium tracking-wider text-slate-400 uppercase">Enterprise Console</span>
            </div>
          </Link>

          <button 
            onClick={() => setMobileOpen(false)}
            className="rounded-lg p-1 text-slate-400 hover:bg-slate-800 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Environment Badge */}
        <div className="px-4 py-3 border-b border-slate-800/80">
          <div className="flex items-center justify-between rounded-xl border border-emerald-500/30 bg-emerald-500/10 px-3 py-1.5 text-xs font-semibold text-emerald-300">
            <span className="flex items-center gap-1.5">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
              Environment
            </span>
            <span className="font-mono text-[11px] uppercase tracking-wider text-emerald-200">PRODUCTION</span>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
          {sidebarItems.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/admin' && pathname.startsWith(item.href));
            const Icon = item.icon;
            return (
              <Link
                key={item.id}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                className={`group flex items-center justify-between rounded-xl px-3.5 py-2.5 text-xs font-semibold transition-all ${
                  isActive
                    ? 'border border-purple-500/30 bg-gradient-to-r from-purple-500/20 to-blue-500/10 text-white shadow-md shadow-purple-500/10'
                    : 'text-slate-400 hover:bg-slate-900 hover:text-slate-200'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`h-4 w-4 transition-colors ${isActive ? 'text-purple-400' : 'text-slate-500 group-hover:text-slate-300'}`} />
                  <span>{item.label}</span>
                </div>
                {isActive && <ChevronRight className="h-3.5 w-3.5 text-purple-400" />}
              </Link>
            );
          })}
        </nav>

        {/* Footer Admin User Info */}
        <div className="border-t border-slate-800 p-4">
          <div className="flex items-center gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-purple-500/20 text-purple-300 font-bold text-sm border border-purple-500/30">
              {user?.name?.[0] || 'A'}
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-xs font-semibold text-white">{user?.name || 'Super Admin'}</p>
              <p className="truncate text-[11px] text-slate-400">{user?.email || 'admin@lumo.trade'}</p>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col lg:pl-64">
        {/* Topbar */}
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-800 bg-slate-950/80 px-6 backdrop-blur-xl">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setMobileOpen(true)}
              className="rounded-xl border border-slate-800 p-2 text-slate-400 hover:bg-slate-900 hover:text-white lg:hidden"
            >
              <Menu className="h-5 w-5" />
            </button>

            {/* Breadcrumbs */}
            <div className="hidden sm:flex items-center gap-2 text-xs font-semibold text-slate-400">
              <Link href="/admin" className="hover:text-purple-400 transition-colors">Admin</Link>
              {pathSegments.slice(1).map((segment, idx) => (
                <React.Fragment key={idx}>
                  <ChevronRight className="h-3.5 w-3.5 text-slate-600" />
                  <span className="capitalize text-slate-200">{segment.replace('-', ' ')}</span>
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* Search & Actions */}
          <div className="flex items-center gap-4">
            {/* Global Search Bar */}
            <div className="relative hidden md:block w-64">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search users, tenants, metrics..."
                className="w-full rounded-xl border border-slate-800 bg-slate-900/80 py-2 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>

            {/* Notifications Bell */}
            <button className="relative rounded-xl border border-slate-800 bg-slate-900/60 p-2 text-slate-400 hover:border-slate-700 hover:text-white transition-colors">
              <Bell className="h-4 w-4" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-purple-400 animate-ping" />
              <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-purple-500" />
            </button>

            {/* Quick Actions Dropdown */}
            <div className="relative">
              <button
                onClick={() => setQuickActionsOpen(!quickActionsOpen)}
                className="flex items-center gap-2 rounded-xl border border-purple-500/30 bg-purple-500/10 px-3.5 py-2 text-xs font-semibold text-purple-300 hover:bg-purple-500/20 transition-all"
              >
                <Sparkles className="h-3.5 w-3.5 text-purple-400" />
                <span>Quick Actions</span>
              </button>

              {quickActionsOpen && (
                <div 
                  className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-800 bg-slate-900 p-2 shadow-2xl z-50 space-y-1 text-xs"
                  onClick={() => setQuickActionsOpen(false)}
                >
                  <button className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white">
                    <RefreshCw className="h-3.5 w-3.5 text-cyan-400" />
                    Restart Services
                  </button>
                  <button className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white">
                    <Database className="h-3.5 w-3.5 text-emerald-400" />
                    Trigger System Backup
                  </button>

                  <Link href="/admin/system" className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white">
                    <Server className="h-3.5 w-3.5 text-purple-400" />
                    System Diagnostics
                  </Link>
                </div>
              )}
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 p-6 lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
