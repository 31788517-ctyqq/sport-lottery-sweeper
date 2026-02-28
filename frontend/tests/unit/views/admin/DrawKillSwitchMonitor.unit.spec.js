import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { ref } from 'vue'
import DrawKillSwitchMonitor from '../../../../src/views/admin/draw_prediction/DrawKillSwitchMonitor.vue'

const messageMock = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}))

const useKillSwitchState = vi.hoisted(() => ({
  loading: ref(false),
  metricsLoading: ref(false),
  alertLoading: ref(false),
  state: ref({ state: 'RUN', reason: {}, manual_override: 0, updated_at: '2026-01-01T00:00:00Z' }),
  metrics: ref({ roi_7d: 0.11, max_drawdown: 0.07, clv_50: 0.04, win_rate: 0.58, settled_count: 12 }),
  alertSummary: ref({ title: 't', summary: 's', actions: ['a1'] }),
  refreshAll: vi.fn().mockResolvedValue(undefined),
  manualStop: vi.fn().mockResolvedValue(undefined),
  manualRelease: vi.fn().mockResolvedValue(undefined),
  generateAlertSummary: vi.fn().mockResolvedValue(undefined)
}))

vi.mock('@/composables/useKillSwitch', () => ({
  useKillSwitch: () => useKillSwitchState
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: messageMock
  }
})

describe('DrawKillSwitchMonitor.vue', () => {
  const mountComponent = async () => {
    const wrapper = shallowMount(DrawKillSwitchMonitor)
    await flushPromises()
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    useKillSwitchState.refreshAll.mockResolvedValue(undefined)
    useKillSwitchState.manualStop.mockResolvedValue(undefined)
    useKillSwitchState.manualRelease.mockResolvedValue(undefined)
    useKillSwitchState.generateAlertSummary.mockResolvedValue(undefined)
  })

  it('初始化触发刷新', async () => {
    await mountComponent()
    expect(useKillSwitchState.refreshAll).toHaveBeenCalled()
  })

  it('manual stop 成功：空操作人会回落到 admin', async () => {
    const wrapper = await mountComponent()
    wrapper.vm.form.operator = '   '
    wrapper.vm.form.note = 'n1'

    await wrapper.vm.handleManualStop()

    expect(useKillSwitchState.manualStop).toHaveBeenCalledWith({ operator: 'admin', note: 'n1' })
    expect(messageMock.success).toHaveBeenCalledWith('已切换为 STOP')
  })

  it('manual stop 失败：提示错误', async () => {
    useKillSwitchState.manualStop.mockRejectedValueOnce(new Error('boom'))
    const wrapper = await mountComponent()

    await wrapper.vm.handleManualStop()

    expect(messageMock.error).toHaveBeenCalledWith('手动STOP失败')
  })

  it('manual release 失败：提示错误', async () => {
    useKillSwitchState.manualRelease.mockRejectedValueOnce(new Error('boom'))
    const wrapper = await mountComponent()

    await wrapper.vm.handleManualRelease()

    expect(messageMock.error).toHaveBeenCalledWith('手动RELEASE失败')
  })

  it('生成告警说明失败：提示错误', async () => {
    useKillSwitchState.generateAlertSummary.mockRejectedValueOnce(new Error('boom'))
    const wrapper = await mountComponent()

    await wrapper.vm.handleGenerateAlert()

    expect(messageMock.error).toHaveBeenCalledWith('生成告警说明失败')
  })

  it('formatPercent 支持数字字符串', async () => {
    const wrapper = await mountComponent()
    expect(wrapper.vm.formatPercent('0.125')).toBe('12.50%')
    expect(wrapper.vm.formatPercent('abc')).toBe('-')
  })
})
