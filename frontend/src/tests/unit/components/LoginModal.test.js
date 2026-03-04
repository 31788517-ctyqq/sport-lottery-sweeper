// AI_WORKING: coder1 @2026-01-29 18:52:00 - 重建LoginModal测试文件
// AI_WORKING: coder1 @2026-01-29 19:16:00 - 修复导入路径，使用别名
import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import LoginModal from '@/components/LoginModal.vue'

// 模拟vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key) => key
  })
}))

describe('LoginModal.vue', () => {
  it('基础测试 - 确保组件可以挂载', () => {
    const wrapper = mount(LoginModal, {
      global: {
        mocks: {
          $t: (key) => key
        },
        stubs: {
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true
        }
      }
    })
    
    expect(wrapper.exists()).toBe(true)
  })
})
// AI_DONE: coder1 @2026-01-29 18:52:00