const { test, expect } = require('@playwright/test');

// 测试比赛数据管理菜单的5个子菜单页面
test.describe('比赛数据管理菜单端到端测试', () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    page = await browser.newPage();
  });

  test.afterAll(async () => {
    await page.close();
  });

  // 登录函数
  const login = async () => {
    await page.goto('/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    
    // 等待登录成功
    await page.waitForURL('**/admin/**');
    await expect(page).toHaveURL(/\/admin\//);
  };

  test('用户登录', async () => {
    await login();
  });

  test.describe('联赛管理页面测试', () => {
    test.beforeEach(async () => {
      // 导航到联赛管理页面
      await page.locator('text=比赛数据管理').click();
      await page.locator('text=联赛管理').click();
      await page.waitForURL('**/admin/match-data/leagues');
    });

    test('页面加载和元素显示', async () => {
      await expect(page.locator('h1:has-text("联赛管理")')).toBeVisible();
      await expect(page.locator('.el-card')).toBeVisible();
      await expect(page.locator('button:has-text("添加联赛")')).toBeVisible();
    });

    test('显示联赛列表', async () => {
      await expect(page.locator('.el-table')).toBeVisible();
      // 检查是否有表格行，即使为空也需要表格存在
      await expect(page.locator('.el-table')).toBeAttached();
    });

    test('添加联赛功能', async () => {
      const initialRowCount = await page.locator('.el-table__row').count();
      
      await page.click('button:has-text("添加联赛")');
      
      // 等待弹窗出现
      await expect(page.locator('.el-dialog')).toBeVisible();
      
      // 填写表单
      await page.fill('input[placeholder="请输入联赛名称"]', `测试联赛${Date.now()}`);
      await page.fill('input[placeholder="请输入联赛国家"]', '中国');
      await page.fill('textarea[placeholder="请输入联赛描述"]', '这是测试联赛');
      
      // 选择联赛级别
      await page.locator('.el-select').nth(0).click();
      await page.locator('.el-popper').getByText('顶级').click();
      
      // 选择联赛状态
      await page.locator('.el-select').nth(1).click();
      await page.locator('.el-popper').getByText('启用').click();
      
      await page.click('button:has-text("确定")');
      
      // 等待操作完成
      await page.waitForResponse(response => response.url().includes('/leagues') && response.status() === 200);
      
      // 检查是否添加成功，行数应该增加
      const finalRowCount = await page.locator('.el-table__row').count();
      expect(finalRowCount).toBeGreaterThan(initialRowCount);
    });

    test('编辑联赛功能', async () => {
      const editButton = page.locator('button:has-text("编辑")').first();
      await expect(editButton).toBeVisible();
      await editButton.click();
      
      // 等待弹窗出现
      await expect(page.locator('.el-dialog')).toBeVisible();
      
      // 修改联赛名称
      await page.fill('input[placeholder="请输入联赛名称"]', `修改联赛${Date.now()}`);
      await page.click('button:has-text("确定")');
      
      // 等待操作完成
      await page.waitForResponse(response => response.url().includes('/leagues') && response.status() === 200);
      
      // 稍等一下让UI更新
      await page.waitForTimeout(500);
    });
  });

  test.describe('比赛管理页面测试', () => {
    test.beforeEach(async () => {
      // 导航到比赛管理页面
      await page.locator('text=比赛数据管理').click();
      await page.locator('text=比赛管理').click();
      await page.waitForURL('**/admin/match-data/matches');
    });

    test('页面加载和元素显示', async () => {
      await expect(page.locator('h1:has-text("比赛管理")')).toBeVisible();
      await expect(page.locator('.el-card')).toBeVisible();
      await expect(page.locator('button:has-text("添加比赛")')).toBeVisible();
    });

    test('显示比赛列表', async () => {
      await expect(page.locator('.el-table')).toBeVisible();
      await expect(page.locator('.el-table')).toBeAttached();
    });

    test('添加比赛功能', async () => {
      const initialRowCount = await page.locator('.el-table__row').count();
      
      await page.click('button:has-text("添加比赛")');
      
      // 等待弹窗出现
      await expect(page.locator('.el-dialog')).toBeVisible();
      
      // 选择联赛
      await page.locator('.el-select').first().click();
      // 选择第一个可用的联赛选项
      const options = page.locator('.el-popper .el-select-dropdown__item:not(.is-disabled)');
      if (await options.count() > 0) {
        await options.first().click();
      } else {
        // 如果没有联赛，则先创建一个
        console.log('没有可用联赛，需要先创建一个');
        await page.locator('button:has-text("取消")').click();
        // 先去联赛管理页面创建联赛
        await page.locator('text=联赛管理').click();
        await page.waitForTimeout(1000);
        
        await page.click('button:has-text("添加联赛")');
        await page.fill('input[placeholder="请输入联赛名称"]', `测试联赛${Date.now()}`);
        await page.fill('input[placeholder="请输入联赛国家"]', '中国');
        await page.fill('textarea[placeholder="请输入联赛描述"]', '这是测试联赛');
        
        await page.locator('.el-select').nth(0).click();
        await page.locator('.el-popper').getByText('顶级').click();
        
        await page.locator('.el-select').nth(1).click();
        await page.locator('.el-popper').getByText('启用').click();
        
        await page.click('button:has-text("确定")');
        await page.waitForResponse(response => response.url().includes('/leagues') && response.status() === 200);
        
        // 返回比赛管理页面
        await page.locator('text=比赛管理').click();
        await page.waitForTimeout(1000);
        
        // 再次尝试添加比赛
        await page.click('button:has-text("添加比赛")');
        await expect(page.locator('.el-dialog')).toBeVisible();
        
        await page.locator('.el-select').first().click();
        await page.locator('.el-popper .el-select-dropdown__item:not(.is-disabled)').first().click();
      }
      
      // 填写表单
      await page.fill('input[placeholder="请输入主队名称"]', `主队${Date.now()}`);
      await page.fill('input[placeholder="请输入客队名称"]', `客队${Date.now()}`);
      
      // 设置比赛时间
      await page.click('input[placeholder="选择日期时间"]');
      await page.locator('.el-date-picker').isVisible();
      await page.locator('.el-date-table td.available').first().click();
      
      await page.click('button:has-text("确定")');
      
      // 等待操作完成
      await page.waitForResponse(response => response.url().includes('/matches') && response.status() === 200);
      
      // 检查是否添加成功，行数应该增加
      const finalRowCount = await page.locator('.el-table__row').count();
      expect(finalRowCount).toBeGreaterThan(initialRowCount);
    });

    test('编辑比赛功能', async () => {
      const editButton = page.locator('button:has-text("编辑")').first();
      if (await editButton.count() > 0) {
        await editButton.click();
        
        // 等待弹窗出现
        await expect(page.locator('.el-dialog')).toBeVisible();
        
        // 修改主队名称
        await page.fill('input[placeholder="请输入主队名称"]', `修改主队${Date.now()}`);
        await page.click('button:has-text("确定")');
        
        // 等待操作完成
        await page.waitForResponse(response => response.url().includes('/matches') && response.status() === 200);
        
        // 稍等一下让UI更新
        await page.waitForTimeout(500);
      }
    });
  });

  test.describe('赔率管理页面测试', () => {
    test.beforeEach(async () => {
      // 导航到赔率管理页面
      await page.locator('text=比赛数据管理').click();
      await page.locator('text=赔率管理').click();
      await page.waitForURL('**/admin/match-data/odds');
    });

    test('页面加载和元素显示', async () => {
      await expect(page.locator('h1:has-text("赔率管理")')).toBeVisible();
      await expect(page.locator('.el-card')).toBeVisible();
      await expect(page.locator('.el-table')).toBeVisible();
    });

    test('显示赔率数据', async () => {
      await expect(page.locator('.el-table')).toBeAttached();
    });

    test('搜索功能', async () => {
      await page.fill('input[placeholder="请输入联赛名称搜索"]').fill('英超');
      await page.click('button:has-text("搜索")');
      
      // 等待搜索完成
      await page.waitForTimeout(1000);
      
      // 检查搜索结果
      await expect(page.locator('.el-table')).toBeAttached();
    });
  });

  test.describe('竞彩赛程页面测试', () => {
    test.beforeEach(async () => {
      // 导航到竞彩赛程页面
      await page.locator('text=比赛数据管理').click();
      await page.locator('text=竞彩赛程').click();
      await page.waitForURL('**/admin/match-data/schedule/jczq');
    });

    test('页面加载和元素显示', async () => {
      await expect(page.locator('h1:has-text("竞彩赛程")')).toBeVisible();
      await expect(page.locator('.el-card')).toBeVisible();
      await expect(page.locator('button:has-text("添加赛程")')).toBeVisible();
    });

    test('显示赛程列表', async () => {
      await expect(page.locator('.el-table')).toBeVisible();
      await expect(page.locator('.el-table')).toBeAttached();
    });

    test('筛选功能', async () => {
      const selectElement = page.locator('.el-select');
      if (await selectElement.count() > 0) {
        await selectElement.first().click();
        const options = page.locator('.el-popper .el-select-dropdown__item');
        if (await options.count() > 1) {
          await options.nth(1).click(); // 选择第二个选项
        }
        
        // 等待筛选完成
        await page.waitForTimeout(1000);
        
        // 检查筛选结果
        await expect(page.locator('.el-table')).toBeAttached();
      }
    });
  });

  test.describe('北单赛程页面测试', () => {
    test.beforeEach(async () => {
      // 导航到北单赛程页面
      await page.locator('text=比赛数据管理').click();
      await page.locator('text=北单赛程').click();
      await page.waitForURL('**/admin/match-data/schedule/bd');
    });

    test('页面加载和元素显示', async () => {
      await expect(page.locator('h1:has-text("北单赛程")')).toBeVisible();
      await expect(page.locator('.el-card')).toBeVisible();
      await expect(page.locator('.el-table')).toBeVisible();
    });

    test('显示北单赛程列表', async () => {
      await expect(page.locator('.el-table')).toBeAttached();
    });

    test('批量操作功能', async () => {
      const checkboxes = page.locator('.el-checkbox').nth(1);
      if (await checkboxes.count() > 0) {
        // 选择第一行
        await checkboxes.click();
        
        // 执行批量删除（如果按钮存在）
        const batchDeleteBtn = page.locator('button:has-text("批量删除")');
        if (await batchDeleteBtn.count() > 0) {
          await batchDeleteBtn.click();
          await page.locator('button:has-text("确定")').click();
          
          // 等待操作完成
          await page.waitForTimeout(1000);
        }
      }
    });
  });

  test('导航到首页', async () => {
    await page.locator('text=Dashboard').first().click();
    await page.waitForURL('**/admin/dashboard');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
  });
});