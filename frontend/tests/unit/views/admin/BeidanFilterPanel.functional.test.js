import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import BeidanFilterPanel from '../../../../src/views/admin/BeidanFilterPanel.vue'
import { ElMessageBox } from 'element-plus'

vi.mock('@/utils/request', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    delete: vi.fn()
  }
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: vi.fn(),
      error: vi.fn(),
      warning: vi.fn(),
      info: vi.fn()
    },
    ElMessageBox: {
      prompt: vi.fn(),
      confirm: vi.fn()
    }
  }
})

describe('BeidanFilterPanel.vue (functional)', () => {
  let wrapper
  let request

  beforeEach(async () => {
    vi.clearAllMocks()
    request = (await import('@/utils/request')).default

    request.get.mockImplementation((url) => {
      if (url.includes('/latest-date-times')) return Promise.resolve({ dateTimes: ['26024', '26023'] })
      if (url.includes('/strategies')) return Promise.resolve({ strategies: [] })
      if (url.includes('/real-time-count')) return Promise.resolve({ matchCount: 10 })
      return Promise.resolve({})
    })

    request.post.mockImplementation((url) => {
      if (url.includes('/advanced-filter')) {
        return Promise.resolve({
          matches: [
            {
              id: 1,
              dateTime: '26024',
              lineId: 101,
              matchTime: '2026-01-01 12:00:00',
              league: '英超',
              homeTeam: '主队',
              guestTeam: '客队',
              strength: 2,
              winLevel: 3,
              pLevel: 2,
              stability: 'A'
            }
          ],
          statistics: { totalMatches: 1 },
          pagination: { totalItems: 1 }
        })
      }
      if (url.includes('/strategies')) return Promise.resolve({ id: 99, name: '我的策略' })
      return Promise.resolve({ success: true })
    })

    request.delete.mockResolvedValue({ success: true })

    wrapper = shallowMount(BeidanFilterPanel, {
      global: {
        plugins: [createTestingPinia({ createSpy: vi.fn })]
      }
    })
    await flushPromises()
  })

  it('runs core workflow: preset -> filter -> results shown', async () => {
    await wrapper.vm.applyPreset('strong')

    expect(wrapper.vm.strategySelected).toBe(true)
    expect(wrapper.vm.hasResults).toBe(true)
    expect(wrapper.vm.totalResults).toBe(1)
    expect(wrapper.vm.pagedResults[0].home_team).toBe('主队')
  })

  it('opens analysis dialog from result row', async () => {
    await wrapper.vm.applyPreset('strong')

    wrapper.vm.handleOpenAnalysis(wrapper.vm.pagedResults[0])

    expect(wrapper.vm.analysisVisible).toBe(true)
    expect(wrapper.vm.currentAnalysisData).toBeTruthy()
    expect(wrapper.vm.currentAnalysisData.homeTeam).toBe('主队')
  })

  it('saves strategy via API', async () => {
    ElMessageBox.prompt.mockResolvedValue({ value: '我的策略' })

    wrapper.vm.filterForm.powerDiffs = [2]
    wrapper.vm.filterForm.winPanDiffs = [3]
    wrapper.vm.filterForm.stabilityTiers = ['A']

    await wrapper.vm.onSaveStrategy()

    expect(request.post).toHaveBeenCalledWith('/api/v1/beidan-filter/strategies', expect.any(Object))
    expect(wrapper.vm.strategyOptions).toContain('我的策略')
  })

  it('updates pagination by handleCurrentChange', async () => {
    wrapper.vm.filterForm.powerDiffs = [2]
    wrapper.vm.filterForm.winPanDiffs = [1]
    wrapper.vm.filterForm.stabilityTiers = ['A']

    await wrapper.vm.handleCurrentChange(3)

    expect(wrapper.vm.currentPage).toBe(3)
    expect(request.post).toHaveBeenCalledWith('/api/v1/beidan-filter/advanced-filter', expect.any(Object))
  })
})
