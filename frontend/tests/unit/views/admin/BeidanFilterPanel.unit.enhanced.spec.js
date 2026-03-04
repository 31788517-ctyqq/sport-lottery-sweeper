import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import BeidanFilterPanel from '../../../../src/views/admin/BeidanFilterPanel.vue'
import { ElMessage } from 'element-plus'

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

describe('BeidanFilterPanel.vue (enhanced)', () => {
  let wrapper
  let request

  beforeEach(async () => {
    vi.clearAllMocks()
    request = (await import('@/utils/request')).default

    request.get.mockImplementation((url) => {
      if (url.includes('/latest-date-times')) return Promise.resolve({ dateTimes: ['26024', '26023'] })
      if (url.includes('/strategies')) return Promise.resolve({ strategies: [] })
      if (url.includes('/real-time-count')) return Promise.resolve({ matchCount: 8 })
      return Promise.resolve({})
    })

    request.post.mockImplementation((url) => {
      if (url.includes('/advanced-filter')) {
        return Promise.resolve({
          matches: [
            {
              id: 1,
              dateTime: '26024',
              lineId: 100,
              matchTime: '2026-01-01 10:00:00',
              league: '测试联赛',
              homeTeam: 'A队',
              guestTeam: 'B队',
              strength: 2,
              winLevel: 1,
              pLevel: 2,
              stability: 'A'
            }
          ],
          statistics: { totalMatches: 1 },
          pagination: { totalItems: 1 }
        })
      }
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

  it('fetches real-time count successfully', async () => {
    await wrapper.vm.fetchRealData()

    expect(wrapper.vm.totalResults).toBe(8)
    expect(wrapper.vm.loading).toBe(false)
    expect(ElMessage.success).toHaveBeenCalled()
  })

  it('handles fetchRealData error gracefully', async () => {
    request.get.mockImplementation((url) => {
      if (url.includes('/real-time-count')) return Promise.reject(new Error('Network Error'))
      if (url.includes('/latest-date-times')) return Promise.resolve({ dateTimes: ['26024'] })
      if (url.includes('/strategies')) return Promise.resolve({ strategies: [] })
      return Promise.resolve({})
    })

    await wrapper.vm.fetchRealData()

    expect(wrapper.vm.loading).toBe(false)
    expect(ElMessage.error).toHaveBeenCalled()
  })

  it('falls back to default date time options when API fails', async () => {
    request.get.mockImplementation((url) => {
      if (url.includes('/latest-date-times')) return Promise.reject(new Error('down'))
      if (url.includes('/strategies')) return Promise.resolve({ strategies: [] })
      return Promise.resolve({})
    })

    await wrapper.vm.refreshDateTimeOptions()

    expect(wrapper.vm.dateTimeOptions.length).toBeGreaterThan(0)
    expect(wrapper.vm.filterForm.dateTime).toBeTruthy()
  })

  it('applies advanced filter and updates result state', async () => {
    wrapper.vm.filterForm.powerDiffs = [2]
    wrapper.vm.filterForm.winPanDiffs = [1]
    wrapper.vm.filterForm.stabilityTiers = ['A']

    await wrapper.vm.applyAdvancedFilter(true)

    expect(wrapper.vm.strategySelected).toBe(true)
    expect(wrapper.vm.hasResults).toBe(true)
    expect(wrapper.vm.totalResults).toBe(1)
    expect(wrapper.vm.pagedResults.length).toBe(1)
  })

  it('clears selection state when strategy name is empty', async () => {
    wrapper.vm.strategySelected = true
    wrapper.vm.hasResults = true

    await wrapper.vm.handleSelectStrategy('')

    expect(wrapper.vm.strategySelected).toBe(false)
    expect(wrapper.vm.hasResults).toBe(false)
  })

  it('loads strategy options from nested response format', async () => {
    request.get.mockImplementation((url) => {
      if (url.includes('/strategies')) {
        return Promise.resolve({ data: { strategies: [{ name: '策略A', id: 1, threeDimensional: {} }] } })
      }
      if (url.includes('/latest-date-times')) return Promise.resolve({ dateTimes: ['26024'] })
      return Promise.resolve({})
    })

    await wrapper.vm.loadStrategyOptions()

    expect(wrapper.vm.strategyOptions).toContain('策略A')
  })
})
