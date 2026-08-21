'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { useCurrency, SUPPORTED_CURRENCIES } from '@/context/CurrencyContext';
import { API_BASE_URL } from '@/lib/config';
import { resetPaperAccount, deleteUserAccount } from '@/services/api';
import { ArrowLeft, Upload, Camera, ShieldCheck, Sparkles, Check, Sliders, DollarSign, Globe, Coins } from 'lucide-react';

const AVATAR_PRESETS = [
  { label: 'Cyber Trader', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CyberTrader' },
  { label: 'Quantum AI', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=QuantumAI' },
  { label: 'Executive Slate', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=ExecutiveSlate' },
  { label: 'Crypto Bull', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=CryptoBull' },
  { label: 'Neon Pulse', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=NeonPulse' },
  { label: 'VIP Gold', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=VIPGold' }
];

export default function ProfilePage() {
  const { user, token, updateProfile, logout } = useAuth();
  const { currency, setCurrency, formatCurrency, currentCurrency } = useCurrency();

  const [name, setName] = useState(user?.name || '');
  const [avatar, setAvatar] = useState(user?.avatar || '');
  const [selectedCurrency, setSelectedCurrency] = useState(user?.currency || currency || 'USD');
  const [timezone, setTimezone] = useState(user?.timezone || 'Asia/Kolkata');
  const [tradingMode, setTradingMode] = useState(user?.trading_mode || 'Paper');

  // Agent POV Custom Preferences State
  const [defaultOrderSize, setDefaultOrderSize] = useState('1000');
  const [preferredLeverage, setPreferredLeverage] = useState('10');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');

  const [profileMsg, setProfileMsg] = useState('');
  const [profileErr, setProfileErr] = useState('');

  const [passwordMsg, setPasswordMsg] = useState('');
  const [passwordErr, setPasswordErr] = useState('');

  const [actionMsg, setActionMsg] = useState('');
  const [actionErr, setActionErr] = useState('');

  const [isUpdatingProfile, setIsUpdatingProfile] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const [isResettingAccount, setIsResettingAccount] = useState(false);
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteInput, setDeleteInput] = useState('');

  // Sync state when user profile is fetched
  useEffect(() => {
    if (user) {
      if (user.name) setName(user.name);
      if (user.avatar) setAvatar(user.avatar);
      if (user.timezone) setTimezone(user.timezone);
      if (user.trading_mode) setTradingMode(user.trading_mode);
      if (user.currency) {
        setSelectedCurrency(user.currency);
        setCurrency(user.currency);
      }
    }
  }, [user]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setProfileErr('Image file size must be less than 5MB.');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = async () => {
        if (typeof reader.result === 'string') {
          const imgData = reader.result;
          setAvatar(imgData);
          setProfileMsg('Custom photo loaded! Saving to profile...');
          // Immediate auto-save to prevent losing photo
          try {
            await updateProfile({
              name: name || user?.name,
              avatar: imgData,
              currency: selectedCurrency,
              timezone,
              trading_mode: tradingMode
            });
            setProfileMsg('Profile photo uploaded and permanently saved!');
          } catch (err: any) {
            setProfileMsg('Custom photo loaded. Click "Save Profile Changes" to persist.');
          }
        }
      };
      reader.readAsDataURL(file);
    }
  };

  const handleResetAccount = async () => {
    setActionMsg('');
    setActionErr('');
    setIsResettingAccount(true);
    try {
      const res = await resetPaperAccount();
      setActionMsg(res.message || 'Full Platform Paper trading account reset to default $10,000.00!');
      setShowResetConfirm(false);
      try {
        localStorage.removeItem('lumo_portfolio_cache');
        localStorage.removeItem('lumo_shadow_cache');
      } catch (e) {}
    } catch (err: any) {
      setActionErr(err.message || 'Failed to reset paper account.');
    } finally {
      setIsResettingAccount(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (deleteInput.trim().toUpperCase() !== 'DELETE') {
      setActionErr('Please type DELETE to confirm account deletion.');
      return;
    }
    setActionMsg('');
    setActionErr('');
    setIsDeletingAccount(true);
    try {
      await deleteUserAccount();
      logout();
    } catch (err: any) {
      setActionErr(err.message || 'Failed to delete account.');
      setIsDeletingAccount(false);
    }
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg('');
    setProfileErr('');
    setIsUpdatingProfile(true);

    try {
      setCurrency(selectedCurrency);
      await updateProfile({
        name,
        avatar,
        currency: selectedCurrency,
        timezone,
        trading_mode: tradingMode,
      });
      setProfileMsg('Profile details, photo, and currency preferences updated successfully!');
    } catch (err: any) {
      setProfileErr(err.message || 'Failed to update profile.');
    } finally {
      setIsUpdatingProfile(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg('');
    setPasswordErr('');

    if (newPassword !== confirmNewPassword) {
      setPasswordErr('New passwords do not match.');
      return;
    }

    setIsChangingPassword(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/change-password`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_new_password: confirmNewPassword,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || data.message || 'Password update failed');
      }

      setPasswordMsg('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (err: any) {
      setPasswordErr(err.message || 'Failed to change password.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
            <div className="flex items-center space-x-3">
              <Link
                href="/dashboard"
                className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition"
              >
                <ArrowLeft className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
                  <span>User Profile & Preferences</span>
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 font-mono">
                    {user?.role || 'TRADER'}
                  </span>
                </h1>
                <p className="text-xs text-slate-400">
                  Manage your personal account details, profile avatar, multi-currency settings, and security.
                </p>
              </div>
            </div>

            <button
              onClick={logout}
              className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
            >
              Sign Out
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* User Profile Card */}
            <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 flex flex-col items-center text-center space-y-4 shadow-xl">
              <div className="relative group">
                <img
                  src={avatar || 'https://api.dicebear.com/7.x/avataaars/svg?seed=LumoTrader'}
                  alt="User Avatar"
                  className="w-28 h-28 rounded-full bg-slate-800 border-2 border-cyan-500/40 p-1 shadow-2xl object-cover"
                />
                <label
                  htmlFor="user-avatar-upload"
                  className="absolute bottom-0 right-0 p-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 rounded-full cursor-pointer shadow-lg transition transform hover:scale-105"
                  title="Upload profile photo"
                >
                  <Camera className="w-4 h-4" />
                  <input
                    id="user-avatar-upload"
                    type="file"
                    accept="image/*"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>
              </div>

              <div>
                <h2 className="text-xl font-bold text-slate-100">{user?.name}</h2>
                <p className="text-xs text-slate-400 mt-0.5">{user?.email}</p>
              </div>

              <div className="w-full pt-4 border-t border-slate-800 space-y-2 text-xs text-slate-400">
                <div className="flex justify-between py-1">
                  <span>Display Currency</span>
                  <span className="font-semibold text-emerald-400 font-mono">
                    {currentCurrency.flag} {currentCurrency.code} ({currentCurrency.symbol})
                  </span>
                </div>
                <div className="flex justify-between py-1">
                  <span>Trading Mode</span>
                  <span className="font-semibold text-cyan-400">{user?.trading_mode}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span>Timezone</span>
                  <span className="font-semibold text-slate-200">{user?.timezone}</span>
                </div>
                <div className="flex justify-between py-1 border-t border-slate-800/60 pt-2">
                  <span>Account Status</span>
                  <span className="font-semibold text-emerald-400 flex items-center gap-1.5">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
                    <span>Active Account</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Profile Forms */}
            <div className="lg:col-span-2 space-y-8">
              {/* Account Details & Photo Customizer */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-slate-100 border-b border-slate-800 pb-3">Account Details & Profile Photo</h3>

                {profileMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-semibold">
                    {profileMsg}
                  </div>
                )}
                {profileErr && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-semibold">
                    {profileErr}
                  </div>
                )}

                <form onSubmit={handleUpdateProfile} className="space-y-5">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Full Name
                    </label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                    />
                  </div>

                  {/* Profile Photo Customizer */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider">
                        Profile Photo / Avatar
                      </label>
                      <label className="cursor-pointer bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition">
                        <Upload className="w-3.5 h-3.5" />
                        <span>Upload Photo from Device</span>
                        <input
                          type="file"
                          accept="image/*"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                      </label>
                    </div>

                    {/* Avatar Preset Grid */}
                    <div className="grid grid-cols-3 sm:grid-cols-6 gap-2 pt-1">
                      {AVATAR_PRESETS.map((preset) => {
                        const isSelected = avatar === preset.url;
                        return (
                          <button
                            key={preset.label}
                            type="button"
                            onClick={() => { setAvatar(preset.url); setProfileMsg(`Selected ${preset.label} avatar preset.`); }}
                            className={`p-2 rounded-xl border flex flex-col items-center gap-1 transition cursor-pointer ${
                              isSelected
                                ? 'bg-cyan-500/10 border-cyan-400 text-cyan-400'
                                : 'bg-slate-950 border-slate-800 hover:border-slate-700 text-slate-400'
                            }`}
                          >
                            <img src={preset.url} alt={preset.label} className="w-8 h-8 rounded-full" />
                            <span className="text-[10px] font-semibold truncate w-full text-center">{preset.label}</span>
                          </button>
                        );
                      })}
                    </div>

                    <input
                      type="text"
                      placeholder="Or paste external avatar URL..."
                      value={avatar}
                      onChange={(e) => setAvatar(e.target.value)}
                      className="w-full px-4 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-300 text-xs focus:outline-none focus:border-cyan-500 font-mono"
                    />
                  </div>

                  {/* Multi-Currency, Timezone & Trading Mode */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {/* Currency Selector */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Coins className="w-3.5 h-3.5 text-emerald-400" />
                        <span>Currency</span>
                      </label>
                      <select
                        value={selectedCurrency}
                        onChange={(e) => {
                          setSelectedCurrency(e.target.value);
                          setCurrency(e.target.value);
                        }}
                        className="w-full px-3 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-xs font-mono"
                      >
                        {SUPPORTED_CURRENCIES.map(c => (
                          <option key={c.code} value={c.code}>
                            {c.flag} {c.code} ({c.symbol}) - {c.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Timezone */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Globe className="w-3.5 h-3.5 text-cyan-400" />
                        <span>Timezone</span>
                      </label>
                      <select
                        value={timezone}
                        onChange={(e) => setTimezone(e.target.value)}
                        className="w-full px-3 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-xs font-mono"
                      >
                        <option value="Asia/Kolkata">Asia/Kolkata (IST +05:30)</option>
                        <option value="UTC">UTC (+00:00)</option>
                        <option value="America/New_York">America/New_York (EST)</option>
                        <option value="Europe/London">Europe/London (GMT)</option>
                        <option value="Asia/Dubai">Asia/Dubai (GST)</option>
                        <option value="Asia/Singapore">Asia/Singapore (SGT)</option>
                        <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                      </select>
                    </div>

                    {/* Trading Mode */}
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center gap-1">
                        <Sliders className="w-3.5 h-3.5 text-purple-400" />
                        <span>Trading Mode</span>
                      </label>
                      <select
                        value={tradingMode}
                        onChange={(e) => setTradingMode(e.target.value)}
                        className="w-full px-3 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-xs font-mono"
                      >
                        <option value="Paper">Paper Trading (Simulated)</option>
                        <option value="Live">Live Trading (Exchange API)</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isUpdatingProfile}
                    className="w-full py-3 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl text-sm transition transform active:scale-98 cursor-pointer flex items-center justify-center space-x-2"
                  >
                    {isUpdatingProfile ? (
                      <span>Saving Profile Changes...</span>
                    ) : (
                      <>
                        <Check className="w-4 h-4" />
                        <span>Save Profile & Currency Changes</span>
                      </>
                    )}
                  </button>
                </form>
              </div>

              {/* Password Management */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-slate-100 border-b border-slate-800 pb-3">Security & Password</h3>

                {passwordMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-semibold">
                    {passwordMsg}
                  </div>
                )}
                {passwordErr && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-semibold">
                    {passwordErr}
                  </div>
                )}

                <form onSubmit={handleChangePassword} className="space-y-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Current Password
                    </label>
                    <input
                      type="password"
                      required
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                        New Password
                      </label>
                      <input
                        type="password"
                        required
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                        Confirm New Password
                      </label>
                      <input
                        type="password"
                        required
                        value={confirmNewPassword}
                        onChange={(e) => setConfirmNewPassword(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isChangingPassword}
                    className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold rounded-xl text-sm transition"
                  >
                    {isChangingPassword ? 'Changing Password...' : 'Update Password'}
                  </button>
                </form>
              </div>

              {/* Danger Zone */}
              <div className="bg-rose-950/20 border border-rose-900/40 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-rose-400 border-b border-rose-900/40 pb-3">Danger Zone</h3>

                {actionMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-xs font-semibold">
                    {actionMsg}
                  </div>
                )}
                {actionErr && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-xs font-semibold">
                    {actionErr}
                  </div>
                )}

                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div>
                    <div className="font-semibold text-sm text-slate-200">Reset Paper Trading Account</div>
                    <div className="text-xs text-slate-400 mt-0.5">Wipe all simulated open positions and reset starting cash to $10,000.00.</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowResetConfirm(true)}
                    className="px-4 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-semibold transition"
                  >
                    Reset Paper Account
                  </button>
                </div>

                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
                  <div>
                    <div className="font-semibold text-sm text-rose-300">Delete User Account</div>
                    <div className="text-xs text-slate-400 mt-0.5">Permanently delete your account, API keys, journal, and trading history.</div>
                  </div>
                  <button
                    type="button"
                    onClick={() => setShowDeleteConfirm(true)}
                    className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
                  >
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Reset Confirmation Modal */}
        {showResetConfirm && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl max-w-md w-full space-y-4 shadow-2xl">
              <h4 className="text-lg font-bold text-slate-100">Reset Paper Account?</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                This will reset your paper trading balance back to 10,000.00 USDT, wipe all open positions, and clear simulated orders.
              </p>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowResetConfirm(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleResetAccount}
                  disabled={isResettingAccount}
                  className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-xl text-xs font-bold transition"
                >
                  {isResettingAccount ? 'Resetting...' : 'Confirm Reset'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Delete Confirmation Modal */}
        {showDeleteConfirm && (
          <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 z-50">
            <div className="bg-slate-900 border border-rose-900/50 p-6 rounded-2xl max-w-md w-full space-y-4 shadow-2xl">
              <h4 className="text-lg font-bold text-rose-400">Permanently Delete Account?</h4>
              <p className="text-xs text-slate-400 leading-relaxed">
                This action is irreversible. All trading history, strategy records, and configuration will be permanently purged.
              </p>
              <div>
                <label className="block text-xs font-semibold text-slate-300 mb-1">
                  Type <span className="text-rose-400 font-mono">DELETE</span> to confirm:
                </label>
                <input
                  type="text"
                  value={deleteInput}
                  onChange={(e) => setDeleteInput(e.target.value)}
                  placeholder="DELETE"
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-sm font-mono text-slate-100 focus:outline-none focus:border-rose-500"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowDeleteConfirm(false)}
                  className="px-4 py-2 bg-slate-800 text-slate-300 rounded-xl text-xs font-semibold hover:bg-slate-700 transition"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={handleDeleteAccount}
                  disabled={isDeletingAccount}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-xl text-xs font-bold transition"
                >
                  {isDeletingAccount ? 'Deleting...' : 'Permanently Delete'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </ProtectedRoute>
  );
}
