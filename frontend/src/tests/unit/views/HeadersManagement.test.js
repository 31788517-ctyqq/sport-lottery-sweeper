import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import HeadersManagement from '@/views/admin/crawler/HeadersManagement.vue'

describe('HeadersManagement.vue', () => {
  let wrapper

  beforeEach(async () => {
    const pinia = createTestingPinia({
      initialState: {
        auth: { 
          user: { role: 'admin' }, 
          token: 'test-token' 
        }
      }
    })

    wrapper = mount(HeadersManagement, {
      global: {
        plugins: [pinia],
        mocks: {
          $route: { path: '/admin/headers-management' },
          $router: { push: vi.fn() }
        }
      }
    })

    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    wrapper.unmount()
  })

  it('应该渲染头部管理页面', () => {
    expect(wrapper.text()).toContain('请求头管理')
  })
})