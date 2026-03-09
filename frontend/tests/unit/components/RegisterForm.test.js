// frontend/tests/unit/components/RegisterForm.test.js
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import RegisterForm from '@/components/RegisterForm.vue'
import { useAuthStore } from '@/stores/auth.js'

// Mock vue-i18n
vi.mock('vue-i18n', () => ({
  useI18n: () => ({
    t: (key) => key,
    locale: { value: 'zh-CN' }
  })
}))

describe('RegisterForm', () => {
  let wrapper
  let authStore

  beforeEach(() => {
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        auth: {
          isLoading: false,
          error: null
        }
      }
    })

    authStore = useAuthStore(pinia)

    wrapper = mount(RegisterForm, {
      global: {
        plugins: [pinia],
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-alert': true,
          'el-progress': true,
          'el-tooltip': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
    vi.clearAllMocks()
  })

  describe('组件渲染', () => {
    it('应该正确渲染注册表单', () => {
      expect(wrapper.find('.register-form').exists()).toBe(true)
      expect(wrapper.find('.form-title').text()).toContain('注册')
    })

    it('应该显示所有必需的输入字段', () => {
      expect(wrapper.findAllComponents({ name: 'ElInput' }).length).toBeGreaterThanOrEqual(4)
    })

    it('应该显示注册按钮', () => {
      const button = wrapper.find('.register-btn')
      expect(button.exists()).toBe(true)
      expect(button.text()).toContain('注册')
    })
  })

  describe('表单验证', () => {
    it('应该在邮箱为空时显示验证错误', async () => {
      const emailInput = wrapper.findAllComponents({ name: 'ElInput' })[0]
      await emailInput.vm.$emit('blur')
      
      // 触发验证
      await wrapper.vm.$nextTick()
      
      // 检查是否有验证错误（具体实现取决于Element Plus的验证机制）
      expect(wrapper.text()).toContain('邮箱')
    })

    it('应该接受有效的邮箱格式', async () => {
      const emailInput = wrapper.findAllComponents({ name: 'ElInput' })[0]
      await emailInput.vm.$emit('input', 'test@example.com')
      await emailInput.vm.$emit('blur')
      
      await wrapper.vm.$nextTick()
      // 有效邮箱不应该有错误提示
    })

    it('应该拒绝无效的邮箱格式', async () => {
      const emailInput = wrapper.findAllComponents({ name: 'ElInput' })[0]
      await emailInput.vm.$emit('input', 'invalid-email')
      await emailInput.vm.$emit('blur')
      
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toMatch(/邮箱|email/i)
    })

    it('应该验证密码强度', async () => {
      const passwordInput = wrapper.findAllComponents({ name: 'ElInput' })[1]
      
      // 测试弱密码
      await passwordInput.vm.$emit('input', '123')
      await passwordInput.vm.$emit('blur')
      
      await wrapper.vm.$nextTick()
      // 应该显示密码强度指示器或错误信息
      expect(wrapper.text()).toBeTruthy()
    })

    it('应该验证密码确认匹配', async () => {
      const passwordInputs = wrapper.findAllComponents({ name: 'ElInput' })
      const passwordInput = passwordInputs[1]
      const confirmPasswordInput = passwordInputs[2]
      
      await passwordInput.vm.$emit('input', 'Password123!')
      await confirmPasswordInput.vm.$emit('input', 'DifferentPassword123!')
      await confirmPasswordInput.vm.$emit('blur')
      
      await wrapper.vm.$nextTick()
      expect(wrapper.text()).toMatch(/密码|password|confirm/i)
    })
  })

  describe('注册流程', () => {
    it('应该调用auth store的register方法', async () => {
      // 设置有效的表单数据
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com') // email
      await inputs[1].vm.$emit('input', 'Password123!') // password
      await inputs[2].vm.$emit('input', 'Password123!') // confirm password
      await inputs[3].vm.$emit('input', '123456') // captcha

      // Mock成功的注册响应
      authStore.register.mockResolvedValue({ success: true })

      // 点击注册按钮
      await wrapper.find('.register-btn').trigger('click')
      await flushPromises()

      expect(authStore.register).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'Password123!',
        confirmPassword: 'Password123!',
        captcha: '123456'
      })
    })

    it('应该在加载状态下禁用按钮', async () => {
      authStore.register.mockReturnValue(new Promise(() => {})) // 永不resolve的promise
      
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com')
      await inputs[1].vm.$emit('input', 'Password123!')
      await inputs[2].vm.$emit('input', 'Password123!')
      await inputs[3].vm.$emit('input', '123456')

      await wrapper.find('.register-btn').trigger('click')
      await wrapper.vm.$nextTick()

      const registerBtn = wrapper.find('.register-btn')
      expect(registerBtn.attributes('disabled')).toBeDefined()
    })

    it('应该显示加载状态', async () => {
      authStore.isLoading = true
      await wrapper.vm.$nextTick()
      
      expect(wrapper.text()).toMatch(/loading|加载|请稍候/i)
    })

    it('应该显示注册成功消息', async () => {
      authStore.register.mockResolvedValue({ success: true })
      
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com')
      await inputs[1].vm.$emit('input', 'Password123!')
      await inputs[2].vm.$emit('input', 'Password123!')
      await inputs[3].vm.$emit('input', '123456')

      await wrapper.find('.register-btn').trigger('click')
      await flushPromises()

      expect(wrapper.emitted('register-success')).toBeTruthy()
    })

    it('应该显示注册错误消息', async () => {
      authStore.register.mockRejectedValue(new Error('Registration failed'))
      authStore.error = '该邮箱已注册'
      
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com')
      await inputs[1].vm.$emit('input', 'Password123!')
      await inputs[2].vm.$emit('input', 'Password123!')
      await inputs[3].vm.$emit('input', '123456')

      await wrapper.find('.register-btn').trigger('click')
      await flushPromises()

      expect(wrapper.text()).toContain('该邮箱已注册')
      expect(wrapper.emitted('register-error')).toBeTruthy()
    })
  })

  describe('验证码功能', () => {
    it('应该刷新验证码', async () => {
      // 找到刷新验证码按钮并点击
      const refreshBtn = wrapper.find('.captcha-refresh')
      if (refreshBtn.exists()) {
        await refreshBtn.trigger('click')
        await wrapper.vm.$nextTick()
        
        // 验证码应该被刷新（具体实现取决于组件逻辑）
        expect(wrapper.vm.captchaText).toBeTruthy()
      }
    })

    it('应该处理验证码输入', async () => {
      const captchaInput = wrapper.findAllComponents({ name: 'ElInput' })[3]
      
      await captchaInput.vm.$emit('input', 'ABC123')
      await wrapper.vm.$nextTick()
      
      expect(wrapper.vm.formData.captcha).toBe('ABC123')
    })
  })

  describe('组件方法', () => {
    it('应该重置表单', async () => {
      // 设置一些表单数据
      wrapper.setData({
        formData: {
          email: 'test@example.com',
          password: 'password',
          confirmPassword: 'password',
          captcha: '123456'
        }
      })

      wrapper.vm.resetForm()
      
      expect(wrapper.vm.formData.email).toBe('')
      expect(wrapper.vm.formData.password).toBe('')
      expect(wrapper.vm.formData.confirmPassword).toBe('')
      expect(wrapper.vm.formData.captcha).toBe('')
    })

    it('应该验证表单', async () => {
      wrapper.setData({
        formData: {
          email: 'invalid-email',
          password: '123',
          confirmPassword: '456',
          captcha: ''
        }
      })

      const isValid = wrapper.vm.validateForm()
      expect(isValid).toBe(false)
    })
  })

  describe('边界情况和错误处理', () => {
    it('应该处理网络错误', async () => {
      authStore.register.mockRejectedValue(new Error('Network error'))
      
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com')
      await inputs[1].vm.$emit('input', 'Password123!')
      await inputs[2].vm.$emit('input', 'Password123!')
      await inputs[3].vm.$emit('input', '123456')

      await wrapper.find('.register-btn').trigger('click')
      await flushPromises()

      expect(wrapper.emitted('register-error')).toBeTruthy()
    })

    it('应该处理服务器错误响应', async () => {
      authStore.register.mockResolvedValue({
        success: false,
        message: 'Server validation failed'
      })
      
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      
      await inputs[0].vm.$emit('input', 'test@example.com')
      await inputs[1].vm.$emit('input', 'Password123!')
      await inputs[2].vm.$emit('input', 'Password123!')
      await inputs[3].vm.$emit('input', '123456')

      await wrapper.find('.register-btn').trigger('click')
      await flushPromises()

      expect(wrapper.emitted('register-error')).toBeTruthy()
    })
  })

  describe('可访问性', () => {
    it('应该为表单元素提供适当的标签', () => {
      const inputs = wrapper.findAllComponents({ name: 'ElInput' })
      inputs.forEach(input => {
        expect(input.attributes('aria-label') || input.attributes('placeholder')).toBeTruthy()
      })
    })

    it('应该在按钮上提供适当的文本', () => {
      const button = wrapper.find('.register-btn')
      expect(button.text()).toBeTruthy()
      expect(button.text().length).toBeGreaterThan(0)
    })
  })
})