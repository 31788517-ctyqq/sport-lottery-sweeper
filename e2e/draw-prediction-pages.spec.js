const { test, expect } = require('@playwright/test')

const login = async (page) => {
  await page.goto('/login')

  if (!page.url().includes('/login')) {
    await page.waitForURL('**/admin/**', { timeout: 15000 })
    return
  }

  const doLogin = async () => {
    await page.fill('input[placeholder="请输入用户名"]', 'admin')
    await page.fill('input[placeholder="请输入密码"]', 'admin123')

    const captchaValue = await page.locator('canvas[aria-label="验证码图像"]').evaluate((el) => el.dataset?.captcha || '')
    await page.fill('input[placeholder="验证码"]', String(captchaValue).slice(0, 4))
    await page.click('button:has-text("登录")')
  }

  await doLogin()

  try {
    await page.waitForURL('**/admin/**', { timeout: 15000 })
  } catch (_) {
    await page.locator('div[aria-label="刷新验证码"], .captcha-image').first().click()
    await doLogin()
    await page.waitForURL('**/admin/**', { timeout: 15000 })
  }

  await expect(page).toHaveURL(/\/admin\//)
}

const openAndAssert = async (page, path, assertions) => {
  await page.goto(path)
  await page.waitForURL(`**${path}**`, { timeout: 15000 })
  await page.waitForLoadState('networkidle')
  await assertions()
}

test.describe('平局预测管理 - 5页面端到端冒烟', () => {
  test.beforeEach(async ({ page }) => {
    await login(page)
  })

  test('ai-draw 页面可用', async ({ page }) => {
    await openAndAssert(page, '/admin/draw-prediction/ai-draw', async () => {
      await expect(page.locator('.box-card .card-header span').first()).toContainText('北单平局预测扫盘')
      await expect(page.locator('button:has-text("手动抓取并计算")')).toBeVisible()
      await expect(page.locator('button:has-text("计算规则")')).toBeVisible()
      await expect(page.locator('button:has-text("查询")')).toBeVisible()
      await expect(page.locator('.el-table')).toBeVisible()
    })
  })

  test('poisson-11 页面可用', async ({ page }) => {
    await openAndAssert(page, '/admin/draw-prediction/poisson-11', async () => {
      await expect(page.locator('.box-card .card-header span').first()).toContainText('1-1比分预测扫盘')
      await expect(page.locator('button:has-text("手动抓取并计算")')).toBeVisible()
      await expect(page.locator('button:has-text("查询")')).toBeVisible()
      await expect(page.locator('th:has-text("1-1概率")')).toBeVisible()
      await expect(page.locator('.el-table')).toBeVisible()
    })
  })

  test('suggestion-center 页面可用', async ({ page }) => {
    await openAndAssert(page, '/admin/draw-prediction/suggestion-center', async () => {
      await expect(page.locator('.box-card .card-header span').first()).toContainText('下注建议中心')
      await expect(page.locator('button:has-text("采集快照")')).toBeVisible()
      await expect(page.locator('button:has-text("生成建议")')).toBeVisible()
      await expect(page.locator('button:has-text("执行结算")')).toBeVisible()
      await expect(page.locator('button:has-text("生成日报")')).toBeVisible()
      await expect(page.locator('th:has-text("决策路径")')).toBeVisible()
    })
  })

  test('killswitch 页面可用', async ({ page }) => {
    await openAndAssert(page, '/admin/draw-prediction/killswitch', async () => {
      await expect(page.locator('.box-card .card-header span').first()).toContainText('风控与熔断监控')
      await expect(page.locator('button:has-text("刷新")')).toBeVisible()
      await expect(page.locator('button:has-text("手动 STOP")')).toBeVisible()
      await expect(page.locator('button:has-text("手动 RELEASE")')).toBeVisible()
      await expect(page.locator('.reason-card').first()).toBeVisible()
    })
  })

  test('model-workbench 页面可用并同步tab参数', async ({ page }) => {
    await openAndAssert(page, '/admin/draw-prediction/model-workbench', async () => {
      await expect(page.locator('.box-card .card-header span').first()).toContainText('模型工坊')
      await expect(page.locator('.el-tabs__item:has-text("数据与特征")')).toBeVisible()
      await expect(page.locator('.el-tabs__item:has-text("模型训练与评估")')).toBeVisible()
      await expect(page.locator('.el-tabs__item:has-text("模型管理与部署")')).toBeVisible()
      await expect(page.locator('.el-tabs__item:has-text("预测服务与监控")')).toBeVisible()
      await expect(page).toHaveURL(/tab=data/)
    })
  })
})
