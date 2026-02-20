import { test, expect } from '@playwright/test'

test.describe('Intelligence Collection Quality Fields', () => {
  test('结果列表与详情区展示质量字段', async ({ page }) => {
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
            data: [{ code: 'ttyingqiu', name: 'ttyingqiu', url: 'https://www.ttyingqiu.com/', item_count: 2 }],
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
              source_timeout_seconds: { default: 1.2, ttyingqiu: 2.2 },
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
                min_match_score_by_source: { ttyingqiu: 1.8, default: 1.8 }
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
            data: { days: 7, items: [{ source: 'ttyingqiu', total_items: 2 }] },
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
              items: [],
              total: 0,
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

      if (path.includes('/matches/') && path.endsWith('/items')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              match_id: 207,
              total: 2,
              items: [
                {
                  id: 9101,
                  task_id: 2001,
                  match_id: 207,
                  source_code: 'ttyingqiu',
                  intel_category: 'prediction',
                  intel_type: 'win_draw_lose',
                  title: '文章命中样例',
                  content_raw: '[match-article] source=ttyingqiu; source_parser=ttyingqiu-news-detail; match_score=3.2; quality_score=3.2; quality_pass_reason=dedicated parser hit teams; hit_terms=广岛三箭|柔佛; summary=样例摘要; is_article_page=1;',
                  source_url: 'https://www.ttyingqiu.com/news/12345',
                  published_at: '2026-02-10T10:00:00',
                  crawled_at: '2026-02-10T10:01:00',
                  confidence: 0.91,
                  quality_score: 3.2,
                  quality_pass_reason: 'dedicated parser hit teams',
                  quality_block_reason: '',
                  source_parser: 'ttyingqiu-news-detail',
                  match_hit_terms: ['广岛三箭', '柔佛'],
                  is_article_page: true,
                  quality_status: 'accepted'
                },
                {
                  id: 9102,
                  task_id: 2001,
                  match_id: 207,
                  source_code: 'ttyingqiu',
                  intel_category: 'off_field',
                  intel_type: 'injury',
                  title: '兜底样例',
                  content_raw: '[match-article-fallback] source=ttyingqiu; source_parser=ttyingqiu-dedicated; quality_score=0; quality_block_reason=no candidate article links; summary=兜底摘要; is_article_page=0;',
                  source_url: 'https://www.ttyingqiu.com/news/home',
                  published_at: '2026-02-10T10:00:00',
                  crawled_at: '2026-02-10T10:01:00',
                  confidence: 0.44,
                  quality_score: 0,
                  quality_pass_reason: '',
                  quality_block_reason: 'no candidate article links',
                  source_parser: 'ttyingqiu-dedicated',
                  match_hit_terms: [],
                  is_article_page: false,
                  quality_status: 'blocked'
                }
              ]
            },
            message: 'ok'
          })
        })
      }

      return route.fallback()
    })

    await page.goto('/admin/intelligence/collection', { waitUntil: 'domcontentloaded' })
    await expect(page.getByText('情报采集管理（降本可落地版）')).toBeVisible()

    await page.locator('.el-table__body-wrapper tbody tr').first().click()

    await expect(page.getByText('高质量 1')).toBeVisible()
    await expect(page.getByText('dedicated parser hit teams').first()).toBeVisible()
    await expect(page.getByText('ttyingqiu-news-detail').first()).toBeVisible()
    await expect(page.getByText('广岛三箭 / 柔佛').first()).toBeVisible()

    await page.getByText('兜底样例').click()
    await expect(page.getByText('no candidate article links').first()).toBeVisible()
  })
})
