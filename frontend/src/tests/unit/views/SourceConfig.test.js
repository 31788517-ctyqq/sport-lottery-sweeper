import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import SourceConfig from '@/views/admin/crawler/SourceConfig.vue'

describe('SourceConfig.vue', () => {
  let wrapper

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        auth: { user: { role: 'admin' }, token: 'test-token' }
      }
    })

    wrapper = mount(SourceConfig, {
      global: {
        plugins: [pinia],
        mocks: {
          $route: { path: '/admin/source-config' },
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

  it('应该渲染源配置页面', () => {
    expect(wrapper.text()).toContain('源配置')
  })
})