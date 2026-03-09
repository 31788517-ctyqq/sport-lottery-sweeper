import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import Poisson11Scanner from '../../../../src/views/admin/draw_prediction/Poisson11Scanner.vue'

const apiMock = vi.hoisted(() => ({
  startPoisson11FetchTask: vi.fn(),
  getDrawPredictionTask: vi.fn(),
  getPoisson11List: vi.fn(),
  getPoisson11Detail: vi.fn(),
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

const mockDetail = {
  prob_11: 0.12,
  rank: 1,
  mu_total: 2.3,
  mu_diff: 0.1,
  mu_home: 1.2,
  mu_away: 1.1,
  input_payload: {
    total_goals_line: 2.5,
    total_goals_line_source: 'source_attributes',
    handicap: 0,
    handicap_source: 'source_attributes',
    odds_score_11: 8.5,
    odds_score_11_source: 'source_attributes',
    odds: { draw: 3.0 },
    source_attributes: {},
    quality_flags: []
  }
}

describe('Poisson11Scanner.vue', () => {
  const mountComponent = async () => {
    const wrapper = shallowMount(Poisson11Scanner)
    await flushPromises()
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.getBdIssueOptions.mockResolvedValue({ items: ['26026', '26025'] })
    apiMock.getBdLeagueOptions.mockResolvedValue({ items: ['英超', '西甲'], resolved_issue_dates: [] })
    apiMock.getPoisson11List.mockResolvedValue({ items: [] })
    apiMock.getPoisson11Detail.mockResolvedValue(mockDetail)
    apiMock.startPoisson11FetchTask.mockResolvedValue({ task_id: 'task-1' })
    apiMock.getDrawPredictionTask.mockResolvedValue({ status: 'success', progress: 100, message: 'ok' })
  })

  it('按排名优先排序并去重 match_id', async () => {
    apiMock.getPoisson11List.mockResolvedValueOnce({
      items: [
        { match_id: 'm1', league: '英超', rank: 3, prob_11: 0.10 },
        { match_id: 'm2', league: '英超', rank: 1, prob_11: 0.08 },
        { match_id: 'm1', league: '英超', rank: 2, prob_11: 0.11 }
      ]
    })

    const wrapper = await mountComponent()
    wrapper.vm.handleQuery()
    await flushPromises()

    expect(wrapper.vm.total).toBe(2)
    expect(wrapper.vm.tableData[0].match_id).toBe('m2')
    expect(wrapper.vm.tableData[0].rank).toBe(1)
    expect(wrapper.vm.tableData[1].match_id).toBe('m1')
    expect(wrapper.vm.tableData[1].rank).toBe(2)
  })

  it('分页切换仅做本地切片，不重复请求列表', async () => {
    apiMock.getPoisson11List.mockResolvedValueOnce({
      items: Array.from({ length: 35 }).map((_, i) => ({
        match_id: `m-${i + 1}`,
        league: '英超',
        rank: i + 1,
        prob_11: 0.2 - i * 0.001
      }))
    })

    const wrapper = await mountComponent()
    wrapper.vm.handleQuery()
    await flushPromises()

    apiMock.getPoisson11List.mockClear()
    wrapper.vm.handleCurrentChange(2)
    await flushPromises()

    expect(apiMock.getPoisson11List).not.toHaveBeenCalled()
    expect(wrapper.vm.currentPage).toBe(2)
    expect(wrapper.vm.tableData.length).toBeGreaterThan(0)
  })

  it('非法期号会阻断查询并提示', async () => {
    const wrapper = await mountComponent()
    wrapper.vm.queryIssueNo = '123'

    wrapper.vm.handleQuery()
    await flushPromises()

    expect(messageMock.warning).toHaveBeenCalledWith('北单期号需为5位数字，如26026')
    expect(apiMock.getPoisson11List).not.toHaveBeenCalled()
  })

  it('重置筛选回到本地日期格式 YYYY-MM-DD', async () => {
    const wrapper = await mountComponent()
    wrapper.vm.queryDate = '1999-01-01'

    wrapper.vm.resetFilter()
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

    expect(apiMock.startPoisson11FetchTask).toHaveBeenCalled()
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
