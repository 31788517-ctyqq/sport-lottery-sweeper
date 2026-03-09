import { test, expect } from '@playwright/test'

test.describe('Intelligence Collection Advanced Settings & Replay', () => {
  test('save advanced settings and run replay debug', async ({ page }) => {
    const calls = {
      putNetwork: 0,
      putRules: 0,
      putQuality: 0,
      putAlias: 0,
      replay: 0
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

      if (path.endsWith('/sources') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: [
              { code: '500w', name: '500w', url: 'https://trade.500.com/', item_count: 12 },
              { code: 'ttyingqiu', name: 'ttyingqiu', url: 'https://www.ttyingqiu.com/', item_count: 8 }
            ],
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/time-window') && method === 'GET') {
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

      if (path.endsWith('/settings/time-window') && method === 'PUT') {
        const body = req.postDataJSON()
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              before_hours: body.before_hours,
              after_hours: body.after_hours,
              strict_mode: body.strict_mode,
              bounds_label: `-${body.before_hours}h ~ +${body.after_hours}h`,
              source: { before: 'db', after: 'db', strict: 'db' }
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/network') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              trust_env: false,
              source_timeout_seconds: {
                default: 1.2,
                '500w': 1.8,
                ttyingqiu: 2.2,
                tencent: 1.8,
                weibo: 1.8,
                sina: 1.8
              },
              max_retry: 2,
              retry_backoff_ms: 120,
              circuit_breaker_threshold: 6,
              circuit_breaker_seconds: 45
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/network') && method === 'PUT') {
        calls.putNetwork += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: req.postDataJSON(), message: 'ok' })
        })
      }

      if (path.endsWith('/settings/source-rules') && method === 'GET') {
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

      if (path.endsWith('/settings/source-rules') && method === 'PUT') {
        calls.putRules += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: req.postDataJSON(), message: 'ok' })
        })
      }

      if (path.endsWith('/settings/quality-thresholds') && method === 'GET') {
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
                min_match_score_by_source: { '500w': 1.6, ttyingqiu: 1.8, default: 1.8 }
              },
              source: 'db'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/settings/quality-thresholds') && method === 'PUT') {
        calls.putQuality += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: req.postDataJSON(), message: 'ok' })
        })
      }

      if (path.endsWith('/settings/alias-dictionary') && method === 'GET') {
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

      if (path.endsWith('/settings/alias-dictionary') && method === 'PUT') {
        calls.putAlias += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: req.postDataJSON(), message: 'ok' })
        })
      }

      if (path.endsWith('/sources/health') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              days: 7,
              items: [{ source: '500w', total_items: 12, accepted_rate: 0.66, blocked_rate: 0.2, avg_quality_score: 1.9, avg_confidence: 0.78 }]
            },
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
          body: JSON.stringify({ success: true, data: { items: [], total: 0, page: 1, size: 20 }, message: 'ok' })
        })
      }

      if (path.endsWith('/channels/dingtalk/bindings')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({ success: true, data: [], message: 'ok' })
        })
      }

      if (path.includes('/matches/') && path.endsWith('/items') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              match_id: 207,
              total: 1,
              items: [
                {
                  id: 9101,
                  task_id: 1,
                  match_id: 207,
                  source_code: '500w',
                  intel_category: 'prediction',
                  intel_type: 'win_draw_lose',
                  title: '测试文章',
                  content_raw: '[match-article] article_title=测试文章; article_url=https://example.com/a; match_score=2.2; summary=摘要; is_article_page=1;',
                  source_url: 'https://example.com/a',
                  confidence: 0.9
                }
              ]
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/debug/replay') && method === 'POST') {
        calls.replay += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              mode: 'replay',
              request: req.postDataJSON(),
              result: {
                match_id: 207,
                source: '500w',
                candidate_count: 3,
                evaluated_count: 3,
                top_candidates: [
                  {
                    url: 'https://example.com/a',
                    status_code: 200,
                    title: '测试候选',
                    score: 2.4,
                    hit_terms: ['广岛三箭'],
                    time_window_pass: true,
                    publish_time: '2026-02-10 09:00:00'
                  }
                ]
              }
            },
            message: 'ok'
          })
        })
      }

      return route.fallback()
    })

    await page.goto('/admin/intelligence/collection', { waitUntil: 'domcontentloaded' })
    await expect(page.locator('.collection-page')).toBeVisible()
    await expect(page.locator('.el-table__body-wrapper tbody tr')).toHaveCount(1)

    await page.getByRole('button', { name: '采集参数' }).click()
    const settingsDialog = page.getByRole('dialog', { name: '采集参数设置' })
    await expect(settingsDialog).toBeVisible()
    await expect(settingsDialog.locator('.el-tabs__item')).toHaveCount(5)

    await settingsDialog.getByRole('button', { name: '保存全部' }).click()
    await expect.poll(() => calls.putNetwork).toBe(1)
    await expect.poll(() => calls.putRules).toBe(1)
    await expect.poll(() => calls.putQuality).toBe(1)
    await expect.poll(() => calls.putAlias).toBe(1)

    await settingsDialog.getByRole('button', { name: '关闭' }).click()
    await page.locator('.el-table__body-wrapper tbody tr').first().click()

    await page.getByRole('button', { name: '回放调试' }).click()
    await expect.poll(() => calls.replay).toBe(1)
    await expect(page.getByRole('dialog', { name: '候选抓取调试结果' }).locator('.el-table')).toBeVisible()
    await expect(page.getByText('https://example.com/a')).toBeVisible()
  })
})
