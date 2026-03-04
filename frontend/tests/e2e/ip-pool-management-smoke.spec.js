import { test, expect } from '@playwright/test'

function createInitialState() {
  const now = new Date().toISOString()
  const ipPools = [
    {
      id: 1,
      ipAddress: '1.1.1.1',
      port: 8080,
      protocol: 'http',
      location: 'CN',
      responseTime: 120,
      successRate: 96,
      lastChecked: now,
      source: 'https://proxy-source-a.test/list',
      anonymity: '高匿',
      score: 95,
      failReason: '',
      status: 'available',
      usageCount: 12,
      lastUsed: now,
      isEnabled: true
    },
    {
      id: 2,
      ipAddress: '2.2.2.2',
      port: 3128,
      protocol: 'http',
      location: 'US',
      responseTime: 210,
      successRate: 88,
      lastChecked: now,
      source: 'https://proxy-source-b.test/list',
      anonymity: '匿名',
      score: 84,
      failReason: '',
      status: 'available',
      usageCount: 7,
      lastUsed: now,
      isEnabled: true
    }
  ]

  const sourceAddresses = [
    { source: 'https://proxy-source-a.test/list', enabled: true },
    { source: 'https://proxy-source-b.test/list', enabled: true }
  ]

  return { ipPools, sourceAddresses, now, ipSeed: 10 }
}

function buildSourceItems(state) {
  return state.sourceAddresses.map((cfg) => {
    const list = state.ipPools.filter((x) => x.source === cfg.source)
    return {
      source: cfg.source,
      enabled: cfg.enabled,
      count: list.length,
      activeCount: list.filter((x) => x.status === 'available').length,
      lastChecked: list[0]?.lastChecked || null
    }
  })
}

test.describe('IP池页面冒烟回归', () => {
  test('自动爬取 + 地址编辑 + 数量展示', async ({ page }) => {
    const state = createInitialState()

    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'mock-access-token')
      localStorage.setItem('token', 'mock-access-token')
      localStorage.setItem('refresh_token', 'mock-refresh-token')
    })

    await page.route('**/api/users/me', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          code: 200,
          data: {
            id: 1,
            username: 'admin',
            roles: ['admin']
          }
        })
      })
    })

    await page.route('**/api/admin/ip-pools**', async (route) => {
      const req = route.request()
      const method = req.method()
      const url = new URL(req.url())
      const path = url.pathname

      if (path.endsWith('/source-addresses')) {
        if (method === 'GET') {
          const items = buildSourceItems(state)
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: {
                items,
                total: items.length,
                enabled: items.filter((x) => x.enabled).length
              },
              message: '获取地址列表获取成功'
            })
          })
          return
        }
        if (method === 'PUT') {
          const payload = req.postDataJSON()
          const oldSource = payload.old_source
          const newSource = payload.new_source
          const enabled = !!payload.enabled
          const apply = !!payload.apply_to_existing_ips

          const target = state.sourceAddresses.find((x) => x.source === oldSource)
          if (target) {
            target.source = newSource
            target.enabled = enabled
          } else {
            state.sourceAddresses.push({ source: newSource, enabled })
          }
          if (apply && oldSource !== newSource) {
            state.ipPools.forEach((x) => {
              if (x.source === oldSource) x.source = newSource
            })
          }

          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify({
              code: 200,
              data: { oldSource, newSource, enabled },
              message: '获取地址更新成功'
            })
          })
          return
        }
      }

      if (path.endsWith('/recrawl') && method === 'POST') {
        const now = new Date().toISOString()
        const enabledSources = state.sourceAddresses.filter((x) => x.enabled)
        enabledSources.forEach((sourceCfg) => {
          state.ipSeed += 1
          state.ipPools.push({
            id: state.ipPools.length + 1,
            ipAddress: `10.0.0.${state.ipSeed}`,
            port: 8000 + state.ipSeed,
            protocol: 'http',
            location: 'AUTO',
            responseTime: 0,
            successRate: 0,
            lastChecked: now,
            source: sourceCfg.source,
            anonymity: '',
            score: 0,
            failReason: '',
            status: 'available',
            usageCount: 0,
            lastUsed: '-',
            isEnabled: true
          })
        })

        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            data: {
              summary: {
                sourceCount: enabledSources.length,
                newCount: enabledSources.length,
                updatedCount: 0
              },
              results: enabledSources.map((x) => ({
                source: x.source,
                enabled: true,
                fetched: 1,
                new: 1,
                updated: 0,
                error: ''
              }))
            },
            message: '自动爬取完成'
          })
        })
        return
      }

      if (path.endsWith('/ip-pools') && method === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            code: 200,
            data: {
              items: state.ipPools,
              total: state.ipPools.length,
              page: 1,
              size: 10,
              pages: 1
            },
            message: 'IP池获取成功'
          })
        })
        return
      }

      await route.continue()
    })

    await page.goto('/admin/data-source/ip-pool')
    await expect(page.locator('h3')).toContainText('IP池管理')

    await expect(page.getByRole('button', { name: '自动爬取' })).toBeVisible()
    await expect(page.getByRole('button', { name: '获取地址编辑' })).toBeVisible()

    await page.getByRole('button', { name: '获取地址编辑' }).click()
    await expect(page.locator('.el-dialog__title')).toContainText('获取地址管理')
    const sourceDialog = page.locator('.el-dialog').filter({ hasText: '获取地址管理' })
    const sourceRowA = sourceDialog.locator('tr', { hasText: 'https://proxy-source-a.test/list' })
    await expect(sourceRowA).toContainText('1')

    await sourceRowA.getByRole('button', { name: '编辑' }).click()
    await expect(page.getByRole('heading', { name: '编辑获取地址' })).toBeVisible()
    await page.locator('input[placeholder="https://..."]').fill('https://proxy-source-a-new.test/list')
    await page.getByRole('button', { name: '保存' }).click()

    await expect(sourceDialog.locator('tr', { hasText: 'https://proxy-source-a-new.test/list' })).toBeVisible()

    await page.getByRole('button', { name: '关闭' }).click()
    await page.getByRole('button', { name: '自动爬取' }).click()
    await expect(page.locator('.el-message').filter({ hasText: '自动爬取完成' }).first()).toBeVisible()

    await page.getByRole('button', { name: '获取地址编辑' }).click()
    const sourceDialogAfter = page.locator('.el-dialog').filter({ hasText: '获取地址管理' })
    await expect(sourceDialogAfter.locator('tr', { hasText: 'https://proxy-source-a-new.test/list' })).toContainText('2')
    await expect(sourceDialogAfter.locator('tr', { hasText: 'https://proxy-source-b.test/list' })).toContainText('2')

    await expect(sourceDialogAfter.locator('tr', { hasText: 'https://proxy-source-a-new.test/list' })).toBeVisible()
    await page.getByRole('button', { name: '关闭' }).click()
    const mainTable = page.locator('.card-container .el-table').first()
    await expect(mainTable).toContainText('https://proxy-source-a-new.test/list')
  })
})
