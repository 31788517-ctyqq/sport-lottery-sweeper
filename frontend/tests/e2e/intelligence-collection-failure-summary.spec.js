import { test, expect } from '@playwright/test'

test.describe('Intelligence Collection Failure Summary', () => {
  test('任务详情展示失败摘要并支持手动刷新', async ({ page }) => {
    const calls = {
      failureSummary: 0
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
            data: [{ code: '500w', name: '500w', url: 'https://trade.500.com/', item_count: 9 }],
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
              source_timeout_seconds: { default: 1.5, '500w': 1.8 },
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
            data: { rules: {}, source: 'db' },
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
          body: JSON.stringify({ success: true, data: { days: 7, items: [] }, message: 'ok' })
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

      if (path.includes('/matches/') && path.endsWith('/items')) {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: { match_id: 207, items: [], total: 0 },
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
                  id: 8801,
                  task_uuid: 'task-8801',
                  mode: 'immediate',
                  status: 'failed',
                  total_count: 6,
                  success_count: 1,
                  failed_count: 5,
                  success_rate: 0.1667,
                  matched_matches: 1,
                  total_matches: 3,
                  coverage_rate: 0.3333,
                  sources: ['500w'],
                  intel_types: ['injury'],
                  match_ids: [207],
                  created_at: '2026-02-20T10:00:00'
                }
              ],
              total: 1,
              page: 1,
              size: 20
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks/8801') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              id: 8801,
              task_uuid: 'task-8801',
              mode: 'immediate',
              status: 'failed',
              total_count: 6,
              success_count: 1,
              failed_count: 5,
              success_rate: 0.1667,
              matched_matches: 1,
              total_matches: 3,
              coverage_rate: 0.3333,
              sources: ['500w'],
              intel_types: ['injury'],
              match_ids: [207],
              error_message: 'timeout',
              created_at: '2026-02-20T10:00:00',
              updated_at: '2026-02-20T10:01:30'
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks/8801/subtasks') && method === 'GET') {
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              task_id: 8801,
              total: 1,
              items: [
                {
                  id: 501,
                  task_id: 8801,
                  match_id: 207,
                  status: 'failed',
                  expected_count: 6,
                  item_count: 1,
                  success_count: 1,
                  failed_count: 5,
                  candidate_count: 6,
                  parsed_count: 6,
                  matched_count: 1,
                  accepted_count: 1,
                  blocked_count: 5
                }
              ]
            },
            message: 'ok'
          })
        })
      }

      if (path.endsWith('/tasks/8801/failure-summary') && method === 'GET') {
        calls.failureSummary += 1
        return route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            data: {
              task_id: 8801,
              task_status: 'failed',
              top_reasons: [
                { reason: 'timeout', count: 3 },
                { reason: 'parser-empty', count: 2 }
              ],
              source_failures: [
                {
                  source: '500w',
                  timeout: 2,
                  errors: 1,
                  retries: 2,
                  circuit_skipped: 1,
                  blocked_decisions: 3,
                  severity_score: 7
                }
              ],
              sample_logs: [
                {
                  time: '2026-02-20 10:00:01',
                  level: 'error',
                  message: 'collect failed: timeout'
                }
              ]
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

      return route.fallback()
    })

    await page.goto('/admin/intelligence/collection', { waitUntil: 'domcontentloaded' })
    const taskCard = page.locator('.block').filter({ hasText: '采集任务' }).first()
    await expect(taskCard.locator('.el-table__body-wrapper tbody tr')).toHaveCount(1)

    await page.getByRole('button', { name: '详情' }).first().click()
    const detailDialog = page.getByRole('dialog', { name: '任务详情' })
    await expect(detailDialog).toBeVisible()
    await expect(detailDialog.getByText('失败摘要')).toBeVisible()
    await expect(detailDialog.getByText('Top 原因')).toBeVisible()
    await expect(detailDialog.getByText('timeout x3')).toBeVisible()
    await expect(detailDialog.getByRole('cell', { name: '500w' }).first()).toBeVisible()
    await expect.poll(() => calls.failureSummary).toBe(1)

    await detailDialog.getByRole('button', { name: '刷新' }).click()
    await expect.poll(() => calls.failureSummary).toBe(2)
  })
})
