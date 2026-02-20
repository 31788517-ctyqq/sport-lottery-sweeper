import { test, expect } from '@playwright/test';

function buildMockUsers(total = 8) {
  return Array.from({ length: total }, (_, idx) => {
    const id = idx + 1;
    return {
      id,
      username: id === 1 ? 'admin' : `operator_${id}`,
      realName: id === 1 ? '系统管理员' : `运营用户${id}`,
      email: id === 1 ? 'admin@example.com' : `operator_${id}@example.com`,
      phone: `1390000${String(id).padStart(4, '0')}`,
      departmentName: id % 2 ? '运营部' : '技术部',
      roleNames: id % 2 ? ['operator'] : ['admin'],
      status: id % 2 ? 'active' : 'inactive',
      lastLoginTime: '2026-02-18T09:30:00.000Z'
    };
  });
}

async function setupMocks(page) {
  const state = {
    users: buildMockUsers(),
    calls: { list: 0, departments: 0, roles: 0, statusPatch: 0 }
  };

  await page.route('**/api/**', async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const path = url.pathname;
    const method = req.method();

    if ((path.endsWith('/admin/admin-users') || path.endsWith('/admin/admin-users/')) && method === 'GET') {
      state.calls.list += 1;
      const limit = Number(url.searchParams.get('limit') || url.searchParams.get('size') || '20');
      const skip = Number(url.searchParams.get('skip') || '0');
      const status = (url.searchParams.get('status') || '').trim();
      const search = (url.searchParams.get('search') || '').trim().toLowerCase();
      let items = [...state.users];
      if (status) {
        items = items.filter((u) => u.status === status);
      }
      if (search) {
        items = items.filter((u) =>
          [u.username, u.realName, u.email].some((x) => String(x).toLowerCase().includes(search))
        );
      }
      const pageItems = items.slice(skip, skip + limit);
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            items: pageItems,
            total: items.length,
            page: 1,
            size: limit,
            pages: Math.max(1, Math.ceil(items.length / limit))
          }
        })
      });
    }

    if (/\/admin\/admin-users\/\d+\/status$/.test(path) && method === 'PATCH') {
      state.calls.statusPatch += 1;
      const id = Number(path.match(/(\d+)\/status$/)?.[1]);
      const payload = req.postDataJSON() || {};
      const user = state.users.find((u) => u.id === id);
      if (user && payload.status) user.status = payload.status;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: user || null })
      });
    }

    if (path.includes('/admin/departments') && method === 'GET') {
      state.calls.departments += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: [{ id: 1, name: '技术部' }, { id: 2, name: '运营部' }] })
      });
    }

    if (path.includes('/admin/roles') && method === 'GET') {
      state.calls.roles += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: [{ id: 1, name: 'admin' }, { id: 2, name: 'operator' }] })
      });
    }

    if (/\/admin\/admin-users\/\d+$/.test(path) && method === 'GET') {
      const id = Number(path.match(/(\d+)$/)?.[1]);
      const user = state.users.find((u) => u.id === id);
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 200, data: user || null }) });
    }

    return route.continue();
  });

  return state;
}

test.describe('User Management Comprehensive', () => {
  test('should pass data, render and logic workflows', async ({ page }) => {
    const state = await setupMocks(page);

    await page.goto('/admin/users/list');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('.modern-table')).toBeVisible();
    await expect(page.locator('.modern-table .el-table__body tbody tr')).toHaveCount(8);

    expect(state.calls.list).toBeGreaterThan(0);
    expect(state.calls.departments).toBeGreaterThan(0);
    expect(state.calls.roles).toBeGreaterThan(0);

    await page.locator('.modern-table .el-table__body .el-button--danger:not(.is-disabled)').first().click();
    await page.locator('.el-message-box__btns .el-button--primary').click();
    await page.waitForLoadState('networkidle');
    expect(state.calls.statusPatch).toBe(1);

    await page.locator('.search-input input').fill('admin');
    await page.locator('.users-controls .action-btn').first().click();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.modern-table .el-table__body tbody tr')).toHaveCount(1);

    await page.locator('.users-controls .action-btn').nth(1).click();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.search-input input')).toHaveValue('');

    await page.locator('.modern-table .el-table__body tbody tr:first-child .el-checkbox').click();
    await expect(page.locator('.action-bar .el-button')).toHaveCount(3);
  });
});
