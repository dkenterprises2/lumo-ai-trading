'use client';

import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Search, 
  Filter, 
  ShieldCheck, 
  MoreVertical, 
  UserPlus, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Key, 
  Trash2, 
  ChevronLeft, 
  ChevronRight,
  Lock,
  UserCheck,
  UserX
} from 'lucide-react';

interface UserRecord {
  id: number;
  name: string;
  email: string;
  role: string;
  tenant_id: string;
  status: 'active' | 'suspended' | 'disabled';
  created_at: string;
  last_login: string;
}

const DEMO_USERS: UserRecord[] = [
  {
    id: 1,
    name: 'Jio Platform Admin',
    email: 'jiodkd@gmail.com',
    role: 'SUPER_ADMIN',
    tenant_id: 'ORG-SYSTEM-01',
    status: 'active',
    created_at: '2026-01-01 00:00:00',
    last_login: '2026-08-10 11:30:00'
  },
  {
    id: 2,
    name: 'Quantum Hedge Admin',
    email: 'quant_admin@qcapital.com',
    role: 'ADMIN',
    tenant_id: 'TEN-QCAPITAL',
    status: 'active',
    created_at: '2026-02-15 10:14:00',
    last_login: '2026-08-10 09:45:00'
  },
  {
    id: 3,
    name: 'Alpha Algo Trader',
    email: 'trader_alpha@lumo.trade',
    role: 'trader',
    tenant_id: 'TEN-QCAPITAL',
    status: 'active',
    created_at: '2026-03-20 14:22:00',
    last_login: '2026-08-09 22:11:00'
  },
  {
    id: 4,
    name: 'Risk Auditor User',
    email: 'auditor_01@compliance.org',
    role: 'viewer',
    tenant_id: 'TEN-NEXUS_INC',
    status: 'active',
    created_at: '2026-04-10 11:05:00',
    last_login: '2026-08-08 16:00:00'
  },
  {
    id: 5,
    name: 'Suspended Account',
    email: 'flagged_trader@badactor.net',
    role: 'trader',
    tenant_id: 'TEN-RETAIL_02',
    status: 'suspended',
    created_at: '2026-05-18 08:30:00',
    last_login: '2026-08-01 12:00:00'
  }
];

export default function AdminUsersPage() {
  const [users, setUsers] = useState<UserRecord[]>(DEMO_USERS);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('ALL');
  const [tenantFilter, setTenantFilter] = useState('ALL');
  const [activeMenuId, setActiveMenuId] = useState<number | null>(null);
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/users');
      if (res.ok) {
        const json = await res.json();
        if (json.users && Array.isArray(json.users) && json.users.length > 0) {
          setUsers(json.users);
        }
      }
    } catch (err) {
      console.error('Failed to fetch platform users:', err);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // User Actions
  const handlePromote = async (user: UserRecord) => {
    const newRole = user.role === 'SUPER_ADMIN' ? 'ADMIN' : 'SUPER_ADMIN';
    try {
      const res = await fetch(`/api/admin/users/${user.id}/role`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: newRole })
      });
      if (res.ok) {
        setUsers(users.map(u => u.id === user.id ? { ...u, role: newRole } : u));
        showToast(`User ${user.email} role updated to ${newRole}`);
      }
    } catch (err) {
      showToast('Failed to update user role', 'error');
    }
    setActiveMenuId(null);
  };

  const handleToggleStatus = async (user: UserRecord) => {
    const newStatus: 'active' | 'suspended' = user.status === 'active' ? 'suspended' : 'active';
    try {
      const res = await fetch(`/api/admin/users/${user.id}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });
      if (res.ok) {
        setUsers(users.map(u => u.id === user.id ? { ...u, status: newStatus } : u));
        showToast(`User ${user.email} status changed to ${newStatus}`);
      }
    } catch (err) {
      showToast('Failed to update user status', 'error');
    }
    setActiveMenuId(null);
  };

  const handleResetPassword = async (user: UserRecord) => {
    try {
      const res = await fetch(`/api/admin/users/${user.id}/reset-password`, { method: 'POST' });
      if (res.ok) {
        showToast(`Password reset link sent to ${user.email}`);
      }
    } catch (err) {
      showToast('Failed to reset password', 'error');
    }
    setActiveMenuId(null);
  };

  const handleDeleteUser = async (user: UserRecord) => {
    if (!confirm(`Are you sure you want to delete user ${user.email}?`)) return;
    try {
      const res = await fetch(`/api/admin/users/${user.id}`, { method: 'DELETE' });
      if (res.ok) {
        setUsers(users.filter(u => u.id !== user.id));
        showToast(`User ${user.email} deleted successfully.`);
      }
    } catch (err) {
      showToast('Failed to delete user', 'error');
    }
    setActiveMenuId(null);
  };

  // Filtered Users
  const filteredUsers = users.filter(u => {
    const matchesEmail = u.email.toLowerCase().includes(searchTerm.toLowerCase()) || u.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = roleFilter === 'ALL' || u.role.toUpperCase() === roleFilter.toUpperCase();
    const matchesTenant = tenantFilter === 'ALL' || u.tenant_id === tenantFilter;
    return matchesEmail && matchesRole && matchesTenant;
  });

  const totalPages = Math.ceil(filteredUsers.length / pageSize) || 1;
  const paginatedUsers = filteredUsers.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const getRoleBadge = (role: string) => {
    switch (role.toUpperCase()) {
      case 'SUPER_ADMIN': return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'ADMIN': return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
      case 'TRADER': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
      default: return 'bg-slate-500/20 text-slate-300 border-slate-500/40';
    }
  };

  return (
    <div className="space-y-8 text-slate-100">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-blue-500/30 bg-blue-500/10 p-2.5 text-blue-400">
              <Users className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Platform Users Console</h1>
              <p className="text-sm text-slate-400">Manage user accounts, RBAC roles, tenant bindings, and security credentials.</p>
            </div>
          </div>
        </div>

        <button
          onClick={fetchUsers}
          className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-blue-500/20 hover:from-blue-500 hover:to-purple-500 transition-all"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh Users
        </button>
      </div>

      {/* Toast Notification */}
      {toast && (
        <div className={`flex items-center gap-3 rounded-xl border p-4 text-sm font-semibold ${
          toast.type === 'success' ? 'border-emerald-500/40 bg-emerald-500/10 text-emerald-300' : 'border-rose-500/40 bg-rose-500/10 text-rose-300'
        }`}>
          {toast.type === 'success' ? <CheckCircle2 className="h-5 w-5" /> : <AlertTriangle className="h-5 w-5" />}
          {toast.message}
        </div>
      )}

      {/* Controls Bar: Search & Filters */}
      <div className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 md:flex-row md:items-center md:justify-between">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search by name or email address..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/60 py-2 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500 focus:outline-none"
          />
        </div>

        {/* Filter Dropdowns */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => { setRoleFilter(e.target.value); setCurrentPage(1); }}
            className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs font-semibold text-slate-300 focus:border-blue-500 focus:outline-none"
          >
            <option value="ALL">All Roles</option>
            <option value="SUPER_ADMIN">SUPER_ADMIN</option>
            <option value="ADMIN">ADMIN</option>
            <option value="TRADER">trader</option>
            <option value="VIEWER">viewer</option>
          </select>

          {/* Tenant Filter */}
          <select
            value={tenantFilter}
            onChange={(e) => { setTenantFilter(e.target.value); setCurrentPage(1); }}
            className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs font-semibold text-slate-300 focus:border-blue-500 focus:outline-none"
          >
            <option value="ALL">All Tenants</option>
            <option value="ORG-SYSTEM-01">System</option>
            <option value="TEN-QCAPITAL">TEN-QCAPITAL</option>
            <option value="TEN-NEXUS_INC">TEN-NEXUS_INC</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950/80 uppercase font-semibold text-slate-400">
              <tr>
                <th className="px-6 py-4">User Details</th>
                <th className="px-6 py-4">Role</th>
                <th className="px-6 py-4">Tenant ID</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Created At</th>
                <th className="px-6 py-4">Last Login</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {paginatedUsers.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    No users matching search filters found.
                  </td>
                </tr>
              ) : (
                paginatedUsers.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-900/80 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-500/20 font-bold text-purple-300 border border-purple-500/30">
                          {u.name?.[0] || 'U'}
                        </div>
                        <div>
                          <p className="font-semibold text-white">{u.name}</p>
                          <p className="text-slate-400 font-mono text-[11px]">{u.email}</p>
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 rounded-full border px-3 py-0.5 text-[10px] font-bold uppercase tracking-wider ${getRoleBadge(u.role)}`}>
                        <ShieldCheck className="h-3 w-3" />
                        {u.role}
                      </span>
                    </td>

                    <td className="px-6 py-4 font-mono text-slate-300">{u.tenant_id}</td>

                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase ${
                        u.status === 'active' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${u.status === 'active' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        {u.status}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-slate-400 font-mono">{u.created_at}</td>
                    <td className="px-6 py-4 text-slate-400 font-mono">{u.last_login}</td>

                    <td className="px-6 py-4 text-right relative">
                      <button
                        onClick={() => setActiveMenuId(activeMenuId === u.id ? null : u.id)}
                        className="rounded-lg border border-slate-800 bg-slate-950/60 p-1.5 text-slate-400 hover:text-white transition-colors"
                      >
                        <MoreVertical className="h-4 w-4" />
                      </button>

                      {/* Actions Menu Dropdown */}
                      {activeMenuId === u.id && (
                        <div className="absolute right-6 mt-2 w-48 rounded-xl border border-slate-800 bg-slate-900 p-1.5 shadow-2xl z-50 text-left space-y-1">
                          <button
                            onClick={() => handlePromote(u)}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white"
                          >
                            <ShieldCheck className="h-3.5 w-3.5 text-purple-400" />
                            {u.role === 'SUPER_ADMIN' ? 'Demote to ADMIN' : 'Promote to SUPER_ADMIN'}
                          </button>

                          <button
                            onClick={() => handleToggleStatus(u)}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white"
                          >
                            {u.status === 'active' ? (
                              <UserX className="h-3.5 w-3.5 text-rose-400" />
                            ) : (
                              <UserCheck className="h-3.5 w-3.5 text-emerald-400" />
                            )}
                            {u.status === 'active' ? 'Suspend User' : 'Activate User'}
                          </button>

                          <button
                            onClick={() => handleResetPassword(u)}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 hover:text-white"
                          >
                            <Key className="h-3.5 w-3.5 text-cyan-400" />
                            Reset Password
                          </button>

                          <button
                            onClick={() => handleDeleteUser(u)}
                            className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-rose-400 hover:bg-rose-500/10 hover:text-rose-300"
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                            Delete Account
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div className="flex items-center justify-between border-t border-slate-800 bg-slate-950/80 px-6 py-4 text-xs text-slate-400">
          <span>Showing {paginatedUsers.length} of {filteredUsers.length} Users</span>

          <div className="flex items-center gap-2">
            <button
              disabled={currentPage === 1}
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              className="rounded-lg border border-slate-800 px-3 py-1.5 hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronLeft className="h-4 w-4" />
            </button>
            <span className="font-semibold text-slate-200">Page {currentPage} of {totalPages}</span>
            <button
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              className="rounded-lg border border-slate-800 px-3 py-1.5 hover:bg-slate-800 disabled:opacity-40"
            >
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
