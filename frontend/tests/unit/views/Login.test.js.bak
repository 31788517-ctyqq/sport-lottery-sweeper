import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Login from '@/views/Login.vue'

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
  it('应该能够正确渲染登录表单', () => {
    const wrapper = mount(Login, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-icon': true,
          'router-link': true
        }
      }
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.login-header h2').exists()).toBe(true)
  })

  it('应该在登录成功后跳转到仪表板', async () => {
    // Mock successful login response
    mockLoginApi.mockResolvedValue({
      data: {
        code: 200,
        message: '登录成功',
        data: {
          access_token: 'mock-token'
        }
      }
    })

    const wrapper = mount(Login, {
      global: {
        stubs: {
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-icon': true,
          'router-link': true
        }
      }
    })

    // Trigger login (simulate the login process)
    await wrapper.vm.handleLogin({ username: 'admin', password: 'password' })

    // Check if navigation happened
    expect(mockRouter.push).toHaveBeenCalledWith('/admin/dashboard')
  })
})
