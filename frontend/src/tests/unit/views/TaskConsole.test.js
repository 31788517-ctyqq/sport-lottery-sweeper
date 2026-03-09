import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import TaskConsole from '@/views/admin/crawler/TaskConsole.vue'

describe('TaskConsole.vue', () => {
  let wrapper

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        auth: { user: { role: 'admin' }, token: 'test-token' }
      }
    })

    wrapper = mount(TaskConsole, {
      global: {
        plugins: [pinia],
        mocks: {
          $route: { path: '/admin/task-console' },
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

  it('应该渲染任务控制台页面', () => {
    expect(wrapper.text()).toContain('任务控制台')
  })
})