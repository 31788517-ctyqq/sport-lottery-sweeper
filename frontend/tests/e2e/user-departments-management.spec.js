import { test, expect } from '@playwright/test';

async function setupDepartmentMocks(page) {
  const state = {
    departments: [
      {
        id: 1,
        name: '总部',
        parent_id: null,
        description: '总部',
        leader_id: null,
        sort_order: 0,
        status: true,
        user_count: 1,
        children: [
          {
            id: 2,
            name: '技术部',
            parent_id: 1,
            description: '研发团队',
            leader_id: null,
            sort_order: 1,
            status: true,
            user_count: 1,
            children: []
          }
        ]
      }
    ],
    users: [
      { id: 10, username: 'admin', realName: '系统管理员', departmentId: 1, department: '总部', status: 'active', roleNames: ['admin'] },
      { id: 11, username: 'dev1', realName: '开发1', departmentId: 2, department: '技术部', status: 'active', roleNames: ['operator'] }
    ],
    calls: { deptList: 0, userList: 0, createDept: 0, updateDept: 0, deleteDept: 0 }
  };

  await page.route('**/api/**', async (route) => {
    const req = route.request();
    const url = new URL(req.url());
    const path = url.pathname;
    const method = req.method();

    if (path.includes('/admin/departments') && method === 'GET') {
      state.calls.deptList += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: { data: state.departments, total: 2, skip: 0, limit: 100 } })
      });
    }

    if ((path.endsWith('/admin/admin-users') || path.endsWith('/admin/admin-users/')) && method === 'GET') {
      state.calls.userList += 1;
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, data: { items: state.users, total: state.users.length, page: 1, size: 500, pages: 1 } })
      });
    }

    if (path.includes('/admin/departments') && method === 'POST') {
      state.calls.createDept += 1;
      const payload = req.postDataJSON() || {};
      state.departments[0].children.push({
        id: 3,
        name: payload.name || '新部门',
        parent_id: payload.parent_id ?? 1,
        description: payload.description || '',
        leader_id: payload.leader_id ?? null,
        sort_order: payload.sort_order ?? 0,
        status: payload.status ?? true,
        user_count: 0,
        children: []
      });
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 200, data: true }) });
    }

    if (/\/admin\/departments\/\d+$/.test(path) && method === 'PUT') {
      state.calls.updateDept += 1;
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 200, data: true }) });
    }

    if (/\/admin\/departments\/\d+$/.test(path) && method === 'DELETE') {
      state.calls.deleteDept += 1;
      return route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 200, data: true }) });
    }

    return route.continue();
  });

  return state;
}

test.describe('User Departments Page', () => {
  test('should load department tree and user data', async ({ page }) => {
    const state = await setupDepartmentMocks(page);

    await page.goto('/admin/users/departments');
    await page.waitForLoadState('networkidle');

    await expect(page.locator('.dept-tree-card')).toBeVisible();
    await expect(page.locator('.dept-detail-card')).toBeVisible();
    await expect(page.getByText('总部')).toBeVisible();

    expect(state.calls.deptList).toBeGreaterThan(0);
    expect(state.calls.userList).toBeGreaterThan(0);
  });

  test('should handle create dialog and detail interaction logic', async ({ page }) => {
    const state = await setupDepartmentMocks(page);

    await page.goto('/admin/users/departments');
    await page.waitForLoadState('networkidle');

    await page.getByRole('button', { name: '新增部门' }).click();
    await expect(page.locator('.el-dialog')).toBeVisible();

    await page.locator('.el-dialog .dialog-footer .el-button').first().click();

    await page.locator('.dept-tree-container .el-tree-node__content').first().click();
    await expect(page.locator('.dept-detail-content')).toBeVisible();

    const before = state.calls.deptList;
    await page.getByRole('button', { name: '刷新' }).first().click();
    await page.waitForLoadState('networkidle');
    expect(state.calls.deptList).toBeGreaterThan(before);
  });
});
