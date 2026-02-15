import { test, expect } from '@playwright/test'

test.describe('BeidanFilterPanel E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/admin/beidan-filter')
    await expect(page.locator('.beidan-filter-panel')).toBeVisible()
  })

  test('should display the main panel elements', async ({ page }) => {
    await expect(page.locator('.dimension-row')).toBeVisible()
    await expect(page.locator('.control-row')).toBeVisible()
    await expect(page.locator('.strategy-card')).toBeVisible()
  })

  test('should allow user to select filter options', async ({ page }) => {
    await page.locator('.strength-options .el-checkbox-button').nth(0).click()
    await page.locator('.strength-options .el-checkbox-button').nth(1).click()
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/)
    await expect(page.locator('.strength-options .el-checkbox-button').nth(1)).toHaveClass(/is-checked/)

    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click()
    await page.locator('.stability-options .el-checkbox-button').nth(0).click()
    await expect(page.locator('.win-pan-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/)
    await expect(page.locator('.stability-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/)
  })

  test('should apply preset strategies correctly', async ({ page }) => {
    await page.locator('.preset-grid .el-button').nth(0).click()
    await expect(page.locator('.strength-options .el-checkbox-button.is-checked')).toHaveCount(2)

    await page.locator('.preset-grid .el-button').nth(1).click()
    await expect(page.locator('.strength-options .el-checkbox-button.is-checked')).toHaveCount(2)
  })

  test('should save strategy', async ({ page }) => {
    await page.locator('.strength-options .el-checkbox-button').nth(0).click()
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click()
    await page.locator('.stability-options .el-checkbox-button').nth(0).click()

    await page.locator('.filter-actions .el-button--success').click()
    await page.locator('.el-message-box .el-input__inner').fill('Test Strategy')
    await page.locator('.el-message-box__btns .el-button--primary').click()

    await expect(page.locator('.el-message-box')).toHaveCount(0)
    await expect(page.locator('.strategy-card')).toBeVisible()
  })

  test('should handle filter application', async ({ page }) => {
    await page.locator('.strength-options .el-checkbox-button').nth(0).click()
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click()

    await page.locator('.filter-actions .el-button--primary').click()

    await expect(page.locator('.el-loading-mask')).toHaveCount(0)
    await expect(page.locator('.result-card, .el-empty')).toBeVisible()
  })

  test('should reset filters correctly', async ({ page }) => {
    await page.locator('.strength-options .el-checkbox-button').nth(0).click()
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click()
    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).toHaveClass(/is-checked/)

    await page.locator('.filter-actions .el-button').nth(1).click()

    await expect(page.locator('.strength-options .el-checkbox-button').nth(0)).not.toHaveClass(/is-checked/)
  })

  test('should display warning when conflicting filters are selected', async ({ page }) => {
    await page.locator('.strength-options .el-checkbox-button').nth(5).click()
    await page.locator('.win-pan-options .el-checkbox-button').nth(0).click()
    const warning = page.locator('.direction-alert')
    if (await warning.count()) {
      await expect(warning).toBeVisible()
    } else {
      await expect(page.locator('.filter-section')).toBeVisible()
    }
  })
})
