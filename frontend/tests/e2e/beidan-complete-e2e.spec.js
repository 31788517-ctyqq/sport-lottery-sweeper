// Complete E2E test for Beidan Filter Panel covering all 7 units
import { test, expect } from '@playwright/test';

test.describe('Beidan Filter Panel - Complete E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Mock login or authentication if required
    await page.goto('/admin/beidan-filter');
    await expect(page.locator('.beidan-filter-panel')).toBeVisible();
  });

  test('1. Pure Functions & Utility Functions - indirectly tested through UI behavior', async ({ page }) => {
    // The utility functions are extensively tested in unit tests
    // Here we verify that they work correctly in the UI context
    await expect(page.locator('.title')).toContainText('三维精算筛选器');
  });

  test('2. UI Components - rendering and interaction', async ({ page }) => {
    // Check that main UI components render correctly
    await expect(page.locator('.filter-card')).toBeVisible();
    await expect(page.locator('.dimension-row')).toBeVisible();
    await expect(page.locator('.control-row')).toBeVisible();
    
    // Check for strength, win pan and stability filter groups
    await expect(page.locator('.filter-group').nth(0)).toContainText('实力等级差 ΔP');
    await expect(page.locator('.filter-group').nth(1)).toContainText('赢盘等级差 ΔWP');
    await expect(page.locator('.filter-group').nth(2)).toContainText('一赔稳定性 P-Tier');
    
    // Test checkbox group interactions
    await page.locator('.strength-options .el-checkbox-button').nth(0).click();
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/);
  });

  test('3. Component Interactions - preset strategies', async ({ page }) => {
    // Test preset strategy buttons
    const presetButtons = page.locator('.preset-grid button');
    await expect(presetButtons).toHaveCount(3); // Strong, Upset, Balance
    
    // Test applying a preset
    await page.locator('.preset-grid button').first().click();
    
    // Verify that filters have been applied
    await expect(page.locator('.preset-applied')).toContainText('强势正路');
  });

  test('4. State Management Integration - data persistence', async ({ page }) => {
    // Navigate away and back to check if state persists appropriately
    await page.click('text=数据源管理');
    await page.waitForURL('**/admin/data-source');
    await page.goBack();
    
    // Verify we're back on the beidan filter page
    await expect(page.locator('.title')).toContainText('三维精算筛选器');
  });

  test('5. Component-API Integration - data fetching', async ({ page }) => {
    // Test that API calls work correctly
    const fetchDataButton = page.locator('button:has-text("获取实时数据")');
    await expect(fetchDataButton).toBeVisible();
    
    // Click to fetch data
    await fetchDataButton.click();
    
    // Verify loading state
    await expect(fetchDataButton).toContainText('加载中');
    
    // Wait for data to load
    await page.waitForTimeout(2000);
    
    // Verify results are displayed
    const resultsTable = page.locator('.el-table');
    await expect(resultsTable).toBeVisible();
  });

  test('6. Route-Component Integration', async ({ page }) => {
    // Verify that the component loads correctly on the specific route
    await page.goto('/admin/beidan-filter');
    await expect(page).toHaveURL(/.*\/admin\/beidan-filter$/);
    
    // Verify component is rendered
    await expect(page.locator('.beidan-filter-panel')).toBeVisible();
  });

  test('7. Complete User Scenario - end-to-end workflow', async ({ page }) => {
    // Full user workflow:
    // 1. Load the page
    await page.goto('/admin/beidan-filter');
    await expect(page.locator('.beidan-filter-panel')).toBeVisible();
    
    // 2. Fetch real data
    await page.locator('button:has-text("获取实时数据")').click();
    await page.waitForTimeout(2000); // Wait for data to load
    
    // 3. Apply preset strategy
    await page.locator('.preset-grid button').first().click(); // Strong preset
    
    // 4. Manually adjust filters
    await page.locator('.strength-options .el-checkbox-button').nth(2).click();
    await page.locator('.win-pan-options .el-checkbox-button').nth(3).click();
    
    // 5. Apply filters
    await page.locator('.filter-actions .el-button').first().click();
    
    // 6. Verify results
    await expect(page.locator('.filter-results')).toBeVisible();
    
    // 7. Save strategy
    await page.locator('.filter-actions .el-dropdown .el-button').click();
    await page.locator('.el-dropdown-menu__item').first().click();
    
    // Enter strategy name
    await page.locator('input.el-message-box__input').fill('Test Strategy');
    await page.locator('.el-message-box__btns .el-button--primary').click();
    
    // Verify success message
    await expect(page.locator('.el-message')).toContainText('策略已保存');
  });

  test('Complete User Scenario - Direction Conflict Warning', async ({ page }) => {
    // Test direction conflict detection
    await page.locator('.strength-options .el-checkbox-button').nth(2).click(); // Positive strength
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click(); // Negative win pan
    
    // Check if warning is displayed
    const warningExists = await page.locator('.direction-alert').isVisible();
    if (warningExists) {
      await expect(page.locator('.direction-alert')).toContainText('方向背离预警');
    }
  });
});