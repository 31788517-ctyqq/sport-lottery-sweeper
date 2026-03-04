import { test, expect } from '@playwright/test';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';
const FRONTEND_PATH = '/admin/match-data/schedule/jczq';

function todayStr() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

test.describe('JCZQ 500W smoke', () => {
  test('click import button and verify today schedule rows', async ({ page, request }) => {
    test.setTimeout(120000);

    const date = todayStr();

    const loginResp = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
      data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
    });
    expect(loginResp.status()).toBe(200);
    const loginJson = await loginResp.json();
    expect(loginJson?.code).toBe(200);

    const token = loginJson?.data?.access_token;
    expect(token).toBeTruthy();

    const authHeaders = { Authorization: `Bearer ${token}` };
    const listUrl = `${BACKEND_BASE_URL}/api/v1/admin/lottery-schedules/lottery-schedules/`;

    const beforeResp = await request.get(listUrl, {
      headers: authHeaders,
      params: { page: 1, size: 20, date_from: date, date_to: date }
    });
    expect(beforeResp.status()).toBe(200);
    const beforeJson = await beforeResp.json();
    const beforeTotal = beforeJson?.data?.total ?? 0;

    await page.addInitScript(({ accessToken, userInfo }) => {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('token', accessToken);
      localStorage.setItem('admin_token', accessToken);
      localStorage.setItem('admin_user', JSON.stringify(userInfo || {}));
    }, {
      accessToken: token,
      userInfo: loginJson?.data?.user_info || {}
    });

    await page.goto(FRONTEND_PATH);
    await expect(page.getByRole('button', { name: '从500W获取竞彩赛程' })).toBeVisible();

    const importRespPromise = page.waitForResponse((resp) => {
      return resp.url().includes('/api/v1/admin/lottery-schedules/lottery-schedules/import/500w') && resp.request().method() === 'POST';
    }, { timeout: 30000 });

    await page.getByRole('button', { name: '从500W获取竞彩赛程' }).click();
    const importResp = await importRespPromise;
    expect(importResp.status()).toBe(200);

    const importJson = await importResp.json();
    expect(importJson?.success).toBeTruthy();

    const afterResp = await request.get(listUrl, {
      headers: authHeaders,
      params: { page: 1, size: 50, date_from: date, date_to: date }
    });
    expect(afterResp.status()).toBe(200);
    const afterJson = await afterResp.json();
    const afterTotal = afterJson?.data?.total ?? 0;
    const importedCount = importJson?.data?.imported_count ?? 0;
    const updatedCount = importJson?.data?.updated_count ?? 0;
    const changedCount = importedCount + updatedCount;

    expect(afterTotal).toBeGreaterThanOrEqual(beforeTotal);

    await page.getByRole('button', { name: '查询' }).click();
    if (changedCount > 0 || afterTotal > 0) {
      const firstRow = page.locator('.el-table__body tbody tr').first();
      await expect(firstRow).toBeVisible({ timeout: 10000 });
      await expect(firstRow).toContainText(date);
    } else {
      await expect(page.locator('.el-table__empty-text')).toContainText(/No Data|暂无数据/i);
    }
  });
});
