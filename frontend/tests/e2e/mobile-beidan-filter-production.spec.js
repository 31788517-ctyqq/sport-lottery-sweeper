import { test, expect } from '@playwright/test'

test.describe('Mobile Beidan Filter - Production Readiness', () => {
  test('full flow: strategy -> filter -> results -> analysis -> output', async ({ page }) => {
    const strategyStore = [
      {
        id: 1,
        name: '稳健策略A',
        description: '测试策略A',
        threeDimensional: {},
        otherConditions: {
          leagues: ['英超'],
          dateTime: '26023',
          powerDiffs: ['1', '2'],
          winPanDiffs: ['1'],
          stabilityTiers: ['S']
        },
        sort: { field: 'p_level', order: 'desc' },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      }
    ]

    page.on('dialog', async (dialog) => dialog.accept())

    await page.route('**/api/v1/beidan-filter/latest-date-times', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ dateTimes: ['26023', '26022'] })
      })
    })

    await page.route('**/api/v1/beidan-filter/strategies', async (route, request) => {
      if (request.method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ strategies: strategyStore })
        })
        return
      }

      if (request.method() === 'POST') {
        const payload = request.postDataJSON()
        const existed = strategyStore.find((s) => s.name === payload.name)
        if (!existed) {
          strategyStore.push({
            ...payload,
            id: strategyStore.length + 1,
            createdAt: payload.createdAt || new Date().toISOString(),
            updatedAt: payload.updatedAt || new Date().toISOString()
          })
        }
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(payload)
        })
      }
    })

    await page.route('**/api/v1/beidan-filter/strategies/*', async (route, request) => {
      if (request.method() === 'DELETE') {
        const id = Number(request.url().split('/').pop())
        const idx = strategyStore.findIndex((s) => s.id === id)
        if (idx >= 0) strategyStore.splice(idx, 1)
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'ok' })
        })
      }
    })

    await page.route('**/api/v1/beidan-filter/real-time-count**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ matchCount: 12 })
      })
    })

    await page.route('**/api/v1/beidan-filter/advanced-filter', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          matches: [
            {
              id: 'm1',
              dateTime: '26023',
              matchTime: '2026-02-17 19:35',
              league: '英超',
              homeTeam: '阿森纳',
              guestTeam: '切尔西',
              strength: 2,
              winLevel: 1,
              pLevel: 2,
              stability: 'S',
              source_attrs: {
                lineId: '10001',
                home_feature: '61%',
                away_feature: '44%',
                homeSpf: '近10场6胜2平2负',
                guestSpf: '近10场4胜3平3负',
                jiaoFenDesc: '近6次交锋主队略占优',
                jiaoFenMatch1: '2025-12-01 阿森纳 2:1 切尔西'
              }
            }
          ],
          statistics: {
            filteredMatches: 1,
            delta_p_count: 1,
            delta_wp_count: 1,
            p_tier_count: 1
          },
          pagination: {
            totalItems: 1
          }
        })
      })
    })

    await page.route('**/api/multi-strategy/config**', async (route, request) => {
      if (request.method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: { id: 1 } })
        })
        return
      }
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: [{ id: 1, task_name: '北单多策略筛选任务' }] })
      })
    })

    await page.route('**/api/multi-strategy/execute', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ success: true, data: { executed: true } })
      })
    })

    await page.goto('/m/beidan-filter')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.mobile-beidan-page')).toBeVisible()
    await expect(page.locator('button.nav-btn:has-text("策略")')).toBeVisible()
    await expect(page.locator('button.nav-btn:has-text("筛选")')).toBeVisible()
    await expect(page.locator('button.nav-btn:has-text("结果")')).toBeVisible()
    await expect(page.locator('button.nav-btn:has-text("输出")')).toBeVisible()

    // 策略：设置并保存
    await page.locator('button.chip:has-text("+1")').first().click()
    await page.locator('button.chip:has-text("P1")').first().click()
    await page.locator('button.secondary-btn:has-text("保存策略")').click()
    await page.keyboard.type('上线前策略')
    await page.keyboard.press('Enter')

    // 筛选：选择策略并触发
    await page.locator('button.nav-btn:has-text("筛选")').click()
    await page.locator('.chips.strategy-tags button:has-text("稳健策略A")').click()
    await page.locator('button.primary-btn:has-text("筛选结果场次")').click()

    // 结果：验证统计、列表、分析弹窗
    await expect(page.locator('button.nav-btn.active:has-text("结果")')).toBeVisible()
    await expect(page.locator('.stats-grid .stat-box')).toHaveCount(4)
    await expect(page.locator('.result-card')).toHaveCount(1)
    await page.locator('.result-card').first().click()
    await expect(page.locator('.mobile-analysis-dialog')).toBeVisible()
    await expect(page.locator('text=比赛基本信息')).toBeVisible()
    await page.keyboard.press('Escape')

    // 输出：验证多策略配置与执行
    await page.locator('button.nav-btn:has-text("输出")').click()
    await expect(page.locator('text=定时与推送配置')).toBeVisible()
    await page.locator('.chips.strategy-tags button:has-text("稳健策略A")').click()
    await page.locator('input[placeholder="例如：北单每日多策略筛选"]').fill('移动端发布前任务')
    await page.locator('label.multi-check:has-text("启用钉钉推送") input').first().setChecked(true)
    await page.locator('textarea[placeholder="请输入钉钉机器人 Webhook URL"]').fill('https://oapi.dingtalk.com/robot/send?access_token=mock')
    await page.locator('button.primary-btn:has-text("保存定时配置")').click()
    await page.locator('button.secondary-btn:has-text("立即执行并推送")').click()
  })
})
