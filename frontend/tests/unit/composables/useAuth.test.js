// frontend/tests/unit/composables/useAuth.test.js
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { useAuth } from '@/composables/useAuth.js'
import { useAuthStore } from '@/stores/auth.js'
import { ElMessage, ElMessageBox } from 'element-plus'

// Mock依赖
vi.mock('@/stores/auth.js', () => ({
  useAuthStore: vi.fn()
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    replace: vi.fn()
  })
}))

describe('useAuth', () => {
  let mockAuthStore
  let mockRouter

  beforeEach(() => {
    // 重置所有mock
    vi.clearAllMocks()
    
    // Mock auth store
    mockAuthStore = {
      isAuthenticated: ref(false),
      user: ref(null),
      isLoading: ref(false),
      error: ref(null),
      login: vi.fn(),
      logout: vi.fn(),
      register: vi.fn(),
      forgotPassword: vi.fn(),
      resetPassword: vi.fn(),
      updateProfile: vi.fn(),
      clearError: vi.fn()
    }
    
    useAuthStore.mockReturnValue(mockAuthStore)
    
    // Mock router
    mockRouter = {
      push: vi.fn(),
      replace: vi.fn()
    }
    
    // Mock window.location
    Object.defineProperty(window, 'location', {
      value: { href: '' },
      writable: true
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('登录功能', () => {
    it('应该调用登录方法并处理成功响应', async () => {
      const { login } = useAuth()
      const credentials = { email: 'test@example.com', password: 'password' }
      const mockResponse = { success: true, data: { token: 'jwt-token' } }
      
      mockAuthStore.login.mockResolvedValue(mockResponse)

      const result = await login(credentials)

      expect(mockAuthStore.login).toHaveBeenCalledWith(credentials)
      expect(result).toEqual(mockResponse)
      expect(ElMessage.success).toHaveBeenCalledWith('登录成功')
    })

    it('应该处理登录失败', async () => {
      const { login } = useAuth()
      const credentials = { email: 'test@example.com', password: 'wrong' }
      const mockError = new Error('Invalid credentials')
      
      mockAuthStore.login.mockRejectedValue(mockError)
      mockAuthStore.error.value = '用户名或密码错误'

      await expect(login(credentials)).rejects.toThrow('Invalid credentials')
      expect(ElMessage.error).toHaveBeenCalledWith('用户名或密码错误')
    })

    it('应该处理网络错误', async () => {
      const { login } = useAuth()
      const credentials = { email: 'test@example.com', password: 'password' }
      
      mockAuthStore.login.mockRejectedValue(new Error('Network error'))

      await expect(login(credentials)).rejects.toThrow('Network error')
      expect(ElMessage.error).toHaveBeenCalledWith('网络连接失败，请检查网络设置')
    })
  })

  describe('注册功能', () => {
    it('应该调用注册方法并处理成功响应', async () => {
      const { register } = useAuth()
      const userData = { 
        email: 'test@example.com', 
        password: 'Password123!', 
        confirmPassword: 'Password123!',
        captcha: '123456'
      }
      const mockResponse = { success: true, message: '注册成功' }
      
      mockAuthStore.register.mockResolvedValue(mockResponse)

      const result = await register(userData)

      expect(mockAuthStore.register).toHaveBeenCalledWith(userData)
      expect(result).toEqual(mockResponse)
      expect(ElMessage.success).toHaveBeenCalledWith('注册成功')
    })

    it('应该处理注册失败', async () => {
      const { register } = useAuth()
      const userData = { 
        email: 'existing@example.com', 
        password: 'Password123!', 
        confirmPassword: 'Password123!',
        captcha: '123456'
      }
      
      mockAuthStore.register.mockRejectedValue(new Error('Registration failed'))
      mockAuthStore.error.value = '该邮箱已注册'

      await expect(register(userData)).rejects.toThrow('Registration failed')
      expect(ElMessage.error).toHaveBeenCalledWith('该邮箱已注册')
    })
  })

  describe('登出功能', () => {
    it('应该调用登出方法并显示确认对话框', async () => {
      const { logout } = useAuth()
      
      ElMessageBox.confirm.mockResolvedValue('confirm')
      mockAuthStore.logout.mockResolvedValue({ success: true })

      await logout()

      expect(ElMessageBox.confirm).toHaveBeenCalledWith(
        '确定要退出登录吗？',
        '提示',
        { type: 'warning' }
      )
      expect(mockAuthStore.logout).toHaveBeenCalled()
      expect(ElMessage.success).toHaveBeenCalledWith('已退出登录')
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('应该在用户取消登出时中止操作', async () => {
      const { logout } = useAuth()
      
      ElMessageBox.confirm.mockResolvedValue('cancel')
      mockAuthStore.logout.mockClear()

      await logout()

      expect(mockAuthStore.logout).not.toHaveBeenCalled()
      expect(ElMessage.success).not.toHaveBeenCalled()
    })

    it('应该处理登出失败', async () => {
      const { logout } = useAuth()
      
      ElMessageBox.confirm.mockResolvedValue('confirm')
      mockAuthStore.logout.mockRejectedValue(new Error('Logout failed'))

      await logout()

      expect(ElMessage.error).toHaveBeenCalledWith('退出登录失败')
    })
  })

  describe('忘记密码功能', () => {
    it('应该发送忘记密码请求', async () => {
      const { forgotPassword } = useAuth()
      const email = 'test@example.com'
      const mockResponse = { success: true, message: '重置邮件已发送' }
      
      mockAuthStore.forgotPassword.mockResolvedValue(mockResponse)

      const result = await forgotPassword(email)

      expect(mockAuthStore.forgotPassword).toHaveBeenCalledWith(email)
      expect(result).toEqual(mockResponse)
      expect(ElMessage.success).toHaveBeenCalledWith('重置邮件已发送')
    })

    it('应该处理忘记密码失败', async () => {
      const { forgotPassword } = useAuth()
      const email = 'nonexistent@example.com'
      
      mockAuthStore.forgotPassword.mockRejectedValue(new Error('User not found'))
      mockAuthStore.error.value = '该邮箱未注册'

      await expect(forgotPassword(email)).rejects.toThrow('User not found')
      expect(ElMessage.error).toHaveBeenCalledWith('该邮箱未注册')
    })
  })

  describe('重置密码功能', () => {
    it('应该重置密码', async () => {
      const { resetPassword } = useAuth()
      const resetData = {
        token: 'reset-token',
        password: 'NewPassword123!',
        confirmPassword: 'NewPassword123!'
      }
      const mockResponse = { success: true, message: '密码重置成功' }
      
      mockAuthStore.resetPassword.mockResolvedValue(mockResponse)

      const result = await resetPassword(resetData)

      expect(mockAuthStore.resetPassword).toHaveBeenCalledWith(resetData)
      expect(result).toEqual(mockResponse)
      expect(ElMessage.success).toHaveBeenCalledWith('密码重置成功')
    })
  })

  describe('更新用户信息功能', () => {
    it('应该更新用户信息', async () => {
      const { updateProfile } = useAuth()
      const profileData = { nickname: 'New Name', phone: '13800138000' }
      const mockResponse = { success: true, data: { nickname: 'New Name' } }
      
      mockAuthStore.updateProfile.mockResolvedValue(mockResponse)

      const result = await updateProfile(profileData)

      expect(mockAuthStore.updateProfile).toHaveBeenCalledWith(profileData)
      expect(result).toEqual(mockResponse)
      expect(ElMessage.success).toHaveBeenCalledWith('个人信息更新成功')
    })
  })

  describe('权限检查功能', () => {
    it('应该检查用户是否已认证', () => {
      const { isAuthenticated } = useAuth()
      
      mockAuthStore.isAuthenticated.value = true
      expect(isAuthenticated()).toBe(true)
      
      mockAuthStore.isAuthenticated.value = false
      expect(isAuthenticated()).toBe(false)
    })

    it('应该检查特定角色权限', () => {
      const { hasRole } = useAuth()
      
      mockAuthStore.user.value = { role: 'admin' }
      expect(hasRole('admin')).toBe(true)
      expect(hasRole('user')).toBe(false)
      
      mockAuthStore.user.value = { role: 'user' }
      expect(hasRole('user')).toBe(true)
      
      mockAuthStore.user.value = null
      expect(hasRole('admin')).toBe(false)
    })

    it('应该检查管理员权限', () => {
      const { isAdmin } = useAuth()
      
      mockAuthStore.user.value = { role: 'admin' }
      expect(isAdmin()).toBe(true)
      
      mockAuthStore.user.value = { role: 'user' }
      expect(isAdmin()).toBe(false)
      
      mockAuthStore.user.value = null
      expect(isAdmin()).toBe(false)
    })
  })

  describe('重定向功能', () => {
    it('应该重定向到登录页', () => {
      const { redirectToLogin } = useAuth()
      
      redirectToLogin()
      expect(mockRouter.push).toHaveBeenCalledWith('/login')
    })

    it('应该重定向到首页', () => {
      const { redirectToHome } = useAuth()
      
      redirectToHome()
      expect(mockRouter.push).toHaveBeenCalledWith('/')
    })

    it('应该重定向到仪表板', () => {
      const { redirectToDashboard } = useAuth()
      
      redirectToDashboard()
      expect(mockRouter.push).toHaveBeenCalledWith('/dashboard')
    })
  })

  describe('令牌管理功能', () => {
    it('应该获取本地存储的token', () => {
      const { getToken } = useAuth()
      
      // Mock localStorage
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      getItemSpy.mockReturnValue('stored-token')
      
      const token = getToken()
      
      expect(getItemSpy).toHaveBeenCalledWith('auth_token')
      expect(token).toBe('stored-token')
      
      getItemSpy.mockRestore()
    })

    it('应该检查token是否存在', () => {
      const { hasToken } = useAuth()
      
      const getItemSpy = vi.spyOn(Storage.prototype, 'getItem')
      
      getItemSpy.mockReturnValue('some-token')
      expect(hasToken()).toBe(true)
      
      getItemSpy.mockReturnValue(null)
      expect(hasToken()).toBe(false)
      
      getItemSpy.mockRestore()
    })
  })

  describe('错误处理功能', () => {
    it('应该清除错误信息', () => {
      const { clearError } = useAuth()
      
      clearError()
      expect(mockAuthStore.clearError).toHaveBeenCalled()
    })

    it('应该检查是否有错误', () => {
      const { hasError } = useAuth()
      
      mockAuthStore.error.value = 'Some error'
      expect(hasError()).toBe(true)
      
      mockAuthStore.error.value = null
      expect(hasError()).toBe(false)
    })
  })

  describe('边界情况和错误处理', () => {
    it('应该处理Element Plus MessageBox错误', async () => {
      const { logout } = useAuth()
      
      ElMessageBox.confirm.mockRejectedValue(new Error('Dialog cancelled'))

      await logout()

      // 应该优雅地处理错误，不抛出未捕获异常
      expect(true).toBe(true)
    })

    it('应该处理localStorage不可用的情况', () => {
      const { getToken } = useAuth()
      
      // Mock localStorage为null
      const originalLocalStorage = window.localStorage
      Object.defineProperty(window, 'localStorage', { value: null, writable: true })
      
      // 应该优雅处理，不抛出错误
      expect(() => getToken()).not.toThrow()
      
      // 恢复localStorage
      window.localStorage = originalLocalStorage
    })

    it('应该在store方法不存在时抛出错误', () => {
      useAuthStore.mockReturnValue({})
      
      const { login } = useAuth()
      
      expect(() => login({ email: 'test@example.com', password: 'password' }))
        .toThrow('login method is not defined in auth store')
    })
  })

  describe('响应式状态', () => {
    it('应该返回响应式的状态值', () => {
      const { isAuthenticated, user, isLoading, error } = useAuth()
      
      // 这些应该是ref对象
      expect(isAuthenticated.value).toBeDefined()
      expect(user.value).toBeDefined()
      expect(isLoading.value).toBeDefined()
      expect(error.value).toBeDefined()
    })
  })
})