/**
 * BeidanFilterPanel 基础功能验证测试
 * 简化版测试，验证核心功能而不依赖复杂的交互
 */

const { test, expect } = require('@playwright/test');

test.describe('BeidanFilterPanel 基础功能验证', () => {
  test.beforeEach(async ({ page }) => {
    // 直接进 BeidanFilterPanel 页面
    await page.goto('/admin/beidan-filter');
    
    // 等待页面基本加载完成
    await page.waitForLoadState('networkidle', { timeout: 15000 });
  });

  test('1. 页面基本加载和文案检查', async ({ page }) => {
    console.log('检查页面基本加载...');
    
    // 检查页面标题或主要内容区域
    await expect(page.locator('h1, h2, h3').first()).toBeVisible({ timeout: 10000 });
    
    // 检查FilterSection是否加载
    await expect(page.locator('.filter-section').first()).toBeVisible({ timeout: 10000 });
    
    // 检查关键文案（组标题）
    await expect(page.locator('text=策略应用和保存').first()).toBeVisible();
    await expect(page.locator('text=其它条件').first()).toBeVisible();
    
    console.log('✓ 页面基本加载和文案检查通过');
  });

  test('2. 策略保存下拉按钮检查', async ({ page }) => {
    console.log('检查策略保存功能...');
    
    // 检查保存策略按钮存在
    const saveButton = page.locator('button:has-text("保存策略")').first();
    await expect(saveButton).toBeVisible({ timeout: 10000 });
    
    // 悬停查看下拉菜单
    await saveButton.hover();
    await page.waitForTimeout(500);
    
    // 检查下拉菜单项
    await expect(page.locator('text=保存当前策略').first()).toBeVisible();
    await expect(page.locator('text=修改和删除策略').first()).toBeVisible();
    
    console.log('✓ 策略保存下拉按钮检查通过');
  });

  test('3. 应用筛选按钮检查', async ({ page }) => {
    console.log('检查应用筛选功能...');
    
    // 检查应用筛选按钮存在并可点击
    const applyButton = page.locator('button:has-text("应用筛选")').first();
    await expect(applyButton).toBeVisible({ timeout: 10000 });
    await expect(applyButton).toBeEnabled();
    
    console.log('✓ 应用筛选按钮检查通过');
  });

  test('4. 筛选条件控件检查', async ({ page }) => {
    console.log('检查筛选条件控件...');
    
    // 检查各种筛选控件存在
    await expect(page.locator('text=实力等级差 ΔP').first()).toBeVisible();
    await expect(page.locator('text=赢盘等级差 ΔWP').first()).toBeVisible();
    await expect(page.locator('text=一赔稳定性 P-Tier').first()).toBeVisible();
    await expect(page.locator('label').filter({ hasText: '联赛筛选' }).first()).toBeVisible();
    
    console.log('✓ 筛选条件控件检查通过');
  });

  test('5. 新旧文案对比验证', async ({ page }) => {
    console.log('验证新旧文案替换...');
    
    // 确认旧文案不存在
    await expect(page.locator('text=排序方式')).toHaveCount(0);
    await expect(page.locator('text=筛选策略')).toHaveCount(0);
    await expect(page.locator('text=快捷组合')).toHaveCount(0);
    await expect(page.locator('text=加载策略')).toHaveCount(0);
    
    // 确认新文案存在
    await expect(page.locator('text=策略应用和保存').first()).toBeVisible();
    
    console.log('✓ 新旧文案对比验证通过');
  });
});