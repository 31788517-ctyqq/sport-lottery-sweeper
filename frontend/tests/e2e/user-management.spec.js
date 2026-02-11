import { test, expect } from '@playwright/test';

test.describe('User Management Page', () => {
  test.beforeEach(async ({ page }) => {
    // 使用API进行身份验证
    const response = await page.request.post('/api/auth/login', {
      data: {
        username: 'admin',
        password: 'admin123'
      }
    });
    
    // 验证登录成功
    expect(response.ok()).toBeTruthy();
    
    // 直接导航到用户管理页面
    await page.goto('/admin/users/list');
    
    // 等待页面加载完成
    await page.waitForLoadState('networkidle');
  });

  test('should load and display user management page correctly', async ({ page }) => {
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

  test('should create a new user', async ({ page }) => {
    const createButton = page.locator('.action-btn.primary');
    await createButton.click();

    // 等待模态框打开
    await expect(page.locator('.modal-content')).toBeVisible();

    // 填写用户信息
    await page.locator('input[name="username"]').fill('testuser');
    await page.locator('input[name="firstName"]').fill('Test');
    await page.locator('input[name="lastName"]').fill('User');
    await page.locator('input[name="email"]').fill('testuser@example.com');
    await page.locator('input[name="phone"]').fill('+86 13800138000');
    
    // 选择角色和状态
    await page.locator('select[name="role"]').selectOption('user');
    await page.locator('select[name="status"]').selectOption('active');

    // 提交表单
    await page.locator('.modal-footer .btn.primary').click();

    // 等待创建完成
    await page.waitForTimeout(2000);

    // 检查新用户是否出现在列表中
    await expect(page.locator('.users-table tbody tr:first-child td:nth-child(3)')).toContainText('testuser');
  });

  test('should edit an existing user', async ({ page }) => {
    // 点击第一个用户的编辑按钮
    const editButton = page.locator('.users-table tbody tr:first-child .action-btn.edit').first();
    await editButton.scrollIntoViewIfNeeded();
    await editButton.click();

    // 等待编辑模态框打开
    await expect(page.locator('.modal-content')).toBeVisible();
    await expect(page.locator('.modal-header h2')).toContainText('编辑用户');

    // 修改邮箱
    const emailInput = page.locator('input[name="email"]');
    await emailInput.clear();
    await emailInput.fill('updated@example.com');

    // 提交更改
    await page.locator('.modal-footer .btn.primary').click();

    // 等待更新完成
    await page.waitForTimeout(2000);

    // 关闭模态框后检查更改是否生效
    await expect(page.locator('.users-table tbody tr:first-child td:nth-child(4)')).toContainText('updated@example.com');
  });

  test('should delete a user', async ({ page }) => {
    // 获取第一个用户的用户名
    const firstUserCell = page.locator('.users-table tbody tr:first-child td:nth-child(3)');
    const originalUsername = await firstUserCell.textContent();

    // 点击删除按钮
    const deleteButton = page.locator('.users-table tbody tr:first-child .action-btn.delete').first();
    await deleteButton.scrollIntoViewIfNeeded();
    await deleteButton.click();

    // 确认删除
    page.on('dialog', dialog => dialog.accept());
    await page.waitForTimeout(1000);

    // 检查用户是否已从列表中移除
    await expect(page.locator(`.users-table tbody tr td:text("${originalUsername}")`)).not.toBeVisible();
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
});