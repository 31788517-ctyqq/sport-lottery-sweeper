import { test, expect } from '@playwright/test';

async function setupRolePageMocks(page) {
  const state = {
    roles: [
      { id: 1, name: '超级管理员', description: '系统内置角色', permissions: [1, 2], isSystem: true },
      { id: 2, name: '运营', description: '运营角色', permissions: [1], isSystem: false }
    ],
    permissions: [
      { id: 1, name: '用户管理', description: '管理用户', parentId: null, children: [] },
      { id: 2, name: '角色权限', description: '管理角色权限', parentId: null, children: [] }
    ],
    calls: { roleList: 0, permissionList: 0, createRole: 0, updateRole: 0, assignPermissions: 0 }
  };

  await page.route('**/api/**', async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const path = url.pathname;
    const method = req.method();

    if ((path.endsWith('/admin/roles') || path.endsWith('/admin/roles/')) && method === 'GET') {
      state.calls.roleList += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: state.roles })
      });
    }

    if ((path.endsWith('/admin/permissions') || path.endsWith('/admin/permissions/')) && method === 'GET') {
      state.calls.permissionList += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: state.permissions })
      });
    }

    if ((path.endsWith('/admin/roles') || path.endsWith('/admin/roles/')) && method === 'POST') {
      state.calls.createRole += 1;
      const payload = req.postDataJSON() || {};
      const created = {
        id: state.roles.length + 1,
        name: payload.name || '新角色',
        description: payload.description || '',
        permissions: payload.permissions || [],
        isSystem: false
      };
      state.roles.push(created);
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: created })
      });
    }

    if (/\/admin\/roles\/\d+$/.test(path) && method === 'PUT') {
      state.calls.updateRole += 1;
      const id = Number(path.match(/(\d+)$/)?.[1]);
      const payload = req.postDataJSON() || {};
      const role = state.roles.find((x) => x.id === id);
      if (role) {
        role.name = payload.name ?? role.name;
        role.description = payload.description ?? role.description;
        role.permissions = payload.permissions ?? role.permissions;
      }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: role || null })
      });
    }

    if (/\/admin\/roles\/\d+\/permissions$/.test(path) && method === 'POST') {
      state.calls.assignPermissions += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: true })
      });
    }

    if (/\/admin\/roles\/\d+$/.test(path) && method === 'DELETE') {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: true })
      });
    }

    if (path.startsWith('/api/')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
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

test.describe('User Roles & Permissions Page', () => {
  test('should load roles and permission tree from data layer', async ({ page }) => {
    const state = await setupRolePageMocks(page);
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('token', 'mock-token');
    });

    await page.goto('/admin/users/roles');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('.roles-card')).toBeVisible();
    await expect(page.locator('.permissions-card')).toBeVisible();
    await expect(page.locator('.role-item')).toHaveCount(2);
    await expect(page.locator('.permissions-card .el-tree')).toBeVisible();

    expect(state.calls.roleList).toBeGreaterThan(0);
    expect(state.calls.permissionList).toBeGreaterThan(0);
  });

  test('should create role and save permissions', async ({ page }) => {
    const state = await setupRolePageMocks(page);
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token');
      localStorage.setItem('token', 'mock-token');
    });

    await page.goto('/admin/users/roles');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: '新建角色' }).click();
    await expect(page.locator('.el-dialog')).toBeVisible();

    await page.locator('.el-dialog input').first().fill('测试角色');
    await page.locator('.el-dialog textarea').first().fill('用于E2E测试');
    await page.locator('.el-dialog .el-button--primary').last().click();
    await page.waitForLoadState('networkidle');

    expect(state.calls.createRole).toBe(1);

    await page.locator('.role-item').nth(1).click();
    await page.locator('.permissions-card .el-button--primary').click();
    await page.waitForLoadState('networkidle');

    expect(state.calls.assignPermissions).toBeGreaterThan(0);
  });
});
