/**
 * BeidanFilterPanel 功能验收 E2E 测试（最终优化版）
 * 验证第 1-3 项：命名一致性、当前应用逻辑、策略应用和保存功能
 */

const { test, expect } = require('@playwright/test');

test.describe('BeidanFilterPanel 功能验收', () => {
  test.beforeEach(async ({ page }) => {
    // 直接进 BeidanFilterPanel 页面，假设已有登录态（用于本地调试）
    await page.goto('/admin/beidan-filter');
    await page.waitForSelector('button:has-text("应用筛选")', { timeout: 15000 });
  });

  test('1. 文案命名一致性检查', async ({ page }) => {
    await expect(page.locator('.filter-section >> text=策略筛选').first()).toBeVisible();
    await expect(page.locator('text=其它条件').first()).toBeVisible();
    await expect(page.locator('text=策略应用和保存').first()).toBeVisible();
    await expect(page.locator('text=修改和删除策略').first()).toBeVisible();

    await expect(page.locator('text=排序方式')).toHaveCount(0);
    await expect(page.locator('text=筛选策略')).toHaveCount(0);
    await expect(page.locator('text=快捷组合')).toHaveCount(0);
    await expect(page.locator('text=加载策略')).toHaveCount(0);
  });

  test('2. 当前应用逻辑验证', async ({ page }) => {
    await page.getByRole('button', { name: '应用筛选' }).click();
    await page.waitForTimeout(1000);

    await page.getByText('当前应用', { exact: true }).click();
    await page.waitForTimeout(1000);

    const statsVisible = await page.locator('.stats-card').isVisible();
    const resultsVisible = await page.locator('.results-section').isVisible();
    expect(statsVisible).toBeTruthy();
    expect(resultsVisible).toBeTruthy();
  });

  test('3. 保存策略功能', async ({ page }) => {
    await page.getByRole('button', { name: '策略应用和保存' }).click();
    await page.getByText('保存当前策略').click();
    
    await page.getByPlaceholder(/策略名称/).fill('test_strategy');
    await page.getByRole('button', { name: '保存' }).click();
    await page.waitForTimeout(500);

    await expect(page.getByText('test_strategy')).toBeVisible();
  });

  test('4. 修改和删除策略功能', async ({ page }) => {
    await page.getByRole('button', { name: '策略应用和保存' }).click();
    await page.getByText('修改和删除策略').click();
    
    await expect(page.locator('.el-message-box__title')).toHaveText('策略管理');
    await expect(page.getByRole('button', { name: '修改保存' })).toBeVisible();
    await expect(page.getByRole('button', { name: '删除策略' })).toBeVisible();
  });
});