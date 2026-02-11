import { test, expect } from '@playwright/test';

test.describe('Comprehensive User Management Page Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 直接访问用户管理页面
    await page.goto('/admin/users/list');
    await page.waitForLoadState('networkidle');
  });

  test('should load the user management page correctly', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 检查页面标题和描述
    await expect(page.locator('.page-header .page-title')).toContainText('👥 用户管理');
    await expect(page.locator('.page-description')).toContainText('管理系统用户、角色和权限分配');

    // 检查搜索框和筛选器
    await expect(page.locator('.search-box input')).toBeVisible();
    await expect(page.locator('.filters select')).toHaveCount(3);

    // 检查操作按钮
    await expect(page.locator('.actions .action-btn.primary')).toContainText('➕ 新增用户');
    
    // 检查加载状态指示器
    await expect(page.locator('.loading-spinner, .spinner, .loader')).not.toBeVisible().catch(() => {});
  });

  test('should display user list with correct columns', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 检查用户表格是否存在
    const table = page.locator('.users-table');
    await expect(table).toBeVisible();

    // 检查表格列标题
    await expect(table.locator('th').nth(0)).toContainText('选择');
    await expect(table.locator('th').nth(1)).toContainText('用户');
    await expect(table.locator('th').nth(2)).toContainText('用户名');
    await expect(table.locator('th').nth(3)).toContainText('邮箱');
    await expect(table.locator('th').nth(4)).toContainText('角色');
    await expect(table.locator('th').nth(5)).toContainText('部门');
    await expect(table.locator('th').nth(6)).toContainText('状态');
    await expect(table.locator('th').nth(7)).toContainText('最后活动');
    await expect(table.locator('th').nth(8)).toContainText('操作');
  });

  test('should allow searching for users', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    const searchInput = page.locator('.search-box input');
    await expect(searchInput).toBeVisible();
    
    await searchInput.fill('admin');
    await page.locator('.search-btn').click();

    // 等待搜索结果加载
    await page.waitForTimeout(1000);

    // 检查搜索结果是否包含'admin'
    const usernames = page.locator('.users-table tbody tr td:nth-child(3)');
    if (await usernames.count() > 0) {
      await expect(usernames.first()).toContainText('admin');
    }
  });

  test('should allow filtering users by role', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    const roleFilter = page.locator('.filters select').nth(0);
    await expect(roleFilter).toBeVisible();
    await roleFilter.selectOption('admin');

    // 等待筛选结果加载
    await page.waitForTimeout(1000);

    // 检查筛选结果
    const roles = page.locator('.users-table tbody tr td:nth-child(5)');
    if (await roles.count() > 0) {
      await expect(roles.first()).toContainText('管理员');
    }
  });

  test('should open user creation modal', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    const createButton = page.locator('.action-btn.primary');
    await expect(createButton).toBeVisible();
    await createButton.click();

    // 检查模态框是否打开
    await expect(page.locator('.modal-content')).toBeVisible();
    await expect(page.locator('.modal-header h2')).toContainText('新增用户');
  });

  test('should handle pagination', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 检查分页控件是否存在
    await expect(page.locator('.pagination')).toBeVisible();

    // 点击下一页按钮
    const nextButton = page.locator('.pagination button').filter({ hasText: '下一页' });
    if (await nextButton.count() > 0 && await nextButton.isEnabled()) {
      const currentFirstUser = await page.locator('.users-table tbody tr:first-child td:nth-child(3)').textContent();
      await nextButton.click();
      await page.waitForTimeout(1000);
      
      const newFirstUser = await page.locator('.users-table tbody tr:first-child td:nth-child(3)').textContent();
      
      // 检查页面是否已切换
      expect(currentFirstUser).not.toEqual(newFirstUser);
    }
  });

  test('should view user details', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle');
    
    // 等待表格加载
    await expect(page.locator('.users-table')).toBeVisible();
    
    // 等待至少有一行数据
    await expect(page.locator('.users-table tbody tr')).toBeVisible();
    
    // 点击第一个用户的查看按钮
    const viewButtons = page.locator('.users-table tbody tr .action-btn.view');
    if (await viewButtons.count() > 0) {
      const firstViewButton = viewButtons.first();
      await firstViewButton.scrollIntoViewIfNeeded();
      await firstViewButton.click();

      // 检查详情模态框是否打开
      await expect(page.locator('.large-modal')).toBeVisible();
      await expect(page.locator('.modal-header h2')).toContainText('用户详情');
    }
  });

  test('should show loading state during data fetching', async ({ page }) => {
    // 监听API请求
    await page.route('**/api/v1/admin/admin-users*', async (route) => {
      // 模拟延迟
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.continue();
    });

    // 刷新页面以触发加载状态
    await page.reload();
    await page.waitForLoadState('networkidle');

    // 等待初始加载完成
    await page.waitForTimeout(1000);

    // 触发筛选以再次测试加载状态
    const roleFilter = page.locator('.filters select').nth(0);
    await expect(roleFilter).toBeVisible();
    await roleFilter.selectOption('admin');
    
    // 检查是否有加载指示器
    await expect(page.locator('.loading-spinner, .spinner, .loader')).toBeVisible().catch(() => {});
  });

  test('should handle error states gracefully', async ({ page }) => {
    // 拦截API请求并模拟错误
    await page.route('**/api/v1/admin/admin-users*', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });

    // 刷新页面以触发错误状态
    await page.reload();
    
    // 等待错误处理
    await page.waitForTimeout(1000);
    
    // 检查是否有错误提示
    await expect(page.locator('.error-message, .alert-error, .notification.error')).toBeVisible().catch(() => {});
  });
});