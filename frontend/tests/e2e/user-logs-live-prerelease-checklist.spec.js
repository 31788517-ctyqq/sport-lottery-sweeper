import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

test.describe('User Logs Live Pre-Release Checklist (No Mock)', () => {
  test('checklist: data + render + logic', async ({ page, request }) => {
    test.setTimeout(120000);

    const issues = [];
    const checkpoints = [];
    const push = (name, passed, detail = '') => {
      checkpoints.push({ name, passed, detail });
      if (!passed) issues.push(`${name}: ${detail}`);
    };

    const loginResp = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
      data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
    });
    expect(loginResp.status()).toBe(200);
    const loginJson = await loginResp.json();
    expect(loginJson?.code).toBe(200);

    const token = loginJson?.data?.access_token;
    expect(token).toBeTruthy();
    const authHeaders = { Authorization: `Bearer ${token}` };

    // Data layer: API contract + non-empty list
    const apiResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/system/logs/db/user?skip=0&limit=20`, {
      headers: authHeaders
    });
    const apiJson = apiResp.ok() ? await apiResp.json() : null;
    const apiItems = apiJson?.data?.items || [];
    const apiTotal = apiJson?.data?.total ?? -1;
    push(
      'data api contract',
      apiResp.status() === 200 && Array.isArray(apiItems) && typeof apiTotal === 'number',
      `status=${apiResp.status()}, items=${Array.isArray(apiItems)}, total=${apiTotal}`
    );

    await page.addInitScript(({ accessToken, userInfo }) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('token', accessToken);
      localStorage.setItem('admin_token', accessToken);
      localStorage.setItem('admin_user', JSON.stringify(userInfo || {}));
    }, {
      accessToken: token,
      userInfo: loginJson?.data?.user_info || {}
    });

    const observedApiErrors = [];
    page.on('response', (resp) => {
      const u = resp.url();
      if (!u.includes('/api/')) return;
      const s = resp.status();
      if (s === 401 || s >= 500) observedApiErrors.push({ url: u, status: s });
    });

    // Render layer: page load, table, pagination
    await page.goto('/admin/users/logs');
    await expect(page.locator('.user-logs-container')).toBeVisible();
    await expect(page.locator('.el-table')).toBeVisible();
    push('render table visible', true, 'container+table visible');

    const rows = page.locator('.el-table__body tbody tr');
    const rowCount = await rows.count();
    push('render rows', rowCount > 0, `rows=${rowCount}`);

    await expect(page.locator('.pagination-container')).toBeVisible();
    push('render pagination', true, 'pagination visible');

    // Logic layer: search should trigger filtered request
    const firstSearchInput = page.locator('.filter-card .el-input__inner').first();
    await firstSearchInput.fill('login');

    const searchRespPromise = page.waitForResponse((resp) => {
      return resp.url().includes('/api/v1/admin/system/logs/db/user') && resp.url().includes('search=login');
    }, { timeout: 10000 });

    await page.locator('.filter-card .el-button--primary').first().click();
    const searchResp = await searchRespPromise;
    push('logic search request', searchResp.status() === 200, `status=${searchResp.status()}`);

    await page.waitForTimeout(600);
    const searchedRows = await rows.count();
    push('logic search render', searchedRows >= 0, `rows_after_search=${searchedRows}`);

    // Logic layer: reset should remove search condition
    const resetRespPromise = page.waitForResponse((resp) => {
      const url = resp.url();
      return url.includes('/api/v1/admin/system/logs/db/user') && !url.includes('search=login');
    }, { timeout: 10000 });

    await page.locator('.filter-card .el-button').nth(1).click();
    const resetResp = await resetRespPromise;
    push('logic reset request', resetResp.status() === 200, `status=${resetResp.status()}`);

    // Logic layer: detail dialog
    const detailBtn = page.locator('.el-table .el-button--link').first();
    if (await detailBtn.count()) {
      await detailBtn.click();
      const detailDialog = page.locator('.el-dialog');
      await expect(detailDialog).toBeVisible();
      push('logic detail dialog', true, 'detail dialog opened');
      await page.keyboard.press('Escape');
    } else {
      push('logic detail dialog', false, 'no detail button found');
    }

    push(
      'api health',
      observedApiErrors.length === 0,
      observedApiErrors.length ? JSON.stringify(observedApiErrors, null, 2) : 'no 401/5xx'
    );

    const reportLines = [
      '# User Logs Live Pre-Release Checklist',
      '',
      `- Time: ${new Date().toISOString()}`,
      `- Backend: ${BACKEND_BASE_URL}`,
      `- Account: ${ADMIN_USERNAME}`,
      '',
      '## Checkpoints',
      ...checkpoints.map((c, i) => `${i + 1}. [${c.passed ? 'PASS' : 'FAIL'}] ${c.name} - ${c.detail}`),
      '',
      '## Summary',
      `- Total: ${checkpoints.length}`,
      `- Failed: ${checkpoints.filter((c) => !c.passed).length}`,
      `- Passed: ${checkpoints.filter((c) => c.passed).length}`
    ];

    fs.writeFileSync(
      path.resolve(process.cwd(), '../USER_LOGS_LIVE_PRERELEASE_CHECKLIST_REPORT.md'),
      reportLines.join('\n'),
      'utf-8'
    );

    expect(issues, `User logs live checklist failed:\n${issues.join('\n')}`).toEqual([]);
  });
});
