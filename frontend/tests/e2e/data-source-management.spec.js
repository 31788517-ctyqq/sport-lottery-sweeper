import { test, expect } from '@playwright/test';

// 模拟数据源列表响应
const mockDataSources = {
  code: 200,
  message: 'success',
  data: {
    items: [
      {
        id: 1,
        name: '500彩票网API',
        type: 'api',
        url: 'https://api.500.com/v1/lottery',
        status: true,
        last_update: '2024-01-15T10:30:00Z',
        error_rate: 2.5,
        config: '{"headers":{"Authorization":"Bearer token"}}'
      },
      {
        id: 2,
        name: '本地比赛数据',
        type: 'file',
        url: '/uploads/matches.csv',
        status: true,
        last_update: '2024-01-14T15:45:00Z',
        error_rate: 0.0,
        config: '{"delimiter":","}'
      },
      {
        id: 3,
        name: '测试数据源',
        type: 'api',
        url: 'https://test.api.com/data',
        status: false,
        last_update: '2024-01-10T09:20:00Z',
        error_rate: 15.0,
        config: '{}'
      }
    ],
    total: 3,
    page: 1,
    size: 20
  }
};

test.describe('足球SP管理 - 数据源管理页面', () => {
  test.beforeEach(async ({ page }) => {
    // 拦截API请求并返回模拟数据
    await page.route('**/admin/sp/data-sources**', (route) => {
      const url = route.request().url();
      console.log('拦截到数据源请求:', url);
      
      // 根据请求方法返回不同的响应
      if (route.request().method() === 'GET') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(mockDataSources),
        });
      } else if (route.request().method() === 'POST') {
        // 模拟创建数据源成功
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            message: '创建成功',
            data: { id: 4, ...JSON.parse(route.request().postData()) }
          }),
        });
      } else {
        route.continue();
      }
    });

    // 拦截登录请求（使用Mock认证）
    await page.route('**/api/v1/auth/login**', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: '登录成功',
          data: {
            access_token: 'mock-jwt-token-1234567890',
            refresh_token: 'mock-refresh-token',
            user_info: {
              userId: 1,
              username: 'admin',
              email: 'admin@sportlottery.com',
              roles: ['admin'],
              status: 'active'
            }
          }
        }),
      });
    });

    // 访问登录页面
    await page.goto('/');
    
    // 等待登录页面加载
    await expect(page).toHaveURL(/.*\/#\/login/);
    
    // 填写登录表单
    await page.fill('input[placeholder*="用户名"]', 'admin');
    await page.fill('input[placeholder*="密码"]', 'admin123');
    
    // 点击登录按钮
    await page.click('button[type="submit"]');
    
    // 等待登录成功并跳转到首页
    await page.waitForURL('**/#/');
    
    // 导航到数据源管理页面
    await page.goto('/#/admin/sp/data-source');
    
    // 等待页面加载完成
    await page.waitForSelector('.data-source-management');
  });

  test('应正确加载数据源管理页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.locator('h1, .page-title')).toContainText(/数据源管理/);
    
    // 验证搜索表单存在
    await expect(page.locator('.search-form')).toBeVisible();
    
    // 验证操作按钮存在
    await expect(page.locator('button:has-text("新增数据源")')).toBeVisible();
    await expect(page.locator('button:has-text("批量测试连接")')).toBeVisible();
    await expect(page.locator('button:has-text("批量导入")')).toBeVisible();
    
    // 验证数据表格存在
    await expect(page.locator('.el-table')).toBeVisible();
    
    // 验证表格中有数据行
    const tableRows = page.locator('.el-table__row');
    await expect(tableRows).toHaveCount(mockDataSources.data.items.length);
    
    // 验证分页组件存在
    await expect(page.locator('.el-pagination')).toBeVisible();
  });

  test('应能搜索数据源', async ({ page }) => {
    // 在搜索框中输入搜索词
    await page.fill('input[placeholder*="数据源名称"]', '500彩票');
    
    // 点击搜索按钮
    await page.click('button:has-text("搜索")');
    
    // 验证表格中只显示匹配的结果
    // 注意：这里需要等待API请求完成，由于我们拦截了请求，可以直接验证
    const firstRow = page.locator('.el-table__row').first();
    await expect(firstRow).toContainText('500彩票网API');
  });

  test('应能新增数据源', async ({ page }) => {
    // 点击新增数据源按钮
    await page.click('button:has-text("新增数据源")');
    
    // 等待对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible();
    await expect(page.locator('.el-dialog__title')).toContainText('新增数据源');
    
    // 填写表单
    await page.fill('input[placeholder*="数据源名称"]', '新的测试数据源');
    
    // 选择API类型（默认已经是API）
    await page.click('label:has-text("API接口")');
    
    // 填写API地址
    await page.fill('input[placeholder*="API接口地址"]', 'https://new.api.com/data');
    
    // 填写配置信息
    await page.fill('textarea[placeholder*="JSON格式的配置信息"]', '{"headers":{"Content-Type":"application/json"}}');
    
    // 点击确定按钮
    await page.click('button:has-text("确定")');
    
    // 等待成功提示
    await expect(page.locator('.el-message--success')).toBeVisible();
    
    // 验证对话框已关闭
    await expect(page.locator('.el-dialog')).not.toBeVisible();
  });

  test('应能编辑数据源', async ({ page }) => {
    // 点击第一行的编辑按钮
    const firstRow = page.locator('.el-table__row').first();
    await firstRow.locator('button:has-text("编辑")').click();
    
    // 等待对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible();
    await expect(page.locator('.el-dialog__title')).toContainText('编辑数据源');
    
    // 修改数据源名称
    const nameInput = page.locator('input[placeholder*="数据源名称"]');
    await nameInput.clear();
    await nameInput.fill('修改后的数据源名称');
    
    // 点击确定按钮
    await page.click('button:has-text("确定")');
    
    // 等待成功提示
    await expect(page.locator('.el-message--success')).toBeVisible();
  });

  test('应能测试数据源连接', async ({ page }) => {
    // 拦截测试连接请求
    await page.route('**/admin/sp/data-sources/*/test', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          message: '测试成功',
          data: {
            success: true,
            response_time: 150,
            status_code: 200,
            data: { message: '连接正常' }
          }
        }),
      });
    });
    
    // 点击第一行的测试连接按钮
    const firstRow = page.locator('.el-table__row').first();
    await firstRow.locator('button:has-text("测试连接")').click();
    
    // 等待测试结果对话框出现
    await expect(page.locator('.el-dialog')).toBeVisible();
    await expect(page.locator('.el-dialog__title')).toContainText('连接测试结果');
    
    // 验证成功结果
    await expect(page.locator('.test-success')).toBeVisible();
    await expect(page.locator('.test-success')).toContainText('连接测试成功');
    
    // 关闭对话框
    await page.click('button:has-text("关闭")');
  });

  test('应能切换数据源状态', async ({ page }) => {
    // 拦截状态更新请求
    await page.route('**/admin/sp/data-sources/*', (route) => {
      if (route.request().method() === 'PUT') {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            message: '状态更新成功'
          }),
        });
      } else {
        route.continue();
      }
    });
    
    // 获取第一行的状态开关
    const firstRow = page.locator('.el-table__row').first();
    const statusSwitch = firstRow.locator('.el-switch');
    
    // 获取当前状态
    const isChecked = await statusSwitch.locator('input').isChecked();
    
    // 点击切换状态
    await statusSwitch.click();
    
    // 等待成功提示
    await expect(page.locator('.el-message--success')).toBeVisible();
  });

  test('应能批量选择数据源', async ({ page }) => {
    // 点击第一行的选择框
    const firstRow = page.locator('.el-table__row').first();
    await firstRow.locator('.el-checkbox').click();
    
    // 验证选择框被选中
    await expect(firstRow.locator('.el-checkbox')).toHaveClass(/is-checked/);
    
    // 点击批量测试连接按钮
    await page.click('button:has-text("批量测试连接")');
    
    // 等待确认对话框出现
    await expect(page.locator('.el-message-box')).toBeVisible();
    
    // 点击取消按钮
    await page.click('button:has-text("取消")');
  });

  test('应能分页浏览数据', async ({ page }) => {
    // 验证分页组件存在
    await expect(page.locator('.el-pagination')).toBeVisible();
    
    // 点击下一页按钮
    const nextButton = page.locator('.el-pagination .btn-next');
    if (await nextButton.isVisible() && await nextButton.isEnabled()) {
      await nextButton.click();
      
      // 等待数据加载（由于我们拦截了请求，这里只是模拟）
      await page.waitForTimeout(500);
    }
    
    // 修改每页显示数量
    const pageSizeSelect = page.locator('.el-pagination .el-select').first();
    if (await pageSizeSelect.isVisible()) {
      await pageSizeSelect.click();
      await page.click('.el-select-dropdown__item:has-text("50")');
      
      // 等待数据加载
      await page.waitForTimeout(500);
    }
  });

  test('应能重置搜索条件', async ({ page }) => {
    // 填写搜索条件
    await page.fill('input[placeholder*="数据源名称"]', '测试搜索');
    await page.selectOption('select[placeholder*="类型"]', 'api');
    
    // 点击重置按钮
    await page.click('button:has-text("重置")');
    
    // 验证搜索条件已清空
    await expect(page.locator('input[placeholder*="数据源名称"]')).toHaveValue('');
    await expect(page.locator('select[placeholder*="类型"]')).toHaveValue('');
  });
});