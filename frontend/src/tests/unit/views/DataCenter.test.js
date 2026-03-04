import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DataCenter from '@/views/admin/crawler/DataCenter.vue'

// 模拟Element Plus组件和全局对象
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn()
}

// 模拟图表库以避免测试错误
global.echarts = {
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  }))
}

describe('DataCenter.vue', () => {
  let wrapper

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        auth: { user: { role: 'admin' }, token: 'test-token' }
      }
    })

    wrapper = mount(DataCenter, {
      global: {
        plugins: [pinia],
        mocks: {
          $route: { path: '/admin/data-center' },
          $router: { push: vi.fn() }
        }
      }
    })

    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    vi.restoreAllMocks()
  })

  describe('基础渲染', () => {
    it('应该渲染数据中心页面', () => {
      expect(wrapper.text()).toContain('数据中心')
    })
  })
})