import { test, expect } from '@playwright/test'

test.describe('Intelligence Collection P2 Cache Behavior', () => {
  test('首次加载走接口、二次同分类命中缓存、强制刷新再次请求', async ({ page }) => {
    const requestCount = {
      all: 0,
      off_field: 0,
      prediction: 0
    }

    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'e2e-mock-token')
      localStorage.setItem('token', 'e2e-mock-token')
      localStorage.setItem('auth_token', 'e2e-mock-token')
    })

    await page.route('**/api/v1/admin/intelligence/collection/**', async (route) => {
      const req = route.request()
      const url = new URL(req.url())
      const path = url.pathname

      if (path.endsWith('/sources')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [{ code: '500w', name: '500w', url: 'https://trade.500.com/', item_count: 10 }],
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/time-window')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              before_hours: 240,
              after_hours: 12,
              strict_mode: true,
              bounds_label: '-240h ~ +12h',
              source: { before: 'db', after: 'db', strict: 'db' }
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/network')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              trust_env: false,
              source_timeout_seconds: { default: 1.2, '500w': 1.8 },
              max_retry: 2,
              retry_backoff_ms: 120,
              circuit_breaker_threshold: 6,
              circuit_breaker_seconds: 45
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/source-rules')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              rules: {
                ttyingqiu: {
                  blacklist_exact_paths: ['/news/-1', '/news/75'],
                  soft_penalty_paths: { '/news/3': 1.2, '/news/6009': 1.2 },
                  require_numeric_news_detail: true
                }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/quality-thresholds')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              thresholds: {
                min_title_len: 6,
                min_context_hits: 1,
                min_excerpt_len: { prediction: 80, off_field: 120, weibo: 40 },
                min_match_score_by_source: { '500w': 1.6, default: 1.8 }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/alias-dictionary')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { dictionary: { league: {}, team: {} }, source: 'db' },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/sources/health')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { days: 7, items: [] },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/time-window')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              before_hours: 240,
              after_hours: 12,
              strict_mode: true,
              bounds_label: '-240h ~ +12h',
              source: { before: 'db', after: 'db', strict: 'db' }
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/network')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              trust_env: false,
              source_timeout_seconds: { default: 1.2, '500w': 1.8 },
              max_retry: 2,
              retry_backoff_ms: 120,
              circuit_breaker_threshold: 6,
              circuit_breaker_seconds: 45
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/source-rules')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              rules: {
                ttyingqiu: {
                  blacklist_exact_paths: ['/news/-1', '/news/75'],
                  soft_penalty_paths: { '/news/3': 1.2, '/news/6009': 1.2 },
                  require_numeric_news_detail: true
                }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/quality-thresholds')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              thresholds: {
                min_title_len: 6,
                min_context_hits: 1,
                min_excerpt_len: { prediction: 80, off_field: 120, weibo: 40 },
                min_match_score_by_source: { '500w': 1.6, default: 1.8 }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/alias-dictionary')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { dictionary: { league: {}, team: {} }, source: 'db' },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/sources/health')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { days: 7, items: [] },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/matches')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              items: [
                {
                  id: 207,
                  league_name: '亚冠',
                  home_team: '广岛三箭',
                  away_team: '柔佛',
                  kickoff_time: '2026-02-10T18:00:00',
                  status: 'scheduled',
                  schedule_date: '2026-02-10'
                }
              ],
              total: 1,
              page: 1,
              size: 100
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { items: [], total: 0, page: 1, size: 100 },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/channels/dingtalk/bindings')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: [], message: 'ok' })
        })
      }

      if (path.includes('/matches/') && path.endsWith('/items')) {
        const category = url.searchParams.get('category') || ''
        if (category === 'off_field') requestCount.off_field += 1
        else if (category === 'prediction') requestCount.prediction += 1
        else requestCount.all += 1

        const item = {
          id: 9001,
          task_id: 1,
          match_id: 207,
          source_code: '500w',
          intel_category: category || 'prediction',
          intel_type: 'win_draw_lose',
          title: `测试标题-${category || 'all'}`,
          content_raw: `[match-article] article_title=测试标题-${category || 'all'}; article_url=https://example.com/a; match_score=0.92; summary=测试摘要`,
          source_url: 'https://example.com/a',
          published_at: '2026-02-10T10:00:00',
          crawled_at: '2026-02-10T10:01:00',
          confidence: 0.88
        }

        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { match_id: 207, items: [item], total: 1 },
            message: 'ok'
          })
        })
      }

      return route.fallback()
    })

    await page.goto('/admin/intelligence/collection', { waitUntil: 'domcontentloaded' })

    await expect(page.getByText('情报采集管理（降本可落地版）')).toBeVisible()
    await expect(page.locator('.el-table__body-wrapper tbody tr')).toHaveCount(1)

    await page.locator('.el-table__body-wrapper tbody tr').first().click()
    await expect.poll(() => requestCount.all).toBe(1)

    const offFieldBtn = page.getByRole('button', { name: '场外信息' })
    await offFieldBtn.click()
    await expect.poll(() => requestCount.off_field).toBe(1)

    await offFieldBtn.click()
    await page.waitForTimeout(500)
    expect(requestCount.off_field).toBe(1)

    await page.getByRole('button', { name: '刷新结果' }).click()
    await expect.poll(() => requestCount.off_field).toBe(2)
  })

  test('任务成功后自动失效缓存并重新请求', async ({ page }) => {
    const requestCount = {
      all: 0,
      taskDetail: 0
    }

    await page.addInitScript(() => {
      localStorage.setItem('access_token', 'e2e-mock-token')
      localStorage.setItem('token', 'e2e-mock-token')
      localStorage.setItem('auth_token', 'e2e-mock-token')
    })

    await page.route('**/api/v1/admin/intelligence/collection/**', async (route) => {
      const req = route.request()
      const url = new URL(req.url())
      const path = url.pathname
      const method = req.method()

      if (path.endsWith('/sources')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [{ code: '500w', name: '500w', url: 'https://trade.500.com/', item_count: 10 }],
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/time-window')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              before_hours: 240,
              after_hours: 12,
              strict_mode: true,
              bounds_label: '-240h ~ +12h',
              source: { before: 'db', after: 'db', strict: 'db' }
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/network')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              trust_env: false,
              source_timeout_seconds: { default: 1.2, '500w': 1.8 },
              max_retry: 2,
              retry_backoff_ms: 120,
              circuit_breaker_threshold: 6,
              circuit_breaker_seconds: 45
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/source-rules')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              rules: {
                ttyingqiu: {
                  blacklist_exact_paths: ['/news/-1', '/news/75'],
                  soft_penalty_paths: { '/news/3': 1.2, '/news/6009': 1.2 },
                  require_numeric_news_detail: true
                }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/quality-thresholds')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              thresholds: {
                min_title_len: 6,
                min_context_hits: 1,
                min_excerpt_len: { prediction: 80, off_field: 120, weibo: 40 },
                min_match_score_by_source: { '500w': 1.6, default: 1.8 }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/alias-dictionary')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { dictionary: { league: {}, team: {} }, source: 'db' },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/sources/health')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { days: 7, items: [] },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/matches')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              items: [
                {
                  id: 207,
                  league_name: '亚冠',
                  home_team: '广岛三箭',
                  away_team: '柔佛',
                  kickoff_time: '2026-02-10T18:00:00',
                  status: 'scheduled',
                  schedule_date: '2026-02-10'
                }
              ],
              total: 1,
              page: 1,
              size: 100
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              items: [
                {
                  id: 1001,
                  task_uuid: 'task-1001',
                  mode: 'immediate',
                  status: 'success',
                  match_ids: [207],
                  sources: ['500w'],
                  intel_types: ['win_draw_lose'],
                  total_count: 1,
                  success_count: 1,
                  failed_count: 0,
                  created_at: '2026-02-10T10:00:00'
                }
              ],
              total: 1,
              page: 1,
              size: 100
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/channels/dingtalk/bindings')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: [], message: 'ok' })
        })
      }

      if (path.endsWith('/tasks/1001') && method === 'GET') {
        requestCount.taskDetail += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 1001,
              task_uuid: 'task-1001',
              mode: 'immediate',
              status: 'success',
              match_ids: [207],
              sources: ['500w'],
              intel_types: ['win_draw_lose'],
              total_count: 1,
              success_count: 1,
              failed_count: 0
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks/1001/retry') && method === 'POST') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 1001,
              status: 'running',
              match_ids: [207]
            },
            message: 'retry accepted'
          })
        })
      }

      if (path.includes('/matches/') && path.endsWith('/items')) {
        requestCount.all += 1
        const item = {
          id: 9010 + requestCount.all,
          task_id: 1001,
          match_id: 207,
          source_code: '500w',
          intel_category: 'prediction',
          intel_type: 'win_draw_lose',
          title: `缓存失效验证-${requestCount.all}`,
          content_raw: `[match-article] article_title=缓存失效验证-${requestCount.all}; article_url=https://example.com/a; match_score=0.95; summary=测试摘要`,
          source_url: 'https://example.com/a',
          published_at: '2026-02-10T10:00:00',
          crawled_at: '2026-02-10T10:01:00',
          confidence: 0.9
        }
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { match_id: 207, items: [item], total: 1 },
            message: 'ok'
          })
        })
      }

      return route.fallback()
    })

    await page.goto('/admin/intelligence/collection', { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('情报采集管理（降本可落地版）')).toBeVisible()

    await page.locator('.el-table__body-wrapper tbody tr').first().click()
    await expect.poll(() => requestCount.all).toBe(1)

    await page.getByRole('button', { name: '全部' }).click()
    await page.waitForTimeout(400)
    expect(requestCount.all).toBe(1)

    await page.getByRole('button', { name: '重试' }).first().click()

    // Retry success should clear cache and force reload items again.
    // Current UI flow may request once or multiple times depending on tracker + callback timing.
    await expect.poll(() => requestCount.all).toBeGreaterThan(1)
    expect(requestCount.taskDetail).toBeGreaterThan(0)
  })
})
