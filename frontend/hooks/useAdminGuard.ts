'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface AdminUser {
  id: number;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  trading_mode?: string;
}

export function useAdminGuard() {
  const router = useRouter();
  const [user, setUser] = useState<AdminUser | null>(null);
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let isMounted = true;

    async function checkAdminAuth() {
      try {
        const res = await fetch('/api/auth/me', {
          headers: { 'Cache-Control': 'no-cache' }
        });

        if (!res.ok) {
          if (isMounted) {
            setLoading(false);
            router.push('/login');
          }
          return;
        }

        const data = await res.json();
        const currentUser: AdminUser = data.user || data;

        const role = (currentUser?.role || '').toUpperCase();
        const email = (currentUser?.email || '').toLowerCase();

        const isSuperAdmin = role === 'SUPER_ADMIN' || role === 'SUPERADMIN' || email === 'jiodkd@gmail.com';

        if (isMounted) {
          if (isSuperAdmin) {
            setUser(currentUser);
            setAuthorized(true);
          } else {
            setAuthorized(false);
            router.push('/403');
          }
          setLoading(false);
        }
      } catch (err) {
        console.error('Admin guard check failed:', err);
        if (isMounted) {
          setLoading(false);
          router.push('/login');
        }
      }
    }

    checkAdminAuth();

    return () => {
      isMounted = false;
    };
  }, [router]);

  return { user, loading, authorized };
}
