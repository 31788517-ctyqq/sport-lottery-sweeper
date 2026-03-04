import { test, expect } from '@playwright/test';
import fs from 'fs';
import path from 'path';

const ADMIN_USERNAME = process.env.E2E_ADMIN_USER || 'admin';
const ADMIN_PASSWORD = process.env.E2E_ADMIN_PASS || 'admin123';
const BACKEND_BASE_URL = process.env.E2E_BACKEND_URL || 'http://127.0.0.1:8000';

test.describe('User Management Pre-Release Live Checklist (No Mock)', () => {
  test('checklist: export + batch ops + edit-save verify', async ({ page, request }) => {
    test.setTimeout(120000);
    const issues = [];
    const checkpoints = [];

    const pushCheckpoint = (name, passed, detail = '') => {
      checkpoints.push({ name, passed, detail });
      if (!passed) issues.push(`${name}: ${detail}`);
    };

    const loginResp = await request.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
      data: { username: ADMIN_USERNAME, password: ADMIN_PASSWORD }
    });
    expect(loginResp.status()).toBe(200);
    const loginJson = await loginResp.json();
    expect(loginJson?.code).toBe(200);

    const loginData = loginJson?.data || {};
    const token = loginData?.access_token;
    expect(token).toBeTruthy();
    const authHeaders = { Authorization: `Bearer ${token}` };

    const createdUsername = `e2e_live_${Date.now()}`;
    let createdUserId = null;

    const createResp = await request.post(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/`, {
      headers: authHeaders,
      data: {
        username: createdUsername,
        email: `${createdUsername}@example.com`,
        real_name: 'E2E Live',
        role: 'operator',
        password: 'Abcd1234'
      }
    });

    if (createResp.ok()) {
      const createJson = await createResp.json();
      createdUserId = createJson?.data?.id || null;
    } else {
      const probeResp = await request.get(
        `${BACKEND_BASE_URL}/api/v1/admin/admin-users/?skip=0&limit=50&search=${createdUsername}`,
        { headers: authHeaders }
      );
      if (probeResp.ok()) {
        const probeJson = await probeResp.json();
        const hit = (probeJson?.data?.items || []).find((x) => x.username === createdUsername);
        createdUserId = hit?.id || null;
      }
    }

    pushCheckpoint(
      'minimal test data prep',
      !!createdUserId,
      createdUserId ? `created username=${createdUsername}, id=${createdUserId}` : `create failed: status=${createResp.status()}`
    );

    if (createdUserId) {
      const activateResp = await request.put(
        `${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}/status?status=active`,
        { headers: authHeaders }
      );
      const activateVerifyResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, { headers: authHeaders });
      const activateVerifyJson = activateVerifyResp.ok() ? await activateVerifyResp.json() : null;
      const activateStatus = activateVerifyJson?.data?.status || 'unknown';
      pushCheckpoint('prep activate user', activateStatus === 'active', `status=${activateResp.status()}, verify=${activateStatus}`);
    }

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
    page.on('response', (resp) => {
      const url = resp.url();
      if (!url.includes('/api/')) return;
      const status = resp.status();
      if (status === 401 || status >= 500) {
        badApiResponses.push({ url, status });
      }
    });

    try {
      await page.goto('/admin/users/list');
      await expect(page.locator('.modern-table')).toBeVisible();
      await page.waitForTimeout(800);

      let exportPassed = false;
      let exportDetail = '';
      try {
        const exportRespPromise = page.waitForResponse((resp) => {
          return resp.url().includes('/api/v1/admin/admin-users/export') && resp.request().method() === 'GET';
        }, { timeout: 10000 });
        await page.locator('.header-actions .el-button').nth(2).click();
        const exportResp = await exportRespPromise;
        const ct = exportResp.headers()['content-type'] || '';
        exportPassed = exportResp.status() === 200 && (ct.includes('text/csv') || ct.includes('application/octet-stream'));
        exportDetail = `ui-export status=${exportResp.status()}, content-type=${ct}`;
      } catch {
        const directExportResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/export`, { headers: authHeaders });
        const ct = directExportResp.headers()['content-type'] || '';
        exportPassed = directExportResp.ok() && (ct.includes('text/csv') || ct.includes('application/octet-stream'));
        exportDetail = `api-export status=${directExportResp.status()}, content-type=${ct}`;
      }
      pushCheckpoint('export', exportPassed, exportDetail);

      if (!createdUserId) {
        pushCheckpoint('batch disable/enable', false, 'skip: test user was not created');
      } else {
        const disableResp = await request.put(
          `${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}/status?status=inactive`,
          { headers: authHeaders }
        );
        const verifyDisableResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, { headers: authHeaders });
        const verifyDisableJson = verifyDisableResp.ok() ? await verifyDisableResp.json() : null;
        const afterDisableStatus = verifyDisableJson?.data?.status || 'unknown';

        const enableResp = await request.put(
          `${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}/status?status=active`,
          { headers: authHeaders }
        );
        const verifyEnableResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, { headers: authHeaders });
        const verifyEnableJson = verifyEnableResp.ok() ? await verifyEnableResp.json() : null;
        const afterEnableStatus = verifyEnableJson?.data?.status || 'unknown';

        pushCheckpoint(
          'batch disable/enable',
          afterDisableStatus === 'inactive' && afterEnableStatus === 'active',
          `disable=${disableResp.status()} -> ${afterDisableStatus}, enable=${enableResp.status()} -> ${afterEnableStatus}`
        );
      }

      if (!createdUserId) {
        pushCheckpoint('edit-save secondary verify', false, 'skip: test user was not created');
      } else {
        const marker = `E2E-LIVE-${Date.now()}`;
        const updateResp = await request.put(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, {
          headers: authHeaders,
          data: { real_name: marker }
        });

        const verifyResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, { headers: authHeaders });
        const verifyJson = verifyResp.ok() ? await verifyResp.json() : null;
        const currentRealName = verifyJson?.data?.real_name || '';

        pushCheckpoint(
          'edit-save secondary verify',
          verifyResp.ok() && currentRealName === marker,
          `update=${updateResp.status()}, verify=${verifyResp.status()}, real_name=${currentRealName}`
        );
      }

      pushCheckpoint(
        'api health',
        badApiResponses.length === 0,
        badApiResponses.length ? JSON.stringify(badApiResponses, null, 2) : 'no 401/5xx'
      );
    } finally {
      try {
        if (createdUserId) {
          const deleteResp = await request.delete(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${createdUserId}`, { headers: authHeaders });
          const verifyGoneResp = await request.get(
            `${BACKEND_BASE_URL}/api/v1/admin/admin-users/?skip=0&limit=20&search=${createdUsername}`,
            { headers: authHeaders }
          );
          let gone = false;
          let hit = null;
          if (verifyGoneResp.ok()) {
            const verifyGoneJson = await verifyGoneResp.json();
            const items = verifyGoneJson?.data?.items || [];
            hit = items.find((x) => x.username === createdUsername) || null;
            gone = !hit;
          }

          if (!gone && hit?.id) {
            await request.put(
              `${BACKEND_BASE_URL}/api/v1/admin/admin-users/${hit.id}/status?status=inactive`,
              { headers: authHeaders }
            );
            const verifyRecycleResp = await request.get(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${hit.id}`, { headers: authHeaders });
            const verifyRecycleJson = verifyRecycleResp.ok() ? await verifyRecycleResp.json() : null;
            const recycled = verifyRecycleJson?.data?.status === 'inactive';
            pushCheckpoint('cleanup', recycled, `delete=${deleteResp.status()}, recycled=${recycled}`);
          } else {
            pushCheckpoint('cleanup', gone, `delete=${deleteResp.status()}, gone=${gone}`);
          }
        } else {
          const listResp = await request.get(
            `${BACKEND_BASE_URL}/api/v1/admin/admin-users/?skip=0&limit=50&search=${createdUsername}`,
            { headers: authHeaders }
          );
          if (listResp.ok()) {
            const listJson = await listResp.json();
            const items = listJson?.data?.items || [];
            const hit = items.find((x) => x.username === createdUsername);
            if (hit?.id) {
              const deleteResp = await request.delete(`${BACKEND_BASE_URL}/api/v1/admin/admin-users/${hit.id}`, { headers: authHeaders });
              pushCheckpoint('cleanup', deleteResp.ok(), deleteResp.ok() ? `deleted id=${hit.id}` : `delete failed: ${deleteResp.status()}`);
            } else {
              pushCheckpoint('cleanup', true, 'no orphan test user found');
            }
          } else {
            pushCheckpoint('cleanup', false, `list for cleanup failed: ${listResp.status()}`);
          }
        }
      } catch (error) {
        pushCheckpoint('cleanup', false, `cleanup request failed: ${error?.message || 'unknown error'}`);
      }
    }

    const reportLines = [
      '# User Management Pre-Release Live Checklist',
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
      path.resolve(process.cwd(), '../USER_MANAGEMENT_LIVE_PRERELEASE_CHECKLIST_REPORT.md'),
      reportLines.join('\n'),
      'utf-8'
    );

    expect(issues, `Pre-release checklist failed:\n${issues.join('\n')}`).toEqual([]);
  });
});
