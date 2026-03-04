import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { reactive, ref } from 'vue'
import DrawSuggestionCenter from '../../../../src/views/admin/draw_prediction/DrawSuggestionCenter.vue'

const messageMock = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}))

const useDrawSuggestionState = vi.hoisted(() => ({
  loading: ref(false),
  snapshotsLoading: ref(false),
  metricsLoading: ref(false),
  submitting: ref(false),
  suggestions: ref([]),
  suggestionsTotal: ref(0),
  snapshots: ref([]),
  snapshotsTotal: ref(0),
  metrics: ref({ state: 'RUN', roi_7d: 0, max_drawdown: 0, win_rate: 0, clv_50: 0 }),
  query: reactive({ date: '', decision: '', page: 1, pageSize: 20 }),
  snapshotTask: reactive({ progress: 0, status: 'idle', message: '' }),
  generateTask: reactive({ progress: 0, status: 'idle', message: '' }),
  settleTask: reactive({ progress: 0, status: 'idle', message: '' }),
  stateTagType: ref('success'),
  explanationMap: reactive({}),
  explaining: reactive({}),
  latestReport: ref(''),
  reportLoading: ref(false),
  refreshSuggestions: vi.fn().mockResolvedValue(undefined),
  refreshSnapshots: vi.fn().mockResolvedValue(undefined),
  refreshMetrics: vi.fn().mockResolvedValue(undefined),
  fetchSnapshots: vi.fn().mockResolvedValue(undefined),
  generateSuggestions: vi.fn().mockResolvedValue(undefined),
  settlePaperBets: vi.fn().mockResolvedValue(undefined),
  batchCreatePaperBets: vi.fn().mockResolvedValue({ created_count: 1 }),
  explainSuggestion: vi.fn().mockResolvedValue('explain text'),
  generateReport: vi.fn().mockResolvedValue('report text')
}))

vi.mock('@/composables/useDrawSuggestion', () => ({
  useDrawSuggestion: () => useDrawSuggestionState
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: messageMock
  }
})

describe('DrawSuggestionCenter.vue', () => {
  const mountComponent = async () => {
    const wrapper = shallowMount(DrawSuggestionCenter)
    await flushPromises()
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    useDrawSuggestionState.query.date = ''
    useDrawSuggestionState.query.decision = ''
    useDrawSuggestionState.query.page = 1
    useDrawSuggestionState.query.pageSize = 20
    useDrawSuggestionState.metrics.value = { state: 'RUN', roi_7d: 0, max_drawdown: 0, win_rate: 0, clv_50: 0 }
    useDrawSuggestionState.suggestions.value = []
    useDrawSuggestionState.suggestionsTotal.value = 0
    useDrawSuggestionState.snapshots.value = []
    useDrawSuggestionState.snapshotsTotal.value = 0
    useDrawSuggestionState.latestReport.value = ''
    Object.keys(useDrawSuggestionState.explanationMap).forEach((k) => delete useDrawSuggestionState.explanationMap[k])

    useDrawSuggestionState.refreshSuggestions.mockResolvedValue(undefined)
    useDrawSuggestionState.refreshSnapshots.mockResolvedValue(undefined)
    useDrawSuggestionState.refreshMetrics.mockResolvedValue(undefined)
    useDrawSuggestionState.batchCreatePaperBets.mockResolvedValue({ created_count: 1 })
    useDrawSuggestionState.explainSuggestion.mockResolvedValue('explain text')
    useDrawSuggestionState.generateReport.mockResolvedValue('report text')
  })

  it('初始化时会加载建议/快照/指标并写入当天日期', async () => {
    await mountComponent()

    expect(useDrawSuggestionState.query.date).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    expect(useDrawSuggestionState.refreshSuggestions).toHaveBeenCalled()
    expect(useDrawSuggestionState.refreshSnapshots).toHaveBeenCalled()
    expect(useDrawSuggestionState.refreshMetrics).toHaveBeenCalled()
  })

  it('批量创建：未选择 BET 时提示并阻断请求', async () => {
    const wrapper = await mountComponent()

    await wrapper.vm.handleSelectionChange([{ id: 1, decision: 'SKIP' }])
    await wrapper.vm.handleBatchCreatePaperBets()

    expect(messageMock.warning).toHaveBeenCalledWith('请先勾选 decision=BET 的建议')
    expect(useDrawSuggestionState.batchCreatePaperBets).not.toHaveBeenCalled()
  })

  it('批量创建：仅传递 BET 且刷新指标', async () => {
    const wrapper = await mountComponent()

    await wrapper.vm.handleSelectionChange([
      { id: '11', decision: 'BET' },
      { id: 9, decision: 'SKIP' },
      { id: 'x', decision: 'BET' },
      { id: 7, decision: 'BET' }
    ])
    await wrapper.vm.handleBatchCreatePaperBets()
    await flushPromises()

    expect(useDrawSuggestionState.batchCreatePaperBets).toHaveBeenCalledWith([11, 7])
    expect(useDrawSuggestionState.refreshMetrics).toHaveBeenCalled()
    expect(messageMock.success).toHaveBeenCalledWith('已创建 1 条模拟下注')
  })

  it('批量创建失败时提示错误', async () => {
    useDrawSuggestionState.batchCreatePaperBets.mockRejectedValueOnce(new Error('boom'))
    const wrapper = await mountComponent()

    await wrapper.vm.handleSelectionChange([{ id: 2, decision: 'BET' }])
    await wrapper.vm.handleBatchCreatePaperBets()
    await flushPromises()

    expect(messageMock.error).toHaveBeenCalledWith('创建模拟下注失败')
  })

  it('决策路径复制成功与失败分支', async () => {
    const wrapper = await mountComponent()
    const writeText = vi.fn().mockResolvedValue(undefined)
    Object.defineProperty(globalThis, 'navigator', {
      configurable: true,
      value: { clipboard: { writeText } }
    })

    await wrapper.vm.copyDecisionPath({
      edge: 0.06,
      decision: 'BET',
      features: { base_prob: 0.31, odds_draw_place: 3.2, edge_min: 0.03 }
    })

    expect(writeText).toHaveBeenCalled()
    expect(messageMock.success).toHaveBeenCalledWith('决策路径已复制')

    writeText.mockRejectedValueOnce(new Error('copy failed'))
    await wrapper.vm.copyDecisionPath({ features: {} })
    expect(messageMock.error).toHaveBeenCalledWith('复制失败，请手动复制')
  })

  it('AI解读失败与日报失败会提示错误', async () => {
    useDrawSuggestionState.explainSuggestion.mockRejectedValueOnce(new Error('explain fail'))
    useDrawSuggestionState.generateReport.mockRejectedValueOnce(new Error('report fail'))

    const wrapper = await mountComponent()
    await wrapper.vm.handleExplain({ id: 99 })
    await wrapper.vm.handleGenerateReport()

    expect(messageMock.error).toHaveBeenCalledWith('获取AI解读失败')
    expect(messageMock.error).toHaveBeenCalledWith('生成日报失败')
  })
})
