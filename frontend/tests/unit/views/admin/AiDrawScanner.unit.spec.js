import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import AiDrawScanner from '../../../../src/views/admin/draw_prediction/AiDrawScanner.vue'

const apiMock = vi.hoisted(() => ({
  startAiDrawFetchTask: vi.fn(),
  getDrawPredictionTask: vi.fn(),
  getAiDrawList: vi.fn(),
  getAiDrawDetail: vi.fn(),
  getAiDrawRules: vi.fn(),
  saveAiDrawRules: vi.fn(),
  getAiDrawMatchRules: vi.fn(),
  saveAiDrawMatchRules: vi.fn(),
  getAiDrawMatchOverrides: vi.fn(),
  saveAiDrawMatchOverrides: vi.fn(),
  importYingqiuBdSchedule: vi.fn(),
  getBdIssueOptions: vi.fn(),
  getBdLeagueOptions: vi.fn()
}))

const messageMock = vi.hoisted(() => ({
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}))

vi.mock('@/api/drawPrediction', () => apiMock)

vi.mock('element-plus', async () => {
  const actual = await vi.importActual('element-plus')
  return {
    ...actual,
    ElMessage: messageMock
  }
})

describe('AiDrawScanner.vue', () => {
  const mountComponent = async () => {
    const wrapper = shallowMount(AiDrawScanner)
    await flushPromises()
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.getAiDrawRules.mockResolvedValue({ rules: null })
    apiMock.getBdIssueOptions.mockResolvedValue({ items: ['26026', '26025'] })
    apiMock.getBdLeagueOptions.mockResolvedValue({
      items: ['英超', '西甲'],
      resolved_issue_dates: []
    })
    apiMock.getAiDrawList.mockResolvedValue({ items: [] })
    apiMock.getAiDrawDetail.mockResolvedValue({})
    apiMock.getAiDrawMatchRules.mockResolvedValue({ rules: null })
    apiMock.getAiDrawMatchOverrides.mockResolvedValue({ overrides: {} })
    apiMock.saveAiDrawRules.mockResolvedValue({})
    apiMock.saveAiDrawMatchRules.mockResolvedValue({})
    apiMock.saveAiDrawMatchOverrides.mockResolvedValue({})
    apiMock.startAiDrawFetchTask.mockResolvedValue({ task_id: 'task-1' })
    apiMock.getDrawPredictionTask.mockResolvedValue({ status: 'success', progress: 100, message: 'ok' })
    apiMock.importYingqiuBdSchedule.mockResolvedValue({})
  })

  it('按概率降序并去重 match_id', async () => {
    apiMock.getAiDrawList.mockResolvedValueOnce({
      items: [
        { match_id: 'm1', league: '英超', prob_draw: 0.22 },
        { match_id: 'm2', league: '英超', prob_draw: 0.35 },
        { match_id: 'm1', league: '英超', prob_draw: 0.28 }
      ]
    })

    const wrapper = await mountComponent()
    await wrapper.vm.handleQuery()
    await flushPromises()

    expect(wrapper.vm.total).toBe(2)
    expect(wrapper.vm.tableData[0].match_id).toBe('m2')
    expect(wrapper.vm.tableData[0].rank).toBe(1)
    expect(wrapper.vm.tableData[1].match_id).toBe('m1')
    expect(wrapper.vm.tableData[1].rank).toBe(2)
  })

  it('分页切换仅做本地切片，不重复请求列表', async () => {
    apiMock.getAiDrawList.mockResolvedValueOnce({
      items: Array.from({ length: 35 }).map((_, i) => ({
        match_id: `m-${i + 1}`,
        league: '英超',
        prob_draw: 0.5 - i * 0.001
      }))
    })

    const wrapper = await mountComponent()
    await wrapper.vm.handleQuery()
    await flushPromises()

    apiMock.getAiDrawList.mockClear()
    await wrapper.vm.handleCurrentChange(2)
    await flushPromises()

    expect(apiMock.getAiDrawList).not.toHaveBeenCalled()
    expect(wrapper.vm.currentPage).toBe(2)
    expect(wrapper.vm.tableData.length).toBeGreaterThan(0)
  })

  it('非法期号会阻断查询并提示', async () => {
    const wrapper = await mountComponent()
    wrapper.vm.queryIssueNo = '123'

    await wrapper.vm.handleQuery()
    await flushPromises()

    expect(messageMock.warning).toHaveBeenCalledWith('北单期号需为5位数字，如26026')
    expect(apiMock.getAiDrawList).not.toHaveBeenCalled()
  })

  it('重置筛选回到本地日期格式 YYYY-MM-DD', async () => {
    const wrapper = await mountComponent()
    wrapper.vm.queryDate = '1999-01-01'

    await wrapper.vm.resetFilter()
    await flushPromises()

    expect(wrapper.vm.queryDate).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('handleFetch 在任务失败时进入失败分支并提示错误', async () => {
    apiMock.getDrawPredictionTask.mockResolvedValueOnce({
      task_id: 'task-1',
      status: 'failed',
      progress: 30,
      message: '处理中',
      error: 'mock fail reason'
    })

    const wrapper = await mountComponent()
    await wrapper.vm.handleFetch()
    await flushPromises()

    expect(apiMock.importYingqiuBdSchedule).toHaveBeenCalled()
    expect(apiMock.startAiDrawFetchTask).toHaveBeenCalled()
    expect(apiMock.getDrawPredictionTask).toHaveBeenCalledWith('task-1')
    expect(wrapper.vm.fetchTaskStatus).toBe('failed')
    expect(wrapper.vm.fetchTaskMessage).toContain('mock fail reason')
    expect(wrapper.vm.fetching).toBe(false)
    expect(messageMock.error).toHaveBeenCalled()
  })

  it('handleFetch 在轮询超时时进入超时分支', async () => {
    apiMock.getDrawPredictionTask.mockResolvedValueOnce({
      task_id: 'task-1',
      status: 'running',
      progress: 40,
      message: 'running'
    })

    const nowSpy = vi.spyOn(Date, 'now')
    nowSpy.mockReturnValueOnce(0)
    nowSpy.mockReturnValueOnce(10 * 60 * 1000 + 1)

    const wrapper = await mountComponent()
    await wrapper.vm.handleFetch()
    await flushPromises()

    expect(wrapper.vm.fetchTaskStatus).toBe('failed')
    expect(wrapper.vm.fetchTaskMessage).toContain('轮询超时')
    expect(wrapper.vm.fetching).toBe(false)
    expect(messageMock.error).toHaveBeenCalled()

    nowSpy.mockRestore()
  })
})
