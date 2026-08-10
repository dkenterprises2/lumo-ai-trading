'use client';

import React from 'react';
import { useAdminGuard } from '@/hooks/useAdminGuard';
import { AdminLayout } from '@/components/admin/AdminLayout';
import { RefreshCw, ShieldCheck } from 'lucide-react';

export default function AdminRootLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, authorized } = useAdminGuard();

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-950 text-slate-100">
        <div className="flex flex-col items-center gap-4">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-purple-500/10 border border-purple-500/30 text-purple-400">
            <ShieldCheck className="h-8 w-8 animate-pulse" />
          </div>
          <div className="flex items-center gap-2 text-sm font-semibold text-slate-400">
            <RefreshCw className="h-4 w-4 animate-spin text-purple-400" />
            Verifying Super Admin Authorization...
          </div>
        </div>
      </div>
    );
  }

  if (!authorized) {
    return null; // Hook redirects to /403 or /login
  }

  return <AdminLayout user={user}>{children}</AdminLayout>;
}
