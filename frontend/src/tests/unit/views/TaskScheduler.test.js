import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import TaskScheduler from '@/views/admin/crawler/TaskScheduler.vue'

describe('TaskScheduler.vue', () => {
  it('应该渲染任务调度器页面', () => {
    const wrapper = mount(TaskScheduler, {
      global: {
        plugins: [
          createTestingPinia({
            initialState: {
              auth: { user: { role: 'admin' }, token: 'test-token' }
            }
          })
        ]
      }
    })

    expect(wrapper.text()).toContain('任务调度')
    wrapper.unmount()
  })
})