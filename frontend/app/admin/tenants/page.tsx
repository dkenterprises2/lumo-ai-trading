'use client';

import React, { useState, useEffect } from 'react';
import { 
  Building2, 
  Plus, 
  Search, 
  CheckCircle2, 
  AlertTriangle, 
  HardDrive, 
  Users, 
  Sparkles, 
  RefreshCw, 
  MoreVertical, 
  X, 
  ShieldAlert, 
  Edit3, 
  PauseCircle, 
  PlayCircle,
  TrendingUp,
  Layers
} from 'lucide-react';

interface TenantRecord {
  tenant_id: string;
  name: string;
  slug: string;
  plan_tier: string;
  status: 'ACTIVE' | 'SUSPENDED';
  active_users: number;
  max_users: number;
  storage_used_gb: number;
  storage_limit_gb: number;
  monthly_volume_usd: string;
}

const DEMO_TENANTS: TenantRecord[] = [
  {
    tenant_id: 'ORG-101',
    name: 'Alpha Quant Capital',
    slug: 'alpha-quant',
    plan_tier: 'INSTITUTIONAL',
    status: 'ACTIVE',
    active_users: 18,
    max_users: 50,
    storage_used_gb: 42.5,
    storage_limit_gb: 100,
    monthly_volume_usd: '$4.2M'
  },
  {
    tenant_id: 'ORG-102',
    name: 'Nexus Digital Assets',
    slug: 'nexus-digital',
    plan_tier: 'PRO',
    status: 'ACTIVE',
    active_users: 8,
    max_users: 10,
    storage_used_gb: 18.2,
    storage_limit_gb: 50,
    monthly_volume_usd: '$1.8M'
  },
  {
    tenant_id: 'ORG-103',
    name: 'Apex Crypto Partners',
    slug: 'apex-crypto',
    plan_tier: 'PRO',
    status: 'SUSPENDED',
    active_users: 4,
    max_users: 10,
    storage_used_gb: 34.0,
    storage_limit_gb: 50,
    monthly_volume_usd: '$850K'
  }
];

