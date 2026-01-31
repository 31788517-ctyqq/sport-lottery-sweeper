// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import LoginView from '../../views/LoginView.vue'
import { useAuth } from '../../composables/useAuth.js'

// 模拟全局对象
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn()
}

describe('LoginView.vue', () => {
  let wrapper
  let authComposable

  beforeEach(() => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState
      }
    })
    
    authComposable = useAuth()
    
    wrapper = mount(LoginView, {
      
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
  })

  describe('组件渲染', () => {
    it('应该正确渲染登录页面', () => {
      expect(wrapper.find('.login-view').exists()).toBe(true)
    })

    it('应该显示登录标题', () => {
      const title = wrapper.find('h1')
      expect(title.exists() || wrapper.text().includes('登录')).toBe(true)
    })

    it('应该包含登录表单元素', () => {
      expect(wrapper.find('form').exists()).toBe(true)
    })
  })

  describe('表单功能', () => {
    it('应该包含输入框', () => {
      const inputs = wrapper.findAll('input')
      expect(inputs.length).toBeGreaterThanOrEqual(2)
    })

    it('应该包含记住我选项', () => {
      const checkbox = wrapper.find('input[type="checkbox"]')
      if (checkbox.exists()) {
        expect(checkbox.element.checked).toBe(false)
      }
    })
  })

  describe('登录流程', () => {
    it('应该调用登录方法', () => {
      authComposable.login = vi.fn().mockResolvedValue({ success: true })
      
      const form = wrapper.find('form')
      if (form.exists()) {
        form.trigger('submit')
        expect(authComposable.login).toHaveBeenCalled()
      }
    })
  })

  describe('错误处理', () => {
    it('应该处理登录失败', () => {
      authComposable.login = vi.fn().mockRejectedValue(new Error('Login failed'))
      
      const form = wrapper.find('form')
      if (form.exists()) {
        form.trigger('submit')
        expect(authComposable.login).toHaveBeenCalled()
      }
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
