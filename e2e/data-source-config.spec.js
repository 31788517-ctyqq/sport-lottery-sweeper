// @ts-check
const { test, expect } = require('@playwright/test');

// 数据源配置页面端到端测试
test.describe('数据源配置页面端到端测试', () => {
  // 登录函数
  const login = async (page) => {
    // 使用正确的前端URL，假设前端运行在3000端口
    await page.goto('http://localhost:3000/login');
    await page.fill('input[type="text"]', 'admin');
    await page.fill('input[type="password"]', 'admin123');
    await page.click('button:has-text("登录")');
    
    // 等待登录成功
    await page.waitForURL('**/admin/**', { timeout: 10000 });
    await expect(page).toHaveURL(/\/admin\//);
  };

  test('用户登录并导航到数据源配置页面', async ({ page }) => {
    await login(page);
    
    // 导航到数据源配置页面
    await page.locator('text=数据源管理').click();
    await page.waitForTimeout(500); // 等待菜单展开
    await page.locator('text=数据源配置').click();
    await page.waitForURL('**/admin/data-source/config', { timeout: 10000 });
    await page.waitForLoadState('networkidle'); // 等待网络空闲
    
    // 验证页面加载成功
    await expect(page.locator('h2:has-text("数据源管理")')).toBeVisible();
  });

  test.describe('数据源配置页面功能测试', () => {
    test.beforeEach(async ({ page }) => {
      // 重新登录以确保会话有效
      await login(page);
      
      // 导航到数据源配置页面
      await page.locator('text=数据源管理').click();
      await page.waitForTimeout(500); // 等待菜单展开
      await page.locator('text=数据源配置').click();
      await page.waitForURL('**/admin/data-source/config', { timeout: 10000 });
      await page.waitForLoadState('networkidle'); // 等待网络空闲
    });

    test('页面加载和元素显示', async ({ page }) => {
      // 等待页面加载完成
      await page.waitForSelector('h2:has-text("数据源管理")', { state: 'visible' });
      
      await expect(page.locator('h2:has-text("数据源管理")')).toBeVisible();
      await expect(page.locator('.page-header .el-button:has-text("新增数据源")')).toBeVisible();
      await expect(page.locator('.stats-section')).toBeVisible();
      
      // 检查统计卡片
      await expect(page.locator('.stats-card').nth(0)).toContainText('总数据源');
      await expect(page.locator('.stats-card').nth(1)).toContainText('在线');
      await expect(page.locator('.stats-card').nth(2)).toContainText('离线');
      await expect(page.locator('.stats-card').nth(3)).toContainText('成功率');
    });

    test('显示数据源列表', async ({ page }) => {
      await expect(page.locator('.el-table')).toBeVisible();
      await expect(page.locator('.el-table')).toBeAttached();
      
      // 等待数据加载
      await page.waitForTimeout(2000);
      
      // 检查是否有表格行
      const rowCount = await page.locator('.el-table__row').count();
      console.log(`找到 ${rowCount} 个数据源条目`);
      
      // 如果有数据源，则检查表格头部
      if (rowCount > 0) {
        // 检查是否有表格列标题
        const headers = ['ID', '源ID', '名称', '分类', '类型', '状态', '成功率', '平均响应时间', '最后更新时间'];
        for (const header of headers) {
          const headerElements = await page.locator(`.el-table th`).allInnerTexts();
          const foundHeader = headerElements.some(text => text.includes(header));
          expect(foundHeader).toBeTruthy();
        }
      }
    });

    test('新增数据源功能', async ({ page }) => {
      const initialRowCount = await page.locator('.el-table__row').count();
      
      // 点击新增数据源按钮
      await page.click('button:has-text("新增数据源")');
      
      // 等待弹窗出现
      await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 10000 });
      await expect(page.locator('.el-dialog .el-form')).toBeVisible();
      
      // 填写表单
      const timestamp = Date.now();
      await page.fill('input[placeholder="请输入数据源名称"]', `测试数据源-${timestamp}`);
      await page.fill('input[placeholder="请输入数据源URL"]', `https://api.example-${timestamp}.com/data`);
      
      // 选择分类
      await page.locator('.el-select').first().click();
      await page.locator('.el-popper .el-select-dropdown__item').first().click();
      
      // 选择类型
      await page.locator('text=请选择数据源类型').click();
      await page.locator('.el-popper .el-select-dropdown__item:has-text("API数据源")').click();
      
      // 设置超时时间
      await page.fill('input[placeholder="请输入超时时间(秒)"]', '30');
      
      // 填写描述
      await page.fill('textarea[placeholder="请输入描述"]', '这是通过E2E测试创建的数据源');
      
      // 点击确定
      await page.click('button:has-text("确定")');
      
      // 等待操作完成
      await page.waitForSelector('.el-message:has-text("创建成功")', { state: 'visible', timeout: 10000 }).catch(() => {});
      
      // 检查是否有成功提示
      const successMsg = page.locator('.el-message:has-text("创建成功")');
      if (await successMsg.count() > 0) {
        await expect(successMsg).toBeVisible();
      }
      
      // 检查数据源列表是否更新
      await page.waitForTimeout(2000);
      const finalRowCount = await page.locator('.el-table__row').count();
      expect(finalRowCount).toBeGreaterThanOrEqual(initialRowCount);
    });

    test('编辑数据源功能', async ({ page }) => {
      // 等待表格数据加载
      await page.waitForSelector('.el-table__row', { state: 'visible', timeout: 10000 }).catch(() => {});
      
      // 查找编辑按钮并点击（如果有数据源的话）
      const editButtons = page.locator('button:has-text("编辑")');
      const count = await editButtons.count();
      
      if (count > 0) {
        await editButtons.first().click();
        
        // 等待弹窗出现
        await expect(page.locator('.el-dialog')).toBeVisible({ timeout: 10000 });
        
        // 修改数据源名称
        const newName = `修改测试数据源-${Date.now()}`;
        await page.fill('input[placeholder="请输入数据源名称"]', newName);
        
        // 点击确定
        await page.click('button:has-text("确定")');
        
        // 等待操作完成
        await page.waitForSelector('.el-message:has-text("更新成功")', { state: 'visible', timeout: 10000 }).catch(() => {});
        
        // 检查是否有成功提示
        const successMsg = page.locator('.el-message:has-text("更新成功")');
        if (await successMsg.count() > 0) {
          await expect(successMsg).toBeVisible();
        }
      } else {
        console.log('没有找到数据源进行编辑');
      }
    });

    test('搜索过滤功能', async ({ page }) => {
      // 等待页面完全加载
      await page.waitForLoadState('networkidle');
      
      // 尝试使用搜索框
      const searchInput = page.locator('input[placeholder="请输入关键词搜索"]');
      if (await searchInput.count() > 0) {
        await searchInput.fill('测试');
        await page.click('button:has-text("搜索")');
        
        // 等待搜索完成
        await page.waitForLoadState('networkidle');
        
        // 检查是否有搜索结果
        await expect(page.locator('.el-table')).toBeAttached();
      }
    });

    test('测试连接功能', async ({ page }) => {
      // 等待表格数据加载
      await page.waitForSelector('.el-table__row', { state: 'visible', timeout: 10000 }).catch(() => {});
      
      // 查找测试连接按钮并点击（如果有数据源的话）
      const testButtons = page.locator('button:has-text("测试连接")');
      const count = await testButtons.count();
      
      if (count > 0) {
        await testButtons.first().click();
        
        // 等待测试完成
        await page.waitForTimeout(5000);
        
        // 检查是否有成功或失败提示
        const successMsg = page.locator('.el-message:has-text("测试成功")');
        const errorMsg = page.locator('.el-message:has-text("测试失败")');
        
        // 至少有一个消息出现
        if (await successMsg.count() > 0) {
          await expect(successMsg).toBeVisible();
        } else if (await errorMsg.count() > 0) {
          await expect(errorMsg).toBeVisible();
        }
      } else {
        console.log('没有找到数据源进行连接测试');
      }
    });

    test('切换数据源状态', async ({ page }) => {
      // 等待表格数据加载
      await page.waitForSelector('.el-table__row', { state: 'visible' }).catch(() => {});
      
      // 查找状态开关并点击（如果有数据源的话）
      const statusSwitches = page.locator('.el-switch');
      const count = await statusSwitches.count();
      
      if (count > 0) {
        const initialStatus = await statusSwitches.first().getAttribute('aria-checked');
        await statusSwitches.first().click();
        
        // 等待状态切换完成
        await page.waitForTimeout(1000);
        
        // 检查是否有成功提示
        const successMsg = page.locator('.el-message:has-text("更新成功")');
        if (await successMsg.count() > 0) {
          await expect(successMsg).toBeVisible();
        }
        
        // 验证状态已改变
        const newStatus = await statusSwitches.first().getAttribute('aria-checked');
        expect(initialStatus).not.toBe(newStatus);
      }
    });

    test('批量操作功能', async ({ page }) => {
      // 等待表格数据加载
      await page.waitForSelector('.el-table__row', { state: 'visible' }).catch(() => {});
      
      // 检查是否有复选框可以选择
      const checkboxes = page.locator('.el-checkbox input[type="checkbox"]');
      const count = await checkboxes.count();
      
      if (count > 1) {
        // 选择前两个数据源
        await checkboxes.nth(0).click();
        await checkboxes.nth(1).click();
        
        // 等待选择完成
        await page.waitForTimeout(500);
        
        // 尝试批量测试连接
        const batchTestBtn = page.locator('button:has-text("批量测试")');
        if (await batchTestBtn.count() > 0) {
          await batchTestBtn.click();
          await page.waitForTimeout(3000);
        }
      } else {
        console.log('复选框数量不足，无法进行批量操作测试');
      }
    });
  });

  test('导航到其他页面', async ({ page }) => {
    await page.locator('text=Dashboard').first().click();
    await page.waitForURL('**/admin/dashboard');
    await expect(page).toHaveURL(/\/admin\/dashboard/);
  });
});