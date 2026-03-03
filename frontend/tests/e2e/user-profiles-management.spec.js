import { test, expect } from '@playwright/test'

async function setupUserProfilesMocks(page) {
  const state = {
    calls: { list: 0, detail: 0, update: 0 },
    profiles: [
      {
        userId: 1001,
        username: 'zhangsan',
        email: 'zhangsan@example.com',
        riskTolerance: 'moderate',
        preferredTeams: ['皇家马德里', '巴塞罗那', '曼城'],
        successRate: 0.65,
        bettingFrequency: 'high',
        bettingHabits: '赛前30分钟下注',
        totalBettingAmount: 12500,
        totalProfit: 2350,
        profitProbability: 0.58,
        tags: ['活跃用户'],
        lastUpdated: '2026-02-18 10:00:00'
      },
      {
        userId: 1002,
        username: 'lisi',
        email: 'lisi@example.com',
        riskTolerance: 'conservative',
        preferredTeams: ['尤文图斯'],
        successRate: 0.72,
        bettingFrequency: 'low',
        bettingHabits: '低频稳健',
        totalBettingAmount: 8200,
        totalProfit: 1450,
        profitProbability: 0.65,
        tags: ['保守型'],
        lastUpdated: '2026-02-18 09:00:00'
      }
    ]
  }

  await page.route('**/api/**', async (route) => {
    const req = route.request()
    const url = new URL(req.url())
    const path = url.pathname
    const method = req.method()

    if ((path.endsWith('/admin/user-profiles') || path.endsWith('/admin/user-profiles/')) && method === 'GET') {
      state.calls.list += 1
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'ok', data: state.profiles })
      })
    }

    if (/\/admin\/user-profiles\/\d+$/.test(path) && method === 'GET') {
      state.calls.detail += 1
      const id = Number(path.match(/(\d+)$/)?.[1])
      const profile = state.profiles.find((x) => x.userId === id) || null
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'ok', data: profile })
      })
    }

    if (/\/admin\/user-profiles\/\d+$/.test(path) && method === 'PUT') {
      state.calls.update += 1
      const id = Number(path.match(/(\d+)$/)?.[1])
      const payload = req.postDataJSON() || {}
      const idx = state.profiles.findIndex((x) => x.userId === id)
      if (idx !== -1) state.profiles[idx] = { ...state.profiles[idx], ...payload }
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ code: 200, message: 'updated', data: state.profiles[idx] })
      })
    }

    if (path.startsWith('/api/')) {
      return route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          success: true,
          message: 'mock default',
          data: {}
        })
      })
    }

    return route.continue()
  })

  return state
}

test.describe('User Profiles Page', () => {
  test('should load, filter, view detail, and submit edit', async ({ page }) => {
    const state = await setupUserProfilesMocks(page)
    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-token')
      localStorage.setItem('token', 'mock-token')
    })

    await page.goto('/admin/users/profiles')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.card-container')).toBeVisible()
    await expect(page.locator('.el-table')).toBeVisible()
    await expect(page.locator('.el-table__body tbody tr')).toHaveCount(2)
    expect(state.calls.list).toBeGreaterThan(0)

    await page.getByPlaceholder('搜索用户名或邮箱').fill('zhangsan')
    await page.getByRole('button', { name: '应用筛选' }).click()
    await expect(page.locator('.el-table__body tbody tr')).toHaveCount(1)

    await page.getByRole('button', { name: '查看' }).first().click()
    await expect(page.locator('.el-dialog')).toBeVisible()
    expect(state.calls.detail).toBeGreaterThan(0)
    await page.keyboard.press('Escape')

    await page.getByRole('button', { name: '编辑' }).first().click()
    await expect(page.locator('.el-dialog')).toBeVisible()
    await page.locator('.el-dialog textarea').first().fill('E2E修改后的投注习惯')
    await page.getByRole('button', { name: '确定' }).last().click()
    await page.waitForTimeout(300)
    expect(state.calls.update).toBe(1)
  })
})
