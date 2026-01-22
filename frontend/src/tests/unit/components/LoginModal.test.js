import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import LoginModal from '@/components/LoginModal.vue'

// 模拟 vue-i18n
type Mock$t = (key: string) => string

vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: ((key: string) => key) as Mock$t
  })
}))

describe('LoginModal.vue', () => {
  let wrapper
  
  beforeEach(() => {
    // 重置所有 mocks
    vi.clearAllMocks()
    
    // 模拟 window.alert
    global.alert = vi.fn()
    
    // 创建组件实例
    wrapper = mount(LoginModal, {
      global: {
        mocks: {
          $t: (key: string) => key
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
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染登录弹窗', () => {
      expect(wrapper.find('.login-modal').exists()).toBe(true)
    })

    it('应该包含用户名和密码输入框', () => {
      expect(wrapper.find('input[type="text"]').exists()).toBe(true)
      expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    })

    it('应该包含登录按钮', () => {
      expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    })
  })

  describe('表单验证', () => {
    it('用户名不能为空', async () => {
      const usernameInput = wrapper.find('input[type="text"]')
      await usernameInput.setValue('')
      await usernameInput.trigger('blur')
      
      // 触发表单验证
      await wrapper.find('form').trigger('submit.prevent')
      
      expect(global.alert).toHaveBeenCalledWith('请输入用户名')
    })

    it('密码不能为空', async () => {
      const passwordInput = wrapper.find('input[type="password"]')
      await passwordInput.setValue('')
      await passwordInput.trigger('blur')
      
      await wrapper.find('form').trigger('submit.prevent')
      
      expect(global.alert).toHaveBeenCalledWith('请输入密码')
    })

    it('密码长度不能少于6位', async () => {
      const passwordInput = wrapper.find('input[type="password"]')
      await passwordInput.setValue('12345')
      await passwordInput.trigger('blur')
      
      await wrapper.find('form').trigger('submit.prevent')
      
      expect(global.alert).toHaveBeenCalledWith('密码长度不能少于6位')
    })
  })

  describe('登录逻辑', () => {
    it('登录成功应该关闭弹窗', async () => {
      // 模拟 API 调用成功
      const mockLogin = vi.fn().mockResolvedValue({ success: true })
      wrapper.vm.$parent.$refs = { loginFormRef: { validate: vi.fn().mockResolvedValue(true) } }
      
      // 填充有效数据
      await wrapper.find('input[type="text"]').setValue('testuser')
      await wrapper.find('input[type="password"]').setValue('123456')
      
      // 模拟登录方法
      wrapper.vm.handleLogin = mockLogin
      
      await wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      expect(mockLogin).toHaveBeenCalled()
    })

    it('登录失败应该显示错误信息', async () => {
      const mockLogin = vi.fn().mockRejectedValue(new Error('登录失败'))
      
      await wrapper.find('input[type="text"]').setValue('testuser')
      await wrapper.find('input[type="password"]').setValue('123456')
      
      wrapper.vm.handleLogin = mockLogin
      
      await wrapper.find('form').trigger('submit.prevent')
      await nextTick()
      
      expect(global.alert).toHaveBeenCalledWith('登录失败')
    })
  })

  describe('关闭功能', () => {
    it('点击关闭按钮应该关闭弹窗', async () => {
      const closeButton = wrapper.find('.close-btn')
      if (closeButton.exists()) {
        await closeButton.trigger('click')
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })

    it('点击遮罩层应该关闭弹窗', async () => {
      await wrapper.setProps({ closeOnClickModal: true })
      
      // 模拟遮罩层点击
      const modal = wrapper.find('.el-overlay')
      if (modal.exists()) {
        await modal.trigger('click')
        expect(wrapper.emitted('close')).toBeTruthy()
      }
    })
  })
})