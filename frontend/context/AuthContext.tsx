'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface User {
  id: number;
  name: string;
  email: string;
  avatar: string;
  timezone: string;
  trading_mode: string;
  role?: string;
  plan?: string;
  plan_tier?: string;
}



interface AuthContextType {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (credentials: any) => Promise<void>;
  register: (userData: any) => Promise<void>;
  logout: () => Promise<void>;
  updateProfile: (profileData: any) => Promise<void>;
  refetchUser: () => Promise<void>;
}

import { API_BASE_URL } from '@/lib/config';
import { apiFetch } from '@/services/api';

const logAuthDebug = (endpoint: string, method: string) => {
  const origin = typeof window !== 'undefined' ? window.location.origin : 'SSR';
  const finalUrl = `${API_BASE_URL}${endpoint}`;
  console.log(`[AUTH_DEBUG]\nwindow.location.origin = ${origin}\nNEXT_PUBLIC_API_URL = ${process.env.NEXT_PUBLIC_API_URL}\nAPI_BASE_URL = ${API_BASE_URL}\nFinal Request URL = ${finalUrl}\nMethod = ${method}`);
};


const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const storedToken = localStorage.getItem('lumo_access_token');
    const storedUserData = localStorage.getItem('lumo_user_data');

    if (storedUserData) {
      try {
        setUser(JSON.parse(storedUserData));
      } catch (e) {
        console.warn('[AUTH] Error parsing stored user data:', e);
      }
    }

    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (authToken: string | null) => {
    const currentToken = authToken || localStorage.getItem('lumo_access_token');
    if (!currentToken) {
      setIsLoading(false);
      return;
    }

    try {
      logAuthDebug('/api/auth/me', 'GET');
      const res = await apiFetch('/api/auth/me');

      if (res.ok) {
        const data = await res.json();
        setUser(data.user);
        localStorage.setItem('lumo_user_data', JSON.stringify(data.user));
      }
    } catch (err) {
      console.warn('[AUTH] fetchUser background refresh warning:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials: any) => {
    setIsLoading(true);
    logAuthDebug('/api/auth/login', 'POST');
    const res = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(credentials),
      credentials: 'include',
    });

    const data = await res.json();
    if (!res.ok) {
      setIsLoading(false);
      throw new Error(data.detail || 'Login failed');
    }

    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('lumo_access_token', data.access_token);
    localStorage.setItem('lumo_user_data', JSON.stringify(data.user));
    setIsLoading(false);

    const userRole = (data.user?.role || '').toUpperCase();
    const userEmail = (data.user?.email || '').toLowerCase();
    const isSuperAdmin = userRole === 'SUPER_ADMIN' || userRole === 'SUPERADMIN' || userEmail === 'jiodkd@gmail.com';

    let redirectUrl = isSuperAdmin ? '/admin' : '/dashboard';
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const target = params.get('redirect');
      if (target) redirectUrl = target;
      window.location.href = redirectUrl;
    } else {
      router.push(redirectUrl);
    }
  };


  const register = async (userData: any) => {
    setIsLoading(true);
    logAuthDebug('/api/auth/register', 'POST');
    const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
      credentials: 'include',
    });

    const data = await res.json();
    if (!res.ok) {
      setIsLoading(false);
      throw new Error(data.detail || 'Registration failed');
    }

    setUser(data.user);
    setToken(data.access_token);
    localStorage.setItem('lumo_access_token', data.access_token);
    localStorage.setItem('lumo_user_data', JSON.stringify(data.user));
    setIsLoading(false);

    if (typeof window !== 'undefined') {
      window.location.href = '/dashboard';
    } else {
      router.push('/dashboard');
    }


  };

  const logout = async () => {
    try {
      logAuthDebug('/api/auth/logout', 'POST');
      await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        credentials: 'include',
      });
    } catch (e) {
      // Ignore network errors on logout
    }
    setUser(null);
    setToken(null);
    localStorage.removeItem('lumo_access_token');
    localStorage.removeItem('lumo_user_data');
    router.push('/login');
  };


  const updateProfile = async (profileData: any) => {
    logAuthDebug('/api/auth/profile', 'PUT');
    const res = await fetch(`${API_BASE_URL}/api/auth/profile`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        Authorization: token ? `Bearer ${token}` : '',
      },
      body: JSON.stringify(profileData),
      credentials: 'include',
    });


    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Profile update failed');
    }

    setUser(data.user);
  };

  const refetchUser = async () => {
    if (token) {
      await fetchUser(token);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        login,
        register,
        logout,
        updateProfile,
        refetchUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
