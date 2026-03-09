import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import IpPoolManagement from '@/views/admin/crawler/IpPoolManagement.vue'

describe('IpPoolManagement.vue', () => {
  it('应该渲染IP池管理页面', async () => {
    const wrapper = mount(IpPoolManagement, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              auth: { user: { role: 'admin' }, token: 'test-token' }
            }
          })
        ],
        mocks: {
          $route: { path: '/admin/ip-pool-management' },
          $router: { push: () => {} }
        }
      }
    })

    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('IP池管理')
  })
})