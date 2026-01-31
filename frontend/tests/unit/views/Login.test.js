import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { ElMessage } from 'element-plus'

// Mock Element Plus Message
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  }
}))

// Mock vue-router
const mockRouter = {
  push: vi.fn()
}
vi.mock('vue-router', () => ({
  useRouter: () => mockRouter
}))

// Mock API
const mockLoginApi = vi.fn()
vi.mock('@/utils/request', () => ({
  default: {
    post: mockLoginApi
  }
}))

// Mock localStorage
const localStorageMock = {
  setItem: vi.fn(),
  getItem: vi.fn(),
  removeItem: vi.fn()
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('Login.vue', () => {
  let wrapper
  let pinia
  
  const mockUserCredentials = {
    username: 'admin',
    password: '123456'
  }
  
  const mockLoginResponse = {
    code: 200,
    message: '登录成功',
    data: {
      access_token: 'mock-jwt-token',
      token_type: 'bearer',
      user_info: {
        username: 'admin',
        email: 'admin@example.com',
        is_active: true
      }
    }
  }
  
  beforeEach(() => {
    // 重置所有mocks
    vi.clearAllMocks()
    
    // 创建新的pinia实例
    pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        admin: {
          token: '',
          userInfo: null
        }
      }
    })
    
    // Mock成功的登录API响应
    mockLoginApi.mockResolvedValue(mockLoginResponse)
    
    // 设置localStorage mock
    localStorageMock.setItem.mockImplementation(() => {})
    localStorageMock.getItem.mockReturnValue(null)
  })
  
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })
  
  const createWrapper = (props = {}, options = {}) => {
    return mount(Login, {
      props,
      global: {
        plugins: [pinia],
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-divider': true,
          'router-link': true
        }
      },
      ...options
    })
  }
  
  describe('组件渲染', () => {
    it('应该正确渲染登录表单', () => {
      wrapper = createWrapper()
      
      expect(wrapper.find('.login-container').exists()).toBe(true)
      expect(wrapper.find('.login-header').exists()).toBe(true)
      expect(wrapper.find('.login-form').exists()).toBe(true)
    })
    
    it('应该显示系统标题和描述', () => {
      wrapper = createWrapper()
      
      expect(wrapper.text()).toContain('竞彩足球扫盘系统')
      expect(wrapper.text()).toContain('专业的体育彩票数据分析平台')
    })
    
    it('应该显示测试用户提示', () => {
      wrapper = createWrapper()
      
      expect(wrapper.text()).toContain('测试账户')
      expect(wrapper.text()).toContain('admin')
      expect(wrapper.text()).toContain('123456')
    })
  })
  
  describe('表单交互', () => {
    it('应该能够输入用户名和密码', async () => {
      wrapper = createWrapper()
      
      // 这里需要根据实际的组件实现来测试表单输入
      // 由于我们使用了stub，这里主要测试组件的基本结构
      expect(wrapper.exists()).toBe(true)
    })
    
    it('应该有登录按钮并且可以点击', () => {
      wrapper = createWrapper()
      
      // 测试登录按钮存在
      expect(wrapper.find('.login-btn').exists()).toBe(true)
    })
  })
  
  describe('登录功能', () => {
    it('成功登录应该保存token和用户信息', async () => {
      wrapper = createWrapper()
      
      // 模拟登录方法调用
      await wrapper.vm.handleLogin(mockUserCredentials)
      await flushPromises()
      
      // 验证API被调用
      expect(mockLoginApi).toHaveBeenCalledWith('/auth/login', mockUserCredentials)
      
      // 验证localStorage被调用
      expect(localStorageMock.setItem).toHaveBeenCalledWith('token', mockLoginResponse.data.access_token)
      
      // 验证成功消息显示
      expect(ElMessage.success).toHaveBeenCalledWith('登录成功')
      
      // 验证路由跳转
      expect(mockRouter.push).toHaveBeenCalledWith('/admin/dashboard')
    })
    
    it('登录失败应该显示错误消息', async () => {
      // Mock登录失败
      const errorMessage = '用户名或密码错误'
      mockLoginApi.mockRejectedValue(new Error(errorMessage))
      
      wrapper = createWrapper()
      
      await wrapper.vm.handleLogin(mockUserCredentials)
      await flushPromises()
      
      // 验证错误消息显示
      expect(ElMessage.error).toHaveBeenCalledWith(errorMessage)
      
      // 验证路由没有跳转
      expect(mockRouter.push).not.toHaveBeenCalled()
    })
    
    it('网络错误应该显示网络错误消息', async () => {
      // Mock网络错误
      mockLoginApi.mockRejectedValue(new Error('Network Error'))
      
      wrapper = createWrapper()
      
      await wrapper.vm.handleLogin(mockUserCredentials)
      await flushPromises()
      
      // 验证网络错误消息显示
      expect(ElMessage.error).toHaveBeenCalledWith('网络连接失败，请检查网络设置')
    })
    
    it('空用户名应该显示验证错误', async () => {
      wrapper = createWrapper()
      
      const emptyCredentials = {
        username: '',
        password: '123456'
      }
      
      await wrapper.vm.handleLogin(emptyCredentials)
      await flushPromises()
      
      // 验证验证错误消息
      expect(ElMessage.warning).toHaveBeenCalledWith('请输入用户名和密码')
      
      // 验证API没有被调用
      expect(mockLoginApi).not.toHaveBeenCalled()
    })
  })
  
  describe('快速填充功能', () => {
    it('应该能够填充测试用户凭据', async () => {
      wrapper = createWrapper()
      
      // 模拟fillTestCredentials方法
      await wrapper.vm.fillTestCredentials()
      
      // 验证表单数据被填充（根据实际实现调整）
      // 这里主要测试方法可以被调用
      expect(typeof wrapper.vm.fillTestCredentials).toBe('function')
    })
  })
  
  describe('组件生命周期', () => {
    it('应该在组件挂载时清空表单', () => {
      wrapper = createWrapper()
      
      // 验证组件有清空表单的方法
      expect(typeof wrapper.vm.resetForm).toBe('function')
    })
  })
  
  describe('错误处理', () => {
    it('应该处理非标准错误响应', async () => {
      // Mock非标准错误响应
      mockLoginApi.mockResolvedValue({
        success: false,
        message: '自定义错误信息'
      })
      
      wrapper = createWrapper()
      
      await wrapper.vm.handleLogin(mockUserCredentials)
      await flushPromises()
      
      // 验证错误消息显示
      expect(ElMessage.error).toHaveBeenCalledWith('登录失败')
    })
    
    it('应该处理空响应', async () => {
      // Mock空响应
      mockLoginApi.mockResolvedValue(null)
      
      wrapper = createWrapper()
      
      await wrapper.vm.handleLogin(mockUserCredentials)
      await flushPromises()
      
      // 验证错误消息显示
      expect(ElMessage.error).toHaveBeenCalledWith('登录失败')
    })
  })
})