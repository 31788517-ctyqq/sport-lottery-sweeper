import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount, flushPromises } from '@vue/test-utils'
import { reactive } from 'vue'
import ModelWorkbench from '../../../../src/views/admin/draw_prediction/ModelWorkbench.vue'

vi.mock('@/views/admin/draw_prediction/DrawDataFeature.vue', () => ({
  default: { name: 'DrawDataFeature', template: '<div />' }
}))
vi.mock('@/views/admin/draw_prediction/DrawModelTrainEval.vue', () => ({
  default: { name: 'DrawModelTrainEval', template: '<div />' }
}))
vi.mock('@/views/admin/draw_prediction/DrawModelManageDeploy.vue', () => ({
  default: { name: 'DrawModelManageDeploy', template: '<div />' }
}))
vi.mock('@/views/admin/draw_prediction/DrawPredictionMonitor.vue', () => ({
  default: { name: 'DrawPredictionMonitor', template: '<div />' }
}))

const routeState = reactive({
  path: '/admin/draw-prediction/model-workbench',
  query: {}
})

const routerMock = {
  replace: vi.fn().mockResolvedValue(undefined)
}

vi.mock('vue-router', () => ({
  useRoute: () => routeState,
  useRouter: () => routerMock
}))

describe('ModelWorkbench.vue', () => {
  const mountComponent = async () => {
    const wrapper = shallowMount(ModelWorkbench)
    await flushPromises()
    return wrapper
  }

  beforeEach(() => {
    vi.clearAllMocks()
    routeState.path = '/admin/draw-prediction/model-workbench'
    routeState.query = {}
  })

  it('初始无tab时会默认data并同步到URL', async () => {
    const wrapper = await mountComponent()

    expect(wrapper.vm.activeTab).toBe('data')
    expect(routerMock.replace).toHaveBeenCalledWith({
      path: '/admin/draw-prediction/model-workbench',
      query: { tab: 'data' }
    })
  })

  it('初始tab非法时会归一化为data并写回URL', async () => {
    routeState.query = { tab: 'UNKNOWN', foo: '1' }
    const wrapper = await mountComponent()

    expect(wrapper.vm.activeTab).toBe('data')
    expect(routerMock.replace).toHaveBeenCalledWith({
      path: '/admin/draw-prediction/model-workbench',
      query: { tab: 'data', foo: '1' }
    })
  })

  it('handleTabChange切换标签时保留其他query参数', async () => {
    routeState.query = { tab: 'data', foo: 'bar' }
    const wrapper = await mountComponent()
    routerMock.replace.mockClear()

    wrapper.vm.handleTabChange('training')
    await flushPromises()

    expect(wrapper.vm.activeTab).toBe('training')
    expect(routerMock.replace).toHaveBeenCalledWith({
      path: '/admin/draw-prediction/model-workbench',
      query: { tab: 'training', foo: 'bar' }
    })
  })

  it('handleTabChange选择当前tab时不重复replace', async () => {
    routeState.query = { tab: 'monitoring' }
    const wrapper = await mountComponent()
    routerMock.replace.mockClear()

    wrapper.vm.handleTabChange('monitoring')
    await flushPromises()

    expect(routerMock.replace).not.toHaveBeenCalled()
  })
})
