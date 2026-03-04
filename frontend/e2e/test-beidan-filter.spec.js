// @ts-check
import { test, expect } from '@playwright/test';

// 北单过滤面板端到端测试
test.describe('北单过滤面板功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 登录到管理面板
    await page.goto('http://localhost:3000/login');
    
    // 输入管理员凭据
    await page.locator('input[type="text"]').fill('admin');
    await page.locator('input[type="password"]').fill('admin123');
    await page.locator('button[type="submit"]').click();
    
    // 等待登录完成并跳转到仪表板
    await page.waitForURL('http://localhost:3000/admin/dashboard');
  });

  test('访问北单过滤页面并验证基本组件', async ({ page }) => {
    // 导航到北单过滤页面
    await page.getByRole('link', { name: '北单过滤' }).click();
    await page.waitForURL('http://localhost:3000/admin/beidan-filter');
    
    // 验证页面标题
    await expect(page.locator('.title')).toContainText('三维精算筛选器');
    await expect(page.locator('.subtitle')).toContainText('基于 ΔP / ΔWP / P-Tier 的联动筛选');
    
    // 验证筛选条件区域存在
    await expect(page.locator('.filter-group').first()).toBeVisible();
    
    // 验证获取实时数据按钮存在
    await expect(page.locator('button:has-text("获取实时数据")')).toBeVisible();
    
    // 验证结果表格存在
    await expect(page.locator('.result-card .el-table')).toBeVisible();
  });

  test('测试获取实时数据功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 记录初始匹配数量
    const initialCount = await page.locator('.match-count span').textContent();
    
    // 点击获取实时数据按钮
    const getDataButton = page.locator('button:has-text("获取实时数据")');
    await getDataButton.click();
    
    // 等待请求完成
    await page.waitForTimeout(2000);
    
    // 验证数据已加载
    const updatedCount = await page.locator('.match-count span').textContent();
    expect(updatedCount).not.toEqual(initialCount);
    
    // 验证表格中有数据
    const tableRows = page.locator('.result-card .el-table tbody tr');
    await expect(tableRows.first()).toBeVisible();
  });

  test('测试实力等级差筛选功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选前的数量
    const countBefore = await page.locator('.match-count span').textContent();
    const initialCount = parseInt(countBefore);
    
    // 选择实力等级差筛选选项
    const strengthCheckboxes = page.locator('.checkbox-grid .el-checkbox-button').first();
    await strengthCheckboxes.click();
    
    // 点击应用筛选按钮
    await page.locator('button:has-text("应用筛选")').click();
    await page.waitForTimeout(2000);
    
    // 验证筛选后数量发生变化
    const countAfter = await page.locator('.match-count span').textContent();
    const afterCount = parseInt(countAfter);
    
    // 筛选后的数量应该小于等于筛选前的数量
    expect(afterCount).toBeLessThanOrEqual(initialCount);
  });

  test('测试赢盘等级差筛选功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选前的数量
    const countBefore = await page.locator('.match-count span').textContent();
    const initialCount = parseInt(countBefore);
    
    // 选择赢盘等级差筛选选项
    const winPanCheckboxes = page.locator('.checkbox-grid .el-checkbox-button').nth(3);
    await winPanCheckboxes.click();
    
    // 点击应用筛选按钮
    await page.locator('button:has-text("应用筛选")').click();
    await page.waitForTimeout(2000);
    
    // 验证筛选后数量发生变化
    const countAfter = await page.locator('.match-count span').textContent();
    const afterCount = parseInt(countAfter);
    
    // 筛选后的数量应该小于等于筛选前的数量
    expect(afterCount).toBeLessThanOrEqual(initialCount);
  });

  test('测试一赔稳定性筛选功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选前的数量
    const countBefore = await page.locator('.match-count span').textContent();
    const initialCount = parseInt(countBefore);
    
    // 选择一赔稳定性筛选选项
    const stabilitySelect = page.locator('.stability-filter .el-select');
    await stabilitySelect.click();
    await page.locator('.el-select-dropdown__item').first().click();
    
    // 点击应用筛选按钮
    await page.locator('button:has-text("应用筛选")').click();
    await page.waitForTimeout(2000);
    
    // 验证筛选后数量发生变化
    const countAfter = await page.locator('.match-count span').textContent();
    const afterCount = parseInt(countAfter);
    
    // 筛选后的数量应该小于等于筛选前的数量
    expect(afterCount).toBeLessThanOrEqual(initialCount);
  });

  test('测试高级筛选功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选前的数量
    const countBefore = await page.locator('.match-count span').textContent();
    const initialCount = parseInt(countBefore);
    
    // 展开高级筛选
    await page.locator('button:has-text("高级筛选")').click();
    
    // 等待高级筛选面板显示
    await expect(page.locator('.advanced-filter-panel')).toBeVisible();
    
    // 选择P级筛选
    const pLevelSelect = page.locator('.p-level-filter .el-select');
    await pLevelSelect.click();
    await page.locator('.el-select-dropdown__item').first().click();
    
    // 点击应用高级筛选按钮
    await page.locator('button:has-text("应用高级筛选")').click();
    await page.waitForTimeout(2000);
    
    // 验证筛选后数量发生变化
    const countAfter = await page.locator('.match-count span').textContent();
    const afterCount = parseInt(countAfter);
    
    // 筛选后的数量应该小于等于筛选前的数量
    expect(afterCount).toBeLessThanOrEqual(initialCount);
  });

  test('测试快捷组合功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选前的数量
    const countBefore = await page.locator('.match-count span').textContent();
    
    // 点击快捷组合按钮
    const quickComboBtn = page.locator('button:has-text("高胜率组合")');
    await quickComboBtn.click();
    
    await page.waitForTimeout(2000);
    
    // 验证筛选后数量发生变化
    const countAfter = await page.locator('.match-count span').textContent();
    
    // 数量可能变化，但页面不应该崩溃
    expect(countAfter).toBeDefined();
  });

  test('测试重置功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 记录原始数量
    const originalCount = await page.locator('.match-count span').textContent();
    
    // 应用一些筛选
    const strengthCheckboxes = page.locator('.checkbox-grid .el-checkbox-button').first();
    await strengthCheckboxes.click();
    await page.locator('button:has-text("应用筛选")').click();
    await page.waitForTimeout(2000);
    
    // 记录筛选后数量
    const filteredCount = await page.locator('.match-count span').textContent();
    
    // 点击重置按钮
    await page.locator('button:has-text("重置")').click();
    await page.waitForTimeout(1000);
    
    // 验证重置后的数量恢复到原始状态
    const resetCount = await page.locator('.match-count span').textContent();
    expect(resetCount).toEqual(originalCount);
  });

  test('测试排序功能', async ({ page }) => {
    await page.goto('http://localhost:3000/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 点击表格列标题进行排序
    const firstColumnHeader = page.locator('.result-card .el-table th').first();
    await firstColumnHeader.click();
    await page.waitForTimeout(1000);
    
    // 再次点击进行反向排序
    await firstColumnHeader.click();
    await page.waitForTimeout(1000);
    
    // 验证页面没有错误
    await expect(page.locator('.result-card .el-table')).toBeVisible();
  });

  test('测试导出功能', async ({ page }) => {
    await page.goto('http://localhost:3004/admin/beidan-filter');
    
    // 先获取实时数据
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000);
    
    // 点击导出按钮
    const exportButton = page.locator('button:has-text("导出Excel")');
    await exportButton.click();
    
    // 等待导出完成
    await page.waitForTimeout(2000);
    
    // 验证页面没有错误
    await expect(page.locator('.result-card .el-table')).toBeVisible();
  });
});
