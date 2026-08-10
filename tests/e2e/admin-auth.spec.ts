import { test, expect } from '@playwright/test';

test.describe('Phase 27 — Secure Super Admin Authentication & RBAC Guards', () => {
  test('Unauthenticated user visiting /admin is redirected to /login', async ({ page }) => {
    // Clear cookies
    await page.context().clearCookies();
    await page.goto('/admin');
    await expect(page).toHaveURL(/\/login/);
  });

  test('Non-super-admin user visiting /admin is redirected to /403', async ({ page }) => {
    // Mock user response returning regular trader role
    await page.route('/api/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          user: {
            id: 99,
            name: 'Regular Trader',
            email: 'trader@lumo.trade',
            role: 'trader'
          }
        })
      });
    });

    // Set auth cookie
    await page.context().addCookies([{
      name: 'lumo_access_token',
      value: 'mock_regular_token',
      domain: 'localhost',
      path: '/'
    }]);

    await page.goto('/admin');
    await expect(page).toHaveURL(/\/403/);
  });

  test('Super Admin user can access /admin, /admin/system, and /admin/ai-governance', async ({ page }) => {
    // Mock user response returning SUPER_ADMIN role
    await page.route('/api/auth/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'success',
          user: {
            id: 1,
            name: 'Platform Super Admin',
            email: 'jiodkd@gmail.com',
            role: 'SUPER_ADMIN'
          }
        })
      });
    });

    // Mock system health response
    await page.route('/api/admin/system-health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'HEALTHY',
          api_latency_ms: 12,
          db_status: 'CONNECTED',
          uptime_pct: 99.99
        })
      });
    });

    // Set auth cookie
    await page.context().addCookies([{
      name: 'lumo_access_token',
      value: 'mock_super_admin_token',
      domain: 'localhost',
      path: '/'
    }]);

    // Access /admin
    await page.goto('/admin');
    await expect(page.locator('h1')).toContainText('Executive Dashboard');

    // Access /admin/system
    await page.goto('/admin/system');
    await expect(page.locator('h1')).toContainText('System Health Console');

    // Access /admin/ai-governance
    await page.goto('/admin/ai-governance');
    await expect(page.locator('h1')).toContainText('AI Governance Console');
  });
});