export default function AdminTenantsPage() {
  const [tenants, setTenants] = useState<TenantRecord[]>(DEMO_TENANTS);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [planFilter, setPlanFilter] = useState('ALL');
  
  // Modals
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [confirmModal, setConfirmModal] = useState<{ tenant: TenantRecord; action: 'suspend' | 'activate' } | null>(null);
  
  // Form State
  const [newTenantName, setNewTenantName] = useState('');
  const [newTenantPlan, setNewTenantPlan] = useState('PRO');
  const [newTenantMaxUsers, setNewTenantMaxUsers] = useState(10);
  
  const [toast, setToast] = useState<{ message: string; type: 'success' | 'error' } | null>(null);

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    setLoading(true);
    try {
      const res = await fetch('/api/admin/tenants');
      if (res.ok) {
        const json = await res.json();
        if (json.tenants && Array.isArray(json.tenants) && json.tenants.length > 0) {
          setTenants(json.tenants);
        }
      }
    } catch (err) {
      console.error('Failed to fetch tenants:', err);
    } finally {
      setLoading(false);
    }
  };

  const showToast = (message: string, type: 'success' | 'error' = 'success') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  const handleCreateTenant = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTenantName.trim()) return;

    try {
      const res = await fetch('/api/admin/tenants/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newTenantName,
          plan_tier: newTenantPlan,
          max_users: newTenantMaxUsers
        })
      });

      if (res.ok) {
        const json = await res.json();
        const created: TenantRecord = json.tenant || {
          tenant_id: `ORG-${Date.now().toString().slice(-3)}`,
          name: newTenantName,
          slug: newTenantName.toLowerCase().replace(/[^a-z0-9]/g, '-'),
          plan_tier: newTenantPlan,
          status: 'ACTIVE',
          active_users: 1,
          max_users: newTenantMaxUsers,
          storage_used_gb: 0.5,
          storage_limit_gb: 50,
          monthly_volume_usd: '$0'
        };
        setTenants([...tenants, created]);
        showToast(`Tenant ${newTenantName} created successfully!`);
        setCreateModalOpen(false);
        setNewTenantName('');
      } else {
        showToast('Failed to create tenant', 'error');
      }
    } catch (err) {
      showToast('Network error creating tenant', 'error');
    }
  };

  const handleToggleStatus = async () => {
    if (!confirmModal) return;
    const { tenant, action } = confirmModal;
    const endpoint = `/api/admin/tenants/${tenant.tenant_id}/${action}`;

    try {
      const res = await fetch(endpoint, { method: 'PATCH' });
      if (res.ok) {
        const newStatus: 'ACTIVE' | 'SUSPENDED' = action === 'suspend' ? 'SUSPENDED' : 'ACTIVE';
        setTenants(tenants.map(t => t.tenant_id === tenant.tenant_id ? { ...t, status: newStatus } : t));
        showToast(`Tenant ${tenant.name} ${newStatus.toLowerCase()} successfully.`);
      }
    } catch (err) {
      showToast(`Failed to ${action} tenant`, 'error');
    } finally {
      setConfirmModal(null);
    }
  };

  const filteredTenants = tenants.filter(t => {
    const matchesSearch = t.name.toLowerCase().includes(searchTerm.toLowerCase()) || t.tenant_id.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPlan = planFilter === 'ALL' || t.plan_tier.toUpperCase() === planFilter.toUpperCase();
    return matchesSearch && matchesPlan;
  });

  const getTierBadge = (tier: string) => {
    switch (tier.toUpperCase()) {
      case 'INSTITUTIONAL': return 'bg-purple-500/20 text-purple-300 border-purple-500/40';
      case 'PRO': return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
      default: return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
    }
  };

  return (
    <div className="space-y-8 text-slate-100">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">
        <div>
          <div className="flex items-center gap-3">
            <div className="rounded-xl border border-purple-500/30 bg-purple-500/10 p-2.5 text-purple-400">
              <Building2 className="h-6 w-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white">Tenant Management Console</h1>
              <p className="text-sm text-slate-400">Multi-tenant enterprise organization isolation, plan tiers, and storage metrics.</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setCreateModalOpen(true)}
            className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-purple-600 to-cyan-600 px-4 py-2.5 text-xs font-semibold text-white shadow-lg shadow-purple-500/20 hover:from-purple-500 hover:to-cyan-500 transition-all"
          >
            <Plus className="h-4 w-4" />
            Create Tenant
          </button>
        </div>
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

      {/* Overview Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Active Organizations</span>
            <Building2 className="h-4 w-4 text-purple-400" />
          </div>
          <p className="text-3xl font-extrabold text-white">{tenants.filter(t => t.status === 'ACTIVE').length} / {tenants.length}</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Active Users</span>
            <Users className="h-4 w-4 text-cyan-400" />
          </div>
          <p className="text-3xl font-extrabold text-cyan-400">{tenants.reduce((acc, t) => acc + (t.active_users || 0), 0)} Users</p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5 space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Aggregate Volume</span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <p className="text-3xl font-extrabold text-emerald-400">$6.85M / mo</p>
        </div>
      </div>

      {/* Controls Bar */}
      <div className="flex flex-col gap-4 rounded-2xl border border-slate-800 bg-slate-900/60 p-4 md:flex-row md:items-center md:justify-between">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-slate-500" />
          <input
            type="text"
            placeholder="Search tenant name or ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full rounded-xl border border-slate-800 bg-slate-950/60 py-2 pl-9 pr-4 text-xs text-slate-200 placeholder-slate-500 focus:border-purple-500 focus:outline-none"
          />
        </div>

        <select
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
          className="rounded-xl border border-slate-800 bg-slate-950/60 px-3 py-2 text-xs font-semibold text-slate-300 focus:border-purple-500 focus:outline-none"
        >
          <option value="ALL">All Plan Tiers</option>
          <option value="INSTITUTIONAL">INSTITUTIONAL</option>
          <option value="PRO">PRO</option>
          <option value="BASIC">BASIC</option>
        </select>
      </div>

      {/* Tenant Table */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="border-b border-slate-800 bg-slate-950/80 uppercase font-semibold text-slate-400">
              <tr>
                <th className="px-6 py-4">Tenant Info</th>
                <th className="px-6 py-4">Plan Tier</th>
                <th className="px-6 py-4">Users Count</th>
                <th className="px-6 py-4">Storage Usage</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/80">
              {filteredTenants.map((t) => {
                const storagePct = Math.min(100, Math.round((t.storage_used_gb / (t.storage_limit_gb || 50)) * 100));
                return (
                  <tr key={t.tenant_id} className="hover:bg-slate-900/80 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-semibold text-white">{t.name}</p>
                        <p className="text-slate-400 font-mono text-[11px]">{t.tenant_id} • {t.slug}</p>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 rounded-full border px-3 py-0.5 text-[10px] font-bold uppercase tracking-wider ${getTierBadge(t.plan_tier)}`}>
                        <Sparkles className="h-3 w-3" />
                        {t.plan_tier}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <div className="font-semibold text-white">
                        {t.active_users} / {t.max_users} Users
                      </div>
                    </td>

                    <td className="px-6 py-4 w-48">
                      <div className="space-y-1">
                        <div className="flex justify-between text-[11px]">
                          <span className="text-slate-400">{t.storage_used_gb} GB</span>
                          <span className="text-purple-400 font-semibold">{storagePct}%</span>
                        </div>
                        <div className="h-1.5 w-full rounded-full bg-slate-800 overflow-hidden">
                          <div className="h-full bg-purple-500 rounded-full" style={{ width: `${storagePct}%` }} />
                        </div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[10px] font-semibold uppercase ${
                        t.status === 'ACTIVE' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-rose-500/20 text-rose-300 border border-rose-500/30'
                      }`}>
                        <span className={`h-1.5 w-1.5 rounded-full ${t.status === 'ACTIVE' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
                        {t.status}
                      </span>
                    </td>

                    <td className="px-6 py-4 text-right">
                      {t.status === 'ACTIVE' ? (
                        <button
                          onClick={() => setConfirmModal({ tenant: t, action: 'suspend' })}
                          className="flex items-center gap-1 rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-1 text-xs font-semibold text-rose-300 hover:bg-rose-500/20 transition-all ml-auto"
                        >
                          <PauseCircle className="h-3.5 w-3.5" />
                          Suspend
                        </button>
                      ) : (
                        <button
                          onClick={() => setConfirmModal({ tenant: t, action: 'activate' })}
                          className="flex items-center gap-1 rounded-lg border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-emerald-300 hover:bg-emerald-500/20 transition-all ml-auto"
                        >
                          <PlayCircle className="h-3.5 w-3.5" />
                          Reactivate
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Tenant Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md space-y-6 rounded-2xl border border-slate-800 bg-slate-900 p-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-4">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Building2 className="h-5 w-5 text-purple-400" />
                Create New Enterprise Tenant
              </h3>
              <button onClick={() => setCreateModalOpen(false)} className="text-slate-400 hover:text-white">
                <X className="h-5 w-5" />
              </button>
            </div>

            <form onSubmit={handleCreateTenant} className="space-y-4 text-xs">
              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Tenant Name</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Apex Digital Capital"
                  value={newTenantName}
                  onChange={(e) => setNewTenantName(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-white placeholder-slate-500 focus:border-purple-500 focus:outline-none"
                />
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Subscription Plan Tier</label>
                <select
                  value={newTenantPlan}
                  onChange={(e) => setNewTenantPlan(e.target.value)}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-white focus:border-purple-500 focus:outline-none"
                >
                  <option value="PRO">PRO Tier (10 Users)</option>
                  <option value="INSTITUTIONAL">INSTITUTIONAL Tier (50 Users)</option>
                  <option value="BASIC">BASIC Tier (5 Users)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="font-semibold text-slate-300">Max Allowed Users Limit</label>
                <input
                  type="number"
                  min={1}
                  max={100}
                  value={newTenantMaxUsers}
                  onChange={(e) => setNewTenantMaxUsers(Number(e.target.value))}
                  className="w-full rounded-xl border border-slate-800 bg-slate-950 p-2.5 text-white focus:border-purple-500 focus:outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setCreateModalOpen(false)}
                  className="rounded-xl border border-slate-800 px-4 py-2 font-semibold text-slate-400 hover:bg-slate-800"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="rounded-xl bg-purple-600 px-5 py-2 font-semibold text-white shadow-lg shadow-purple-600/20 hover:bg-purple-500"
                >
                  Create Organization
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Suspend / Activate Confirmation Modal */}
      {confirmModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
          <div className="w-full max-w-md space-y-4 rounded-2xl border border-slate-800 bg-slate-900 p-6 text-center shadow-2xl">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <ShieldAlert className="h-6 w-6" />
            </div>

            <h3 className="text-lg font-bold text-white">Confirm Tenant {confirmModal.action === 'suspend' ? 'Suspension' : 'Reactivation'}</h3>
            <p className="text-xs text-slate-400">
              Are you sure you want to {confirmModal.action} <span className="font-semibold text-white">{confirmModal.tenant.name}</span> ({confirmModal.tenant.tenant_id})?
            </p>

            <div className="flex items-center justify-center gap-3 pt-2">
              <button
                onClick={() => setConfirmModal(null)}
                className="rounded-xl border border-slate-800 px-4 py-2 text-xs font-semibold text-slate-400 hover:bg-slate-800"
              >
                Cancel
              </button>
              <button
                onClick={handleToggleStatus}
                className={`rounded-xl px-5 py-2 text-xs font-semibold text-white shadow-lg ${
                  confirmModal.action === 'suspend' ? 'bg-rose-600 hover:bg-rose-500' : 'bg-emerald-600 hover:bg-emerald-500'
                }`}
              >
                Yes, {confirmModal.action.toUpperCase()}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
