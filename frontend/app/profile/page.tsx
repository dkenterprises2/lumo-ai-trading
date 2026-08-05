'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';
import { useAuth } from '@/context/AuthContext';
import { API_BASE_URL } from '@/lib/config';
import { resetPaperAccount, deleteUserAccount } from '@/services/api';
import { ArrowLeft, Upload, Camera, ShieldCheck, Sparkles, Check, Sliders } from 'lucide-react';

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

  const [name, setName] = useState(user?.name || '');
  const [avatar, setAvatar] = useState(user?.avatar || '');
  const [timezone, setTimezone] = useState(user?.timezone || 'UTC');
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

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 3 * 1024 * 1024) {
        setProfileErr('Image file size must be less than 3MB.');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        if (typeof reader.result === 'string') {
          setAvatar(reader.result);
          setProfileMsg('Custom photo loaded into live preview. Click "Save Profile Changes" to update!');
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
      setActionMsg(res.message || 'Paper trading account reset to default $10,000.00!');
      setShowResetConfirm(false);
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
      await updateProfile({
        name,
        avatar,
        timezone,
        trading_mode: tradingMode,
      });
      setProfileMsg('Profile details and photo updated successfully!');
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
          Authorization: token ? `Bearer ${token}` : '',
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_new_password: confirmNewPassword,
        }),
        credentials: 'include',
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Password change failed.');
      }

      setPasswordMsg('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmNewPassword('');
    } catch (err: any) {
      setPasswordErr(err.message || 'Password change failed.');
    } finally {
      setIsChangingPassword(false);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950 text-slate-100 p-6 lg:p-10">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Top Bar with Back Button */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-6">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-slate-300 hover:text-cyan-400 rounded-xl text-xs font-semibold transition shadow-md"
              >
                <ArrowLeft className="h-4 w-4" />
                <span>Back to Terminal</span>
              </Link>
              <div>
                <h1 className="text-2xl lg:text-3xl font-bold text-slate-100">User Profile</h1>
                <p className="text-slate-400 text-xs mt-0.5">Manage your account preferences, photo, credentials, and trading rules</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/20 rounded-xl text-xs font-semibold transition-colors"
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
                            className={`p-2 rounded-xl border flex flex-col items-center gap-1 transition ${
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

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                        Timezone
                      </label>
                      <select
                        value={timezone}
                        onChange={(e) => setTimezone(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                      >
                        <option value="UTC">UTC</option>
                        <option value="America/New_York">America/New_York (EST)</option>
                        <option value="Europe/London">Europe/London (GMT)</option>
                        <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
                        <option value="Asia/Kolkata">Asia/Kolkata (IST)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                        Trading Mode
                      </label>
                      <select
                        value={tradingMode}
                        onChange={(e) => setTradingMode(e.target.value)}
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500 text-sm"
                      >
                        <option value="Paper">Paper Trading (Simulated)</option>
                        <option value="Live">Live Trading (Exchange API)</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isUpdatingProfile}
                    className="py-3 px-6 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-xl transition-colors text-xs uppercase tracking-wider disabled:opacity-50 shadow-lg shadow-cyan-500/20"
                  >
                    {isUpdatingProfile ? 'Saving...' : 'Save Profile Changes'}
                  </button>
                </form>
              </div>

              {/* Agent Point of View: Execution & Trading Preferences Card */}
              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4">
                <h3 className="text-lg font-semibold text-slate-100 border-b border-slate-800 pb-3 flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-cyan-400" />
                  <span>Execution & Trading Rules (Agent POV Recommendations)</span>
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                    <label className="block text-[11px] font-semibold text-slate-400">Default Allocation ($ USDT)</label>
                    <input
                      type="number"
                      value={defaultOrderSize}
                      onChange={(e) => setDefaultOrderSize(e.target.value)}
                      className="w-full bg-transparent text-slate-100 font-bold text-sm focus:outline-none"
                    />
                  </div>

                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                    <label className="block text-[11px] font-semibold text-slate-400">Preferred Leverage</label>
                    <select
                      value={preferredLeverage}
                      onChange={(e) => setPreferredLeverage(e.target.value)}
                      className="w-full bg-transparent text-slate-100 font-bold text-sm focus:outline-none"
                    >
                      <option value="1" className="bg-slate-900">1x (Spot)</option>
                      <option value="2" className="bg-slate-900">2x</option>
                      <option value="5" className="bg-slate-900">5x</option>
                      <option value="10" className="bg-slate-900">10x</option>
                      <option value="20" className="bg-slate-900">20x</option>
                    </select>
                  </div>

                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 flex flex-col justify-between">
                    <label className="block text-[11px] font-semibold text-slate-400">Execution Sound Alerts</label>
                    <button
                      type="button"
                      onClick={() => setNotificationsEnabled(!notificationsEnabled)}
                      className={`text-xs font-bold px-2 py-1 rounded-lg w-fit transition ${
                        notificationsEnabled ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {notificationsEnabled ? 'Enabled' : 'Disabled'}
                    </button>
                  </div>
                </div>
              </div>


              {/* Change Password Form */}


              <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-slate-100 border-b border-slate-800 pb-3">Change Security Password</h3>

                {passwordMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-sm">
                    {passwordMsg}
                  </div>
                )}
                {passwordErr && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm">
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
                      className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500"
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
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500"
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
                        className="w-full px-4 py-3 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 focus:outline-none focus:border-cyan-500"
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={isChangingPassword}
                    className="py-3 px-6 bg-slate-800 hover:bg-slate-700 text-slate-100 font-semibold rounded-xl transition-colors disabled:opacity-50"
                  >
                    {isChangingPassword ? 'Updating Password...' : 'Update Password'}
                  </button>
                </form>
              </div>

              {/* Danger Zone & Account Management */}
              <div className="bg-slate-900/80 border border-rose-500/30 rounded-2xl p-6 space-y-6">
                <h3 className="text-lg font-semibold text-rose-400 border-b border-slate-800 pb-3 flex items-center gap-2">
                  <span>Danger Zone & Account Management</span>
                </h3>

                {actionMsg && (
                  <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded-xl text-sm">
                    {actionMsg}
                  </div>
                )}
                {actionErr && (
                  <div className="p-3 bg-rose-500/10 border border-rose-500/20 text-rose-400 rounded-xl text-sm">
                    {actionErr}
                  </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Option 1: Reset Paper Account */}
                  <div className="p-4 bg-slate-950/60 border border-slate-800 rounded-xl space-y-3">
                    <div>
                      <h4 className="font-bold text-slate-200 text-sm">Reset Paper Account</h4>
                      <p className="text-xs text-slate-400 mt-1">
                        Resets paper wallet balance back to default $10,000.00 USDT and clears all open positions & trade history.
                      </p>
                    </div>
                    {!showResetConfirm ? (
                      <button
                        type="button"
                        onClick={() => { setActionMsg(''); setActionErr(''); setShowResetConfirm(true); }}
                        className="w-full py-2.5 px-4 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded-xl text-xs font-semibold transition"
                      >
                        Reset Paper Account to Default ($10,000)
                      </button>
                    ) : (
                      <div className="space-y-2 pt-2 border-t border-slate-800">
                        <p className="text-xs text-amber-400 font-semibold">Confirm reset to $10,000 USDT default?</p>
                        <div className="flex gap-2">
                          <button
                            type="button"
                            disabled={isResettingAccount}
                            onClick={handleResetAccount}
                            className="flex-1 py-2 px-3 bg-amber-500 hover:bg-amber-600 text-slate-950 text-xs font-bold rounded-lg transition disabled:opacity-50"
                          >
                            {isResettingAccount ? 'Resetting...' : 'Yes, Reset Now'}
                          </button>
                          <button
                            type="button"
                            onClick={() => setShowResetConfirm(false)}
                            className="py-2 px-3 bg-slate-800 text-slate-300 text-xs font-semibold rounded-lg hover:bg-slate-700 transition"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Option 2: Delete Account */}
                  <div className="p-4 bg-slate-950/60 border border-rose-500/20 rounded-xl space-y-3">
                    <div>
                      <h4 className="font-bold text-rose-400 text-sm">Delete Account Permanently</h4>
                      <p className="text-xs text-slate-400 mt-1">
                        Permanently deletes your account credentials, API keys, sessions, and all trading data.
                      </p>
                    </div>
                    {!showDeleteConfirm ? (
                      <button
                        type="button"
                        onClick={() => { setActionMsg(''); setActionErr(''); setShowDeleteConfirm(true); }}
                        className="w-full py-2.5 px-4 bg-rose-500/10 hover:bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded-xl text-xs font-semibold transition"
                      >
                        Delete Account
                      </button>
                    ) : (
                      <div className="space-y-2 pt-2 border-t border-slate-800">
                        <p className="text-[11px] text-rose-400 font-semibold">Type DELETE to confirm permanent deletion:</p>
                        <input
                          type="text"
                          placeholder="Type DELETE"
                          value={deleteInput}
                          onChange={(e) => setDeleteInput(e.target.value)}
                          className="w-full px-3 py-1.5 bg-slate-950 border border-rose-500/40 rounded-lg text-xs text-slate-100 focus:outline-none"
                        />
                        <div className="flex gap-2">
                          <button
                            type="button"
                            disabled={isDeletingAccount || deleteInput.trim().toUpperCase() !== 'DELETE'}
                            onClick={handleDeleteAccount}
                            className="flex-1 py-2 px-3 bg-rose-600 hover:bg-rose-500 text-white text-xs font-bold rounded-lg transition disabled:opacity-40"
                          >
                            {isDeletingAccount ? 'Deleting...' : 'Permanently Delete'}
                          </button>
                          <button
                            type="button"
                            onClick={() => { setShowDeleteConfirm(false); setDeleteInput(''); }}
                            className="py-2 px-3 bg-slate-800 text-slate-300 text-xs font-semibold rounded-lg hover:bg-slate-700 transition"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
}

