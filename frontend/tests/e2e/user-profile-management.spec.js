import { test, expect } from '@playwright/test';

async function setupUserProfileMocks(page) {
  const state = {
    calls: {
      currentUserGet: 0,
      currentUserPut: 0,
      loginHistory: 0,
      stats: 0,
      changePassword: 0
    },
    currentUser: {
      id: 1,
      username: 'admin',
      realName: '系统管理员',
      email: 'admin@example.com',
      phone: '13800000000',
      departmentName: '技术部',
      position: '管理员',
      roleNames: ['admin'],
      status: 'active',
      createdAt: '2026-02-01T08:00:00.000Z',
      lastLoginTime: '2026-02-18T10:00:00.000Z',
      gender: 1,
      birthday: '1990-01-01',
      avatar: '',
      bio: '管理员账号'
    }
  };

  await page.route('**/api/**', async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const path = url.pathname;
    const method = req.method();

    if (path.endsWith('/admin/admin-users/current-user') && method === 'GET') {
      state.calls.currentUserGet += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'ok', data: state.currentUser })
      });
    }

    if (path.endsWith('/admin/admin-users/current-user') && method === 'PUT') {
      state.calls.currentUserPut += 1;
      const payload = req.postDataJSON() || {};
      state.currentUser = { ...state.currentUser, ...payload };
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'updated', data: state.currentUser })
      });
    }

    if (path.endsWith('/admin/admin-users/login-history') && method === 'GET') {
      state.calls.loginHistory += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: 'ok',
          data: [
            {
              id: 1,
              loginTime: '2026-02-18T10:00:00.000Z',
              ip: '127.0.0.1',
              location: '北京',
              device: 'Desktop',
              browser: 'Chrome',
              success: true
            }
          ]
        })
      });
    }

    if (path.endsWith('/admin/admin-users/stats/overview') && method === 'GET') {
      state.calls.stats += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: 'ok',
          data: { totalLogins: 12, thisMonthLogins: 4, totalOperations: 31 }
        })
      });
    }

    if (path.endsWith('/admin/admin-users/change-password') && method === 'PUT') {
      state.calls.changePassword += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'ok', data: { message: 'changed' } })
      });
    }

    return route.continue();
  });

  return state;
}

test.describe('User Profile Page', () => {
  test('should load profile, render stats/history, and submit profile/password actions', async ({ page }) => {
    const state = await setupUserProfileMocks(page);

    await page.goto('/admin/users/profile');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('.profile-card')).toBeVisible();
    await expect(page.locator('.security-card')).toBeVisible();
    await expect(page.locator('.quick-actions-card')).toBeVisible();
    await expect(page.locator('.login-history-card')).toBeVisible();
    await expect(page.locator('.stats-card')).toBeVisible();
    await expect(page.locator('.profile-card')).toContainText('admin');
    await expect(page.locator('.stats-card')).toContainText('12');

    expect(state.calls.currentUserGet).toBeGreaterThan(0);
    expect(state.calls.loginHistory).toBeGreaterThan(0);
    expect(state.calls.stats).toBeGreaterThan(0);

    await page.locator('input[name="old_password"]').fill('OldPass123');
    await page.locator('input[name="new_password"]').fill('NewPass123');
    await page.locator('input[name="confirm_password"]').fill('NewPass123');
    await page.locator('.security-card .el-button--primary').first().click();
    await page.waitForTimeout(300);
    expect(state.calls.changePassword).toBe(1);

    await page.locator('.profile-card .card-header .el-button').click();
    await expect(page.locator('.el-dialog')).toBeVisible();
    await page.locator('.el-dialog input[name="real_name"]').fill('测试管理员');
    await page.locator('.el-dialog input[name="email"]').fill('profile@example.com');
    await page.locator('.el-dialog .el-button--primary').last().click();
    await page.waitForTimeout(300);
    expect(state.calls.currentUserPut).toBe(1);
  });
});

