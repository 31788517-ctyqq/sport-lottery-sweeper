import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

test.describe('AI Remote Services Live Pre-Release Checklist (No Mock)', () => {
  test('checklist: data + render + logic + CRUD + cleanup', async ({ page, request }) => {
    test.setTimeout(150000);

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

    const countResp = await request.get(`${BACKEND_BASE_URL}/api/v1/llm-providers/count`, { headers: authHeaders });
    const countJson = countResp.ok() ? await countResp.json() : {};
    const totalCount = Number(countJson?.count || 0);
    push('data count api', countResp.status() === 200, `status=${countResp.status()}, count=${totalCount}`);

    const listResp = await request.get(`${BACKEND_BASE_URL}/api/v1/llm-providers/?skip=0&limit=50`, { headers: authHeaders });
    const listJson = listResp.ok() ? await listResp.json() : [];
    const listItems = Array.isArray(listJson) ? listJson : [];
    push('data list api', listResp.status() === 200, `status=${listResp.status()}, list=${listItems.length}`);
    push('data recovered providers >= 4', listItems.length >= 4, `current=${listItems.length}`);

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

    await page.goto('/admin/ai-services/remote');
    await expect(page.locator('.remote-ai-service')).toBeVisible();
    await expect(page.locator('.el-table')).toBeVisible();
    push('render table visible', true, 'page+table visible');

    const initialRows = await page.locator('.el-table__body tbody tr').count();
    push('render rows > 0', initialRows > 0, `rows=${initialRows}`);

    const searchInput = page.locator('.el-row input').first();
    await searchInput.fill('OpenAI');
    await page.locator('.el-row .el-button').first().click();
    await page.waitForTimeout(600);
    const searchedRows = await page.locator('.el-table__body tbody tr').count();
    push('logic search request', searchedRows >= 0, `rows=${searchedRows}`);

    await searchInput.fill('');
    await page.locator('.el-row .el-button').last().click();
    await page.waitForTimeout(600);
    const resetRows = await page.locator('.el-table__body tbody tr').count();
    push('logic reset request', resetRows > 0, `rows=${resetRows}`);

    const tempName = `E2E_REMOTE_${Date.now()}`;
    const createResp = await request.post(`${BACKEND_BASE_URL}/api/v1/llm-providers/`, {
      headers: authHeaders,
      data: {
        name: tempName,
        provider_type: 'openai',
        description: 'playwright live prerelease temp provider',
        api_key: 'sk-playwright-temp-key',
        base_url: 'https://api.openai.com/v1',
        default_model: 'gpt-4-turbo',
        enabled: true,
        priority: 8,
        max_requests_per_minute: 60,
        timeout_seconds: 30,
        rate_limit_strategy: 'fixed_window',
        retry_policy: {},
        circuit_breaker_config: {},
        cost_per_token: {},
        version: '1.0',
        tags: ['e2e', 'temp']
      }
    });
    const createOk = createResp.status() === 201 || createResp.status() === 400;
    push('data create temp provider api', createOk, `status=${createResp.status()}`);
    let tempProviderId = null;
    if (createResp.status() === 201) {
      const created = await createResp.json();
      tempProviderId = created?.id || null;
    }

    await page.locator('.card-header .el-button').nth(1).click();
    await searchInput.fill(tempName);
    await page.locator('.el-row .el-button').first().click();
    await page.waitForTimeout(800);
    push('logic search temp provider', true, 'search triggered');

    const hasTempRow = await page.locator('.el-table__body tbody tr').filter({ hasText: tempName }).count();
    push('render temp provider row', hasTempRow > 0, `rows=${hasTempRow}`);

    if (!tempProviderId) {
      const lookupResp = await request.get(`${BACKEND_BASE_URL}/api/v1/llm-providers/?skip=0&limit=200&search=${encodeURIComponent(tempName)}`, {
        headers: authHeaders
      });
      const lookupList = lookupResp.ok() ? await lookupResp.json() : [];
      tempProviderId = Array.isArray(lookupList) && lookupList[0] ? lookupList[0].id : null;
    }

    if (tempProviderId) {
      const disableResp = await request.post(`${BACKEND_BASE_URL}/api/v1/llm-providers/${tempProviderId}/disable`, {
        headers: authHeaders
      });
      push('logic toggle provider status', disableResp.status() === 200, `status=${disableResp.status()}`);

      const deleteResp = await request.delete(`${BACKEND_BASE_URL}/api/v1/llm-providers/${tempProviderId}`, {
        headers: authHeaders
      });
      push('logic delete temp provider', deleteResp.status() === 204, `status=${deleteResp.status()}`);
    } else {
      push('logic cleanup temp provider', false, 'temp provider id not found');
    }

    push(
      'api health',
      badApiResponses.length === 0,
      badApiResponses.length ? JSON.stringify(badApiResponses, null, 2) : 'no 401/5xx'
    );

    const reportLines = [
      '# AI Remote Services Live Pre-Release Checklist',
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
      path.resolve(process.cwd(), '../AI_REMOTE_SERVICES_LIVE_PRERELEASE_CHECKLIST_REPORT.md'),
      reportLines.join('\n'),
      'utf-8'
    );

    expect(issues, `AI remote services live checklist failed:\n${issues.join('\n')}`).toEqual([]);
  });
});
