import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

test.describe('Operation Logs Live Pre-Release Checklist (No Mock)', () => {
  test('checklist: data + render + logic + export + cleanup', async ({ page, request }) => {
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

    // Data layer: contract
    const apiResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/system/logs/db/user?skip=0&limit=20`, {
      headers: authHeaders
    });
    const apiJson = apiResp.ok() ? await apiResp.json() : null;
    const apiItems = apiJson?.data?.items || [];
    push(
      'data api contract',
      apiResp.status() === 200 && Array.isArray(apiItems),
      `status=${apiResp.status()}, items=${Array.isArray(apiItems) ? apiItems.length : 'invalid'}`
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

    const badApiResponses = [];
    page.on('response', (resp) => {
      const url = resp.url();
      if (!url.includes('/api/')) return;
      const status = resp.status();
      if (status === 401 || status >= 500) badApiResponses.push({ url, status });
    });

    await page.goto('/admin/users/logs');
    await expect(page.locator('.operation-log-container')).toBeVisible();
    await expect(page.locator('.modern-table')).toBeVisible();
    push('render main table', true, 'page+table visible');

    const initialRows = await page.locator('.modern-table .el-table__body tbody tr').count();
    push('render rows', initialRows > 0, `rows=${initialRows}`);

    // Logic: search + reset
    const searchInput = page.locator('.search-input input').first();
    await searchInput.fill('login');

    const searchRespPromise = page.waitForResponse((resp) => {
      const url = resp.url();
      return url.includes('/api/v1/admin/system/logs/db/user') && url.includes('search=login');
    }, { timeout: 10000 });

    await page.locator('.logs-controls .action-btn').first().click();
    const searchResp = await searchRespPromise;
    push('logic search request', searchResp.status() === 200, `status=${searchResp.status()}`);

    const resetRespPromise = page.waitForResponse((resp) => {
      const url = resp.url();
      return url.includes('/api/v1/admin/system/logs/db/user') && !url.includes('search=login');
    }, { timeout: 10000 });

    await page.locator('.logs-controls .action-btn').nth(1).click();
    const resetResp = await resetRespPromise;
    push('logic reset request', resetResp.status() === 200, `status=${resetResp.status()}`);

    // Logic: detail dialog
    const firstRow = page.locator('.modern-table .el-table__body tbody tr').first();
    const firstRowBtns = firstRow.locator('button');
    if (await firstRowBtns.count()) {
      await firstRowBtns.first().click();
      await expect(page.locator('.el-dialog')).toBeVisible();
      push('logic detail dialog', true, 'detail opened');
      await page.keyboard.press('Escape');
      await page.waitForTimeout(300);
    } else {
      push('logic detail dialog', false, 'no row action button');
    }

    // Export: backend + UI trigger
    const directExportResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/system/logs/export?skip=0&limit=100`, {
      headers: authHeaders
    });
    const directExportCt = directExportResp.headers()['content-type'] || '';
    push(
      'data export endpoint',
      directExportResp.status() === 200 && directExportCt.includes('text/csv'),
      `status=${directExportResp.status()}, content-type=${directExportCt}`
    );

    let uiExportOk = false;
    let uiExportDetail = '';
    try {
      const uiExportRespPromise = page.waitForResponse((resp) => resp.url().includes('/api/v1/admin/system/logs/export'), { timeout: 10000 });
      await page.locator('.header-actions .el-button').first().click();
      const uiExportResp = await uiExportRespPromise;
      uiExportOk = uiExportResp.status() === 200;
      uiExportDetail = `status=${uiExportResp.status()}`;
    } catch {
      uiExportDetail = 'export response not captured';
    }
    push('logic export button', uiExportOk, uiExportDetail);

    // Cleanup: use keep latest 10000 to minimize data impact
    await page.locator('.header-actions .el-button').nth(1).click();
    const cleanupDialog = page.locator('.el-dialog:has(.el-radio-group)');
    await expect(cleanupDialog).toBeVisible();
    const radios = cleanupDialog.locator('.el-radio');
    if ((await radios.count()) >= 2) {
      await radios.nth(1).click();
    }

    const cleanupRespPromise = page.waitForResponse((resp) => resp.url().includes('/api/v1/admin/system/logs/db/user/clear'), { timeout: 10000 });
    await cleanupDialog.locator('.el-button--danger').last().click();
    const cleanupResp = await cleanupRespPromise;
    push('logic cleanup request', cleanupResp.status() === 200, `status=${cleanupResp.status()}`);

    push(
      'api health',
      badApiResponses.length === 0,
      badApiResponses.length ? JSON.stringify(badApiResponses, null, 2) : 'no 401/5xx'
    );

    const reportLines = [
      '# Operation Logs Live Pre-Release Checklist',
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
      path.resolve(process.cwd(), '../USER_OPERATION_LOGS_LIVE_PRERELEASE_CHECKLIST_REPORT.md'),
      reportLines.join('\n'),
      'utf-8'
    );

    expect(issues, `Operation logs live checklist failed:\n${issues.join('\n')}`).toEqual([]);
  });
});
