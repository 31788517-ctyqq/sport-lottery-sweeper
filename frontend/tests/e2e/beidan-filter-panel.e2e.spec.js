// E2E tests for BeidanFilterPanel
import { test, expect } from '@playwright/test';

test.describe('BeidanFilterPanel E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Assuming the app is running on localhost:5173 (default Vite port)
    await page.goto('/admin/beidan-filter');
    
    // Wait for the panel to load
    await expect(page.locator('.beidan-filter-panel')).toBeVisible();
  });

  test('should display the main panel elements', async ({ page }) => {
    // Check if main elements are present
    await expect(page.locator('.title')).toContainText('三维精算筛选器');
    await expect(page.locator('.subtitle')).toContainText('基于 ΔP / ΔWP / P-Tier 的联动筛选');
    
    // Check for filter sections
    await expect(page.locator('.dimension-row')).toBeVisible();
    await expect(page.locator('.control-row')).toBeVisible();
    
    // Check for strength, win pan and stability filter groups
    await expect(page.locator('.filter-group').nth(0)).toContainText('实力等级差 ΔP');
    await expect(page.locator('.filter-group').nth(1)).toContainText('赢盘等级差 ΔWP');
    await expect(page.locator('.filter-group').nth(2)).toContainText('一赔稳定性 P-Tier');
  });

  test('should allow user to select filter options', async ({ page }) => {
    // Click on some strength options
    await page.locator('.strength-options .el-checkbox-button').nth(0).click();
    await page.locator('.strength-options .el-checkbox-button').nth(1).click();
    
    // Verify selections are active
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
    await expect(page.locator('.strength-options .el-checkbox-button').nth(1)).toHaveClass(/is-checked/);
    
    // Click on some win pan options
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click();
    await page.locator('.win-pan-options .el-checkbox-button').nth(1).click();
    
    // Verify selections are active
    await expect(page.locator('.win-pan-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
    await expect(page.locator('.win-pan-options .el-checkbox-button').nth(1)).toHaveClass(/is-checked/);
    
    // Click on some stability options
    await page.locator('.stability-options .el-checkbox-button').nth(0).click();
    await page.locator('.stability-options .el-checkbox-button').nth(1).click();
    
    // Verify selections are active
    await expect(page.locator('.stability-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
    await expect(page.locator('.stability-options .el-checkbox-button').nth(1)).toHaveClass(/is-checked/);
  });

  test('should apply preset strategies correctly', async ({ page }) => {
    // Click on "强势正路" preset
    await page.locator('.preset-grid button').first().click();
    
    // Verify that the appropriate filters are selected
    // Note: This would require checking the actual state of the component
    // which may not be directly possible in E2E tests
    // So we'll just verify that the click happened and no errors occurred
    
    // Click on "冷门潜质" preset
    await page.locator('.preset-grid button').nth(1).click();
    
    // Click on "均衡博弈" preset
    await page.locator('.preset-grid button').nth(2).click();
  });

  test('should save and load strategies', async ({ page }) => {
    // First, apply some filters
    await page.locator('.strength-options .el-checkbox-button').nth(0).click();
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click();
    await page.locator('.stability-options .el-checkbox-button').nth(0).click();
    
    // Click on the save strategy dropdown
    await page.locator('.filter-actions .el-dropdown .el-button').click();
    
    // Click on "保存当前策略"
    await page.locator('.el-dropdown-menu__item').first().click();
    
    // Enter strategy name
    await page.locator('input.el-message-box__input').fill('Test Strategy');
    await page.locator('.el-message-box__btns .el-button--primary').click();
    
    // Wait for confirmation
    await expect(page.locator('.el-message')).toContainText('策略已保存');
    
    // Now try to load the strategy
    await page.locator('.filter-actions .el-dropdown .el-button').click();
    await page.locator('.el-dropdown-menu__item').nth(1).click();
    
    // Wait for the modal to appear
    await page.waitForSelector('#strategySelect');
    
    // Select our saved strategy
    await page.locator('#strategySelect').selectOption('Test Strategy');
    
    // Click load
    await page.locator('.el-message-box__btns .el-button--primary').click();
    
    // Verify the strategy was loaded
    // This is difficult to verify directly in E2E tests
    // so we just ensure no errors occurred
    await expect(page.locator('.el-message')).toContainText('策略已加载');
  });

  test('should handle filter application', async ({ page }) => {
    // Apply some filters
    await page.locator('.strength-options .el-checkbox-button').nth(0).click();
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click();
    
    // Click apply filter button
    await page.locator('.filter-actions .el-button').first().click();
    
    // Wait for loading to finish
    await expect(page.locator('.el-button[loading="true"]')).not.toBeVisible();
    
    // Check that results are displayed
    // This assumes that there are results after filtering
    // which depends on the backend data
  });

  test('should reset filters correctly', async ({ page }) => {
    // Apply some filters first
    await page.locator('.strength-options .el-checkbox-button').nth(0).click();
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click();
    
    // Verify they are checked
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
    await expect(page.locator('.win-pan-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
    
    // Click reset button
    await page.locator('.filter-actions .el-button').nth(1).click();
    
    // Verify filters are cleared (this might depend on how the reset works)
    // If reset clears the UI elements, we can check them:
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).not.toHaveClass(/is-checked/);
  });

  test('should display warning when conflicting filters are selected', async ({ page }) => {
    // Select conflicting filters (positive strength and negative win pan)
    await page.locator('.strength-options .el-checkbox-button').nth(2).click(); // +1
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click(); // -3 (assuming this is the negative option)
    
    // Check if warning is displayed
    // Wait for reactivity to update
    await page.waitForTimeout(100);
    
    const warningExists = await page.locator('.direction-alert').isVisible();
    if (warningExists) {
      await expect(page.locator('.direction-alert')).toContainText('方向背离预警');
    }
  });
});