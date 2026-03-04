import { test, expect } from '@playwright/test';

function buildMockUsers(total = 25) {
  return Array.from({ length: total }, (_, idx) => {
    const id = idx + 1;
    return {
      id,
      username: id === 1 ? 'admin' : `user_${id}`,
      realName: id === 1 ? '系统管理员' : `测试用户${id}`,
      email: id === 1 ? 'admin@example.com' : `user_${id}@example.com`,
      phone: `1380000${String(id).padStart(4, '0')}`,
      departmentName: id % 2 === 0 ? '技术部' : '运营部',
      roleNames: id % 2 === 0 ? ['admin'] : ['operator'],
      status: id % 3 === 0 ? 'inactive' : 'active',
      lastLoginTime: '2026-02-18T10:00:00.000Z'
    };
  });
}

async function setupUserListMocks(page) {
  const corsHeaders = {
    'access-control-allow-origin': '*',
    'access-control-allow-methods': 'GET,POST,PUT,PATCH,DELETE,OPTIONS',
    'access-control-allow-headers': '*'
  };

  const state = {
    users: buildMockUsers(),
    calls: {
      list: 0,
      departments: 0,
      roles: 0,
      statusPatch: 0,
      detail: 0,
      import: 0,
      importMethods: []
    }
  };
  state.lastListParams = [];

  await page.route('**/api/**', async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const path = url.pathname;
    const method = req.method();

    if (method === 'OPTIONS' && path.startsWith('/api/')) {
      return route.fulfill({ status: 204, headers: corsHeaders });
    }

    if (path.endsWith('/admin/admin-users') || path.endsWith('/admin/admin-users/')) {
      if (method === 'GET') {
        state.calls.list += 1;
        state.lastListParams.push({
          skip: Number(url.searchParams.get('skip') || '0'),
          limit: Number(url.searchParams.get('limit') || '20')
        });

        const size = Number(url.searchParams.get('size') || url.searchParams.get('limit') || '20');
        const skip = Number(url.searchParams.get('skip') || '0');
        const pageNo = Number(url.searchParams.get('page') || String(Math.floor(skip / size) + 1));
        const search = (url.searchParams.get('search') || '').trim().toLowerCase();
        const status = (url.searchParams.get('status') || '').trim();

        let filtered = [...state.users];
        if (search) {
          filtered = filtered.filter((u) =>
            [u.username, u.realName, u.email].some((x) => String(x).toLowerCase().includes(search))
          );
        }
        if (status) {
          filtered = filtered.filter((u) => u.status === status);
        }

        const start = (pageNo - 1) * size;
        const items = filtered.slice(start, start + size);

        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            message: 'success',
            data: {
              items,
              total: filtered.length,
              page: pageNo,
              size,
              pages: Math.max(1, Math.ceil(filtered.length / size))
            }
          })
        });
      }

      if (method === 'POST') {
        const payload = req.postDataJSON() || {};
        const newUser = {
          id: state.users.length + 1,
          username: payload.username || `user_${state.users.length + 1}`,
          realName: payload.realName || '新用户',
          email: payload.email || `new_${state.users.length + 1}@example.com`,
          phone: payload.phone || '13800000000',
          departmentName: '技术部',
          roleNames: ['operator'],
          status: payload.status || 'active',
          lastLoginTime: null
        };
        state.users.unshift(newUser);
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ code: 200, message: 'created', data: newUser })
        });
      }
    }

    if (/\/admin\/admin-users\/\d+\/status$/.test(path) && method === 'PATCH') {
      state.calls.statusPatch += 1;
      const payload = req.postDataJSON() || {};
      const id = Number(path.match(/(\d+)\/status$/)?.[1]);
      const target = state.users.find((u) => u.id === id);
      if (target && payload.status) {
        target.status = payload.status;
      }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'updated', data: target || null })
      });
    }

    if (/\/admin\/admin-users\/\d+$/.test(path) && method === 'GET') {
      state.calls.detail += 1;
      const id = Number(path.match(/(\d+)$/)?.[1]);
      const target = state.users.find((u) => u.id === id);
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'ok', data: target || null })
      });
    }

    if (path.includes('/admin/departments') && method === 'GET') {
      state.calls.departments += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: corsHeaders,
        body: JSON.stringify({
          code: 200,
          message: 'ok',
          data: [
            { id: 1, name: '技术部' },
            { id: 2, name: '运营部' }
          ]
        })
      });
    }

    if (path.includes('/admin/roles') && method === 'GET') {
      state.calls.roles += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: 'ok',
          data: [
            { id: 1, name: 'admin' },
            { id: 2, name: 'operator' }
          ]
        })
      });
    }

    if (path.endsWith('/admin/admin-users/import') || path.endsWith('/admin/admin-users/import/')) {
      state.calls.import += 1;
      state.calls.importMethods.push(method);
      if (method !== 'POST') {
        return route.fulfill({
          status: 204,
          headers: corsHeaders
        });
      }
      const importedUser = {
        id: state.users.length + 1,
        username: 'import_user',
        realName: '导入用户',
        email: 'import_user@example.com',
        phone: '13900001234',
        departmentName: '技术部',
        roleNames: ['operator'],
        status: 'active',
        lastLoginTime: null
      };
      state.users.unshift(importedUser);
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: corsHeaders,
        body: JSON.stringify({
          code: 200,
          message: 'ok',
          data: {
            total_rows: 1,
            imported_count: 1,
            skipped_count: 0,
            default_password_count: 0,
            errors: []
          }
        })
      });
    }

    if (path.startsWith('/api/')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        headers: corsHeaders,
        body: JSON.stringify({
          code: 200,
          success: true,
          message: 'mock default',
          data: {}
        })
      });
    }

    return route.continue();
  });

  return state;
}

test.describe('User Management Page', () => {
  let mockState;

  test.beforeEach(async ({ page }) => {
    mockState = await setupUserListMocks(page);
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('admin_token', 'mock-token');
    });
    await page.goto('/admin/users/list');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.modern-table')).toBeVisible();
  });

  test('should load and display page structure', async ({ page }) => {
    await expect(page.locator('.card-header')).toBeVisible();
    await expect(page.locator('.search-input')).toBeVisible();
    await expect(page.locator('.status-selector')).toBeVisible();
    await expect(page.locator('.dept-selector')).toBeVisible();
    await expect(page.locator('.role-selector')).toBeVisible();
    await expect(page.locator('.header-actions .el-button')).toHaveCount(3);
  });

  test('should render user rows from data layer', async ({ page }) => {
    const rows = page.locator('.modern-table .el-table__body tbody tr');
    await expect(rows).toHaveCount(20);
    await expect(rows.first()).toContainText('admin');
  });

  test('should search users and narrow results', async ({ page }) => {
    await page.locator('.search-input input').fill('admin');
    await page.locator('.users-controls .action-btn').first().click();
    await page.waitForLoadState('networkidle');

    const rows = page.locator('.modern-table .el-table__body tbody tr');
    await expect(rows).toHaveCount(1);
    await expect(rows.first()).toContainText('admin');
  });

  test('should open user detail dialog from action button', async ({ page }) => {
    await page.locator('.modern-table .el-table__body tbody tr:first-child .el-button').first().click();
    await expect(page.locator('.el-dialog')).toBeVisible();
  });

  test('should paginate to next page', async ({ page }) => {
    await page.locator('.pagination-wrapper .btn-next').click();
    await page.waitForLoadState('networkidle');
    const lastListCall = mockState.lastListParams[mockState.lastListParams.length - 1];
    expect(lastListCall.skip).toBeGreaterThanOrEqual(20);
  });

  test('should import users from csv file', async ({ page }) => {
    const importRequests = [];
    page.on('request', (req) => {
      if (req.url().includes('/admin/admin-users/import')) {
        importRequests.push(req.method());
      }
    });

    const [fileChooser] = await Promise.all([
      page.waitForEvent('filechooser'),
      page.getByRole('button', { name: '批量导入' }).click()
    ]);

    await fileChooser.setFiles({
      name: 'users.csv',
      mimeType: 'text/csv',
      buffer: Buffer.from('username,email,real_name,password,role\nimport_user,import_user@example.com,导入用户,TempPass123,operator\n')
    });
    await page.waitForLoadState('networkidle');

    await expect.poll(() => mockState.calls.import, { timeout: 5000 }).toBeGreaterThan(0);
    expect(mockState.calls.importMethods).toContain('POST');
    expect(importRequests).toContain('POST');
    await expect(page.locator('.modern-table .el-table__body')).toContainText('import_user');
  });

  test('should debounce search and persist list state', async ({ page }) => {
    const beforeCalls = mockState.calls.list;

    await page.locator('.search-input input').fill('user_2');
    await expect.poll(() => mockState.calls.list, { timeout: 5000 }).toBeGreaterThan(beforeCalls);
    await expect(page.locator('.modern-table .el-table__body')).toContainText('user_2');

    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('admin_user_list_view_state_v1') || '{}'));
    expect(state.searchKeyword).toBe('user_2');

    await page.reload();
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.search-input input')).toHaveValue('user_2');
  });

  test('should support density switch and column visibility config', async ({ page }) => {
    await page.locator('.density-switch .el-radio-button__inner', { hasText: '紧凑' }).click();
    await expect.poll(async () => {
      const state = await page.evaluate(() => JSON.parse(localStorage.getItem('admin_user_list_view_state_v1') || '{}'));
      return state.tableDensity;
    }).toBe('small');

    await page.locator('.column-config-trigger').click();
    await page.locator('.column-config-popover .el-checkbox', { hasText: '邮箱' }).click();

    await expect(page.locator('.modern-table .el-table__header-wrapper')).not.toContainText('邮箱');

    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('admin_user_list_view_state_v1') || '{}'));
    expect(state.visibleColumnKeys).not.toContain('email');
  });
});
