import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import BeidanFilterPanel from '../../../../src/views/admin/BeidanFilterPanel.vue'

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

describe('BeidanFilterPanel.vue (unit)', () => {
  let wrapper
  let request

  const mountPanel = async () => {
    wrapper = shallowMount(BeidanFilterPanel, {
      global: {
        plugins: [createTestingPinia({ createSpy: vi.fn })]
      }
    })
    await flushPromises()
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    request = (await import('@/utils/request')).default

    request.get.mockImplementation((url) => {
      if (url.includes('/latest-date-times')) return Promise.resolve({ dateTimes: ['26024', '26023'] })
      if (url.includes('/strategies')) return Promise.resolve({ strategies: [] })
      if (url.includes('/real-time-count')) return Promise.resolve({ matchCount: 5 })
      return Promise.resolve({})
    })

    request.post.mockImplementation((url) => {
      if (url.includes('/advanced-filter')) {
        return Promise.resolve({
          matches: [],
          statistics: {},
          pagination: { totalItems: 0 }
        })
      }
      if (url.includes('/strategies')) return Promise.resolve({ id: 1, name: '测试策略' })
      return Promise.resolve({ success: true })
    })

    request.delete.mockResolvedValue({ success: true })

    await mountPanel()
  })

  it('renders root container', () => {
    expect(wrapper.find('.beidan-filter-panel').exists()).toBe(true)
  })

  it('initializes basic filter state', () => {
    expect(wrapper.vm.filterForm.powerDiffs).toEqual([])
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([])
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual([])
    expect(wrapper.vm.filterForm.sortBy).toBe('p_level')
  })

  it('applies strong preset and calls advanced filter API', async () => {
    await wrapper.vm.applyPreset('strong')

    expect(wrapper.vm.filterForm.powerDiffs).toEqual([2, 3])
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([3, 4])
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual(['S', 'A', 'B'])
    expect(request.post).toHaveBeenCalledWith('/api/v1/beidan-filter/advanced-filter', expect.any(Object))
  })

  it('resets filter state', () => {
    wrapper.vm.filterForm.powerDiffs = [2]
    wrapper.vm.filterForm.winPanDiffs = [3]
    wrapper.vm.filterForm.stabilityTiers = ['S']
    wrapper.vm.strategySelected = true
    wrapper.vm.hasResults = true

    wrapper.vm.resetFilters()

    expect(wrapper.vm.filterForm.powerDiffs).toEqual([])
    expect(wrapper.vm.filterForm.winPanDiffs).toEqual([])
    expect(wrapper.vm.filterForm.stabilityTiers).toEqual([])
    expect(wrapper.vm.strategySelected).toBe(false)
    expect(wrapper.vm.hasResults).toBe(false)
  })

  it('opens analysis dialog with mapped data', () => {
    wrapper.vm.handleOpenAnalysis({
      match_id: '26024_1',
      date_time: '26024',
      line_id: 1,
      match_time: '2026-01-01 12:00:00',
      league: '测试联赛',
      home_team: '主队',
      away_team: '客队',
      power_home: '80',
      power_away: '70',
      power_diff: 1,
      delta_wp: 1,
      p_level: 2,
      stability: 'A'
    })

    expect(wrapper.vm.analysisVisible).toBe(true)
    expect(wrapper.vm.currentAnalysisData.homeTeam).toBe('主队')
    expect(wrapper.vm.currentAnalysisData.guestTeam).toBe('客队')
  })
})
