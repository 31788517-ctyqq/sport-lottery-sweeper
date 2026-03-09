import { test, expect } from '@playwright/test';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

test.describe('User Management Live Regression (No Mock)', () => {
  test('should pass end-to-end checks with real backend and real auth session', async ({ page, request }) => {
    const loginResp = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
      data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
    });
    expect(loginResp.status()).toBe(200);

    const loginJson = await loginResp.json();
    expect(loginJson?.code).toBe(200);
    const loginData = loginJson?.data || {};
    const token = loginData?.access_token;
    expect(token).toBeTruthy();

    await page.addInitScript(({ accessToken, userInfo }) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('token', accessToken);
      localStorage.setItem('admin_token', accessToken);
      localStorage.setItem('admin_user', JSON.stringify(userInfo || {}));
    }, {
      accessToken: token,
      userInfo: loginData?.user_info || {}
    });

    const badApiResponses = [];
    const severeConsoleErrors = [];

    page.on('response', (resp) => {
      const url = resp.url();
      if (!url.includes('/api/')) return;
      const status = resp.status();
      if (status === 401 || status >= 500) {
        badApiResponses.push({ url, status });
      }
    });

    page.on('console', (msg) => {
      if (msg.type() !== 'error') return;
      const text = msg.text();
      if (text.includes('status code 401') || text.includes('status code 500') || text.includes('AxiosError')) {
        severeConsoleErrors.push(text);
      }
    });

    await page.goto('/admin/users/list');
    await expect(page.locator('.modern-table')).toBeVisible();

    await page.goto('/admin/users/roles');
    await expect(page.locator('.roles-card')).toBeVisible();

    await page.goto('/admin/users/departments');
    await expect(page.locator('.dept-tree-card')).toBeVisible();

    await page.goto('/admin/users/profile');
    await expect(page.locator('.profile-card')).toBeVisible();

    await page.goto('/admin/users/profiles');
    await expect(page.locator('.card-container')).toBeVisible();
    await expect(page.locator('.el-table')).toBeVisible();

    expect(badApiResponses, `Bad API responses: ${JSON.stringify(badApiResponses, null, 2)}`).toEqual([]);
    expect(severeConsoleErrors, `Severe console errors: ${JSON.stringify(severeConsoleErrors, null, 2)}`).toEqual([]);
  });
});

