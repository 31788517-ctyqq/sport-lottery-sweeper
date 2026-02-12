/**
 * BeidanFilterPanel 功能验收 E2E 测试（最终正确版）
 * 基于实际DOM结构验证第 1-3 项功能
 */

const { test, expect } = require('@playwright/test');

test.describe('BeidanFilterPanel 功能验收', () => {
  test.beforeEach(async ({ page }) => {
    // 直接进 BeidanFilterPanel 页面，假设已有登录态（用于本地调试）
    await page.goto('/admin/beidan-filter');
    await page.waitForSelector('button:has-text("应用筛选")', { timeout: 15000 });
  });

  test('1. 文案命名一致性检查', async ({ page }) => {
    console.log('检查文案命名一致性...');
    
    // 检查组标题中的文案（策略应用和保存）
    await expect(page.locator('.filter-section >> text=策略应用和保存').first()).toBeVisible();
    await expect(page.locator('text=其它条件').first()).toBeVisible();
    
    // 检查下拉菜单项中的文案（修改和删除策略）
    // 先悬停或点击下拉按钮才能看到菜单项
    await page.locator('button:has-text("保存策略")').first().hover();
    await page.waitForTimeout(500);
    await expect(page.locator('text=修改和删除策略').first()).toBeVisible();

    // 确认旧的文案已经不存在
    await expect(page.locator('text=排序方式')).toHaveCount(0);
    await expect(page.locator('text=筛选策略')).toHaveCount(0);
    await expect(page.locator('text=快捷组合')).toHaveCount(0);
    await expect(page.locator('text=加载策略')).toHaveCount(0);
    
    console.log('✓ 文案命名一致性检查通过');
  });

  test('2. 当前应用逻辑验证', async ({ page }) => {
    console.log('验证当前应用逻辑...');
    
    // 点击应用筛选按钮（走筛选API）
    await page.locator('button:has-text("应用筛选")').first().click();
    await page.waitForTimeout(2000);

    // 检查是否显示了当前应用和统计信息
    await expect(page.locator('text=当前应用').first()).toBeVisible({ timeout: 10000 });
    
    // 点击当前应用按钮
    await page.locator('text=当前应用', { exact: true }).first().click();
    await page.waitForTimeout(1000);

    // 验证统计卡片和表格显示
    const statsVisible = await page.locator('.stats-card').isVisible();
    expect(statsVisible).toBe(true);

    const tableVisible = await page.locator('table').isVisible();
    expect(tableVisible).toBe(true);
    
    console.log('✓ 当前应用逻辑验证通过');
  });

  test('3. 保存策略功能', async ({ page }) => {
    console.log('测试保存策略功能...');
    
    // 点击保存策略下拉按钮
    await page.locator('button:has-text("保存策略")').first().click();
    await page.waitForTimeout(500);
    
    // 点击保存当前策略菜单项
    await page.locator('text=保存当前策略').first().click();

    // 填写策略名称并提交
    await page.locator('input[placeholder*="策略名称"]').first().fill('test_strategy');
    await page.locator('button:has-text("确定")').first().click();

    // 验证保存成功消息
    await expect(page.locator('text=策略保存成功').first()).toBeVisible({ timeout: 5000 });
    
    console.log('✓ 保存策略功能测试通过');
  });

  test('4. 修改和删除策略功能', async ({ page }) => {
    console.log('测试修改和删除策略功能...');
    
    // 点击保存策略下拉按钮
    await page.locator('button:has-text("保存策略")').first().click();
    await page.waitForTimeout(500);
    
    // 点击修改和删除策略菜单项
    await page.locator('text=修改和删除策略').first().click();

    // 验证管理弹窗显示
    await expect(page.locator('text=管理筛选策略').first()).toBeVisible({ timeout: 5000 });
    await expect(page.locator('button:has-text("新建策略")').first()).toBeVisible();
    await expect(page.locator('button:has-text("编辑")').first()).toBeVisible();
    await expect(page.locator('button:has-text("删除")').first()).toBeVisible();
    await expect(page.locator('button:has-text("关闭")').first()).toBeVisible();
    
    console.log('✓ 修改和删除策略功能测试通过');
  });
});