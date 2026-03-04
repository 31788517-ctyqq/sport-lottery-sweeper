// AI_WORKING: coder1 @2026-01-29 18:52:00 - 重建MainView测试文件
// AI_WORKING: coder1 @2026-01-29 19:16:00 - 修复导入路径，使用别名
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MainView from '@/components/MainView.vue'

// 模拟子组件
vi.mock('@/components/HeaderComponent.vue', () => ({
  default: vi.fn()
}))

vi.mock('@/components/BottomNav.vue', () => ({
  default: vi.fn()
}))

vi.mock('@/components/MainContent.vue', () => ({
  default: vi.fn()
}))

describe('MainView.vue', () => {
  it('基础测试 - 确保组件可以挂载', () => {
    const wrapper = mount(MainView, {
      global: {
        mocks: {
          $t: (key) => key
        },
        stubs: {
          'HeaderComponent': true,
          'BottomNav': true,
          'MainContent': true
        }
      }
    })
    
    expect(wrapper.exists()).toBe(true)
  })
})
// AI_DONE: coder1 @2026-01-29 18:52:00