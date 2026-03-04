// AI_WORKING: coder1 @2026-01-29 18:52:00 - 重建HeaderComponent测试文件
// AI_WORKING: coder1 @2026-01-29 19:15:00 - 修复导入路径，使用别名
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'

// 模拟vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  }),
  useRoute: () => ({
    path: '/'
  })
}))

// 模拟Pinia store
vi.mock('@/stores/user', () => ({
  useUserStore: () => ({
    isLoggedIn: true,
    user: { username: 'testuser', nickname: 'Test User' }
  })
}))

describe('HeaderComponent.vue', () => {
  it('基础测试 - 确保组件可以挂载', () => {
    const wrapper = mount(HeaderComponent, {
      global: {
        mocks: {
          $t: (key) => key
        },
        stubs: {
          'el-menu': true,
          'el-menu-item': true,
          'el-icon': true,
          'el-dropdown': true,
          'el-dropdown-menu': true,
          'el-dropdown-item': true
        }
      }
    })
    
    expect(wrapper.exists()).toBe(true)
  })
})
// AI_DONE: coder1 @2026-01-29 18:52:00