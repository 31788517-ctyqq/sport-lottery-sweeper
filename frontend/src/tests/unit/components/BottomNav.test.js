// AI_WORKING: coder1 @2026-01-29 18:52:00 - 重建BottomNav测试文件
// AI_WORKING: coder1 @2026-01-29 19:16:00 - 修复导入路径，使用别名
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import BottomNav from '@/components/BottomNav.vue'

// 模拟vue-router
vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn()
  }),
  useRoute: () => ({
    path: '/'
  })
}))

describe('BottomNav.vue', () => {
  it('基础测试 - 确保组件可以挂载', () => {
    const wrapper = mount(BottomNav, {
      global: {
        mocks: {
          $t: (key) => key
        },
        stubs: {
          'el-menu': true,
          'el-menu-item': true,
          'el-icon': true
        }
      }
    })
    
    expect(wrapper.exists()).toBe(true)
  })
})
// AI_DONE: coder1 @2026-01-29 18:52:00