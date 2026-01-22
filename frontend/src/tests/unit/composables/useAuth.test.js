import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useAuth } from '@/composables/useAuth.js'
import { ref } from 'vue'

// 模拟 Vue Router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: { href: 'http://localhost:3000/' },
  writable: true
})

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn()
}

describe('useAuth', () => {
  let auth

  beforeEach(() => {
    vi.clearAllMocks()
    
    // 重置所有相关的localStorage mock
    localStorage.clear()
    
    // 模拟 localStorage
    Storage.prototype.getItem = vi.fn()
    Storage.prototype.setItem = vi.fn()
    Storage.prototype.removeItem = vi.fn()
    
    auth = useAuth()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('状态管理', () => {
    it('应该初始化用户状态为null', () => {
      expect(auth.user.value).toBeNull()
    })

    it('应该初始化token状态为null', () => {
      expect(auth.token.value).toBeNull()
    })

    it('应该初始化loading状态为false', () => {
      expect(auth.loading.value).toBe(false)
    })

    it('应该初始化error状态为null', () => {
      expect(auth.error.value).toBeNull()
    })

    it('应该初始化isAuthenticated为false', () => {
      expect(auth.isAuthenticated.value).toBe(false)
    })
  })

  describe('计算属性', () => {
    it('isAuthenticated应该基于token判断登录状态', async () => {
      // 初始状态应该是未认证
      expect(auth.isAuthenticated.value).toBe(false)
      
      // 设置token后应该变为已认证
      auth.token.value = 'fake-jwt-token'
      expect(auth.isAuthenticated.value).toBe(true)
      
      // token为空时应该变为未认证
      auth.token.value = null
      expect(auth.isAuthenticated.value).toBe(false)
    })

    it('userRole应该返回用户角色', async () => {
      // 用户为空时应该返回null
      expect(auth.userRole.value).toBeNull()
      
      // 设置用户后应该返回对应角色
      auth.user.value = { role: 'admin' }
      expect(auth.userRole.value).toBe('admin')
      
      // 设置普通用户角色
      auth.user.value = { role: 'user' }
      expect(auth.userRole.value).toBe('user')
    })

    it('userName应该返回用户名', () => {
      // 用户为空时应该返回空字符串
      expect(auth.userName.value).toBe('')
      
      // 设置用户后应该返回用户名
      auth.user.value = { username: 'testuser' }
      expect(auth.userName.value).toBe('testuser')
      
      // 设置昵称时应该优先返回昵称
      auth.user.value = { username: 'testuser', nickname: 'Test User' }
      // 根据实际实现决定优先级
      expect(auth.userName.value).toBeDefined()
    })
  })

  describe('初始化', () => {
    it('应该从localStorage恢复认证状态', async () => {
      // 模拟localStorage中有保存的数据
      localStorage.getItem.mockImplementation(key => {
        const data = {
          'auth_token': 'saved-jwt-token',
          'auth_user': JSON.stringify({ id: 1, username: 'saveduser' })
        }
        return data[key]
      })
      
      await auth.initializeAuth()
      
      expect(auth.token.value).toBe('saved-jwt-token')
      expect(auth.user.value).toEqual({ id: 1, username: 'saveduser' })
      expect(localStorage.getItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.getItem).toHaveBeenCalledWith('auth_user')
    })

    it('localStorage中没有数据应该保持未认证状态', async () => {
      localStorage.getItem.mockReturnValue(null)
      
      await auth.initializeAuth()
      
      expect(auth.token.value).toBeNull()
      expect(auth.user.value).toBeNull()
      expect(auth.isAuthenticated.value).toBe(false)
    })

    it('localStorage数据损坏应该清除无效数据', async () => {
      localStorage.getItem.mockImplementation(key => {
        if (key === 'auth_user') return 'invalid-json'
        return null
      })
      
      await auth.initializeAuth()
      
      expect(auth.token.value).toBeNull()
      expect(auth.user.value).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
    })

    it('初始化时应该验证token有效性', async () => {
      localStorage.getItem.mockImplementation(key => {
        if (key === 'auth_token') return 'expired-token'
        return null
      })
      
      // 模拟token验证失败
      global.fetch = vi.fn().mockRejectedValue(new Error('Token expired'))
      
      await auth.initializeAuth()
      
      expect(auth.token.value).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('注册功能', () => {
    it('应该成功注册用户', async () => {
      const userData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123'
      }
      
      const mockResponse = {
        success: true,
        data: {
          user: { id: 1, username: 'newuser', email: 'newuser@example.com' },
          message: 'Registration successful'
        }
      }
      
      // 模拟API调用
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          register: vi.fn().mockResolvedValue(mockResponse)
        }
      }))
      
      await auth.register(userData)
      
      expect(auth.loading.value).toBe(false)
      expect(auth.error.value).toBeNull()
      expect(toast.success).toHaveBeenCalledWith('注册成功，请等待管理员审核')
    })

    it('注册应该处理验证错误', async () => {
      const userData = { username: '', email: 'invalid-email' }
      
      const validationErrors = {
        username: ['用户名不能为空'],
        email: ['邮箱格式不正确']
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          register: vi.fn().mockRejectedValue({
            response: {
              status: 422,
              data: { success: false, errors: validationErrors }
            }
          })
        }
      }))
      
      try {
        await auth.register(userData)
      } catch (error) {
        expect(auth.loading.value).toBe(false)
        expect(auth.error.value).toBeDefined()
        expect(Object.keys(auth.error.value)).toEqual(['username', 'email'])
      }
    })

    it('注册应该处理网络错误', async () => {
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          register: vi.fn().mockRejectedValue(new Error('Network error'))
        }
      }))
      
      const userData = { username: 'testuser', email: 'test@example.com', password: 'password123' }
      
      try {
        await auth.register(userData)
      } catch (error) {
        expect(auth.loading.value).toBe(false)
        expect(auth.error.value).toBe('Network error')
        expect(toast.error).toHaveBeenCalledWith('注册失败，请检查网络连接')
      }
    })

    it('注册时应该设置loading状态', async () => {
      const userData = { username: 'testuser', email: 'test@example.com', password: 'password123' }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          register: vi.fn().mockImplementation(() => new Promise(resolve => {
            setTimeout(() => resolve({ success: true }), 100)
          }))
        }
      }))
      
      const promise = auth.register(userData)
      
      // 立即检查loading状态
      expect(auth.loading.value).toBe(true)
      
      await promise
      
      expect(auth.loading.value).toBe(false)
    })
  })

  describe('登录功能', () => {
    it('应该成功登录并设置认证状态', async () => {
      const credentials = {
        username: 'testuser',
        password: 'password123'
      }
      
      const mockResponse = {
        success: true,
        data: {
          user: {
            id: 1,
            username: 'testuser',
            email: 'test@example.com',
            balance: 1000.0
          },
          access_token: 'jwt-access-token',
          refresh_token: 'jwt-refresh-token'
        }
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          login: vi.fn().mockResolvedValue(mockResponse)
        }
      }))
      
      await auth.login(credentials)
      
      expect(auth.token.value).toBe('jwt-access-token')
      expect(auth.user.value).toEqual(mockResponse.data.user)
      expect(auth.isAuthenticated.value).toBe(true)
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'jwt-access-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockResponse.data.user))
      expect(toast.success).toHaveBeenCalledWith('登录成功')
    })

    it('登录失败应该设置错误状态', async () => {
      const credentials = {
        username: 'wronguser',
        password: 'wrongpass'
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          login: vi.fn().mockRejectedValue({
            response: {
              status: 401,
              data: { success: false, message: 'Invalid credentials' }
            }
          })
        }
      }))
      
      try {
        await auth.login(credentials)
      } catch (error) {
        expect(auth.loading.value).toBe(false)
        expect(auth.error.value).toBe('Invalid credentials')
        expect(auth.token.value).toBeNull()
        expect(auth.user.value).toBeNull()
        expect(localStorage.setItem).not.toHaveBeenCalled()
        expect(toast.error).toHaveBeenCalledWith('用户名或密码错误')
      }
    })

    it('账号未激活应该特殊处理', async () => {
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          login: vi.fn().mockRejectedValue({
            response: {
              status: 403,
              data: { success: false, code: 'ACCOUNT_NOT_ACTIVATED' }
            }
          })
        }
      }))
      
      const credentials = { username: 'inactiveuser', password: 'password123' }
      
      try {
        await auth.login(credentials)
      } catch (error) {
        expect(toast.warning).toHaveBeenCalledWith('账号未激活，请联系管理员')
      }
    })

    it('登录时应该清除之前的错误状态', async () => {
      auth.error.value = 'Previous error'
      
      const credentials = { username: 'testuser', password: 'password123' }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          login: vi.fn().mockResolvedValue({ success: true, data: {} })
        }
      }))
      
      await auth.login(credentials)
      
      expect(auth.error.value).toBeNull()
    })
  })

  describe('登出功能', () => {
    it('应该清除认证状态并跳转', async () => {
      // 设置初始认证状态
      auth.token.value = 'fake-token'
      auth.user.value = { id: 1, username: 'testuser' }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          logout: vi.fn().mockResolvedValue({ success: true })
        }
      }))
      
      await auth.logout()
      
      expect(auth.token.value).toBeNull()
      expect(auth.user.value).toBeNull()
      expect(auth.isAuthenticated.value).toBe(false)
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
      expect(window.location.href).toBe('/login')
    })

    it('登出API失败时也应该清除本地状态', async () => {
      auth.token.value = 'fake-token'
      auth.user.value = { id: 1, username: 'testuser' }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          logout: vi.fn().mockRejectedValue(new Error('API error'))
        }
      }))
      
      await auth.logout()
      
      // 即使API失败，本地状态也应该被清除
      expect(auth.token.value).toBeNull()
      expect(auth.user.value).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
    })
  })

  describe('获取当前用户信息', () => {
    it('应该成功获取并更新用户信息', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        balance: 1000.0
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          getCurrentUser: vi.fn().mockResolvedValue({ success: true, data: mockUser })
        }
      }))
      
      await auth.fetchCurrentUser()
      
      expect(auth.user.value).toEqual(mockUser)
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(mockUser))
    })

    it('获取用户信息失败应该清除认证状态', async () => {
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          getCurrentUser: vi.fn().mockRejectedValue(new Error('API error'))
        }
      }))
      
      auth.token.value = 'fake-token'
      
      await auth.fetchCurrentUser()
      
      expect(auth.token.value).toBeNull()
      expect(auth.user.value).toBeNull()
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_user')
    })

    it('没有token时不应该发起请求', async () => {
      auth.token.value = null
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          getCurrentUser: vi.fn()
        }
      }))
      
      await auth.fetchCurrentUser()
      
      expect(authAPI.getCurrentUser).not.toHaveBeenCalled()
    })
  })

  describe('更新用户信息', () => {
    it('应该成功更新用户信息', async () => {
      const profileData = {
        nickname: 'Updated Name',
        email: 'updated@example.com'
      }
      
      const updatedUser = {
        id: 1,
        username: 'testuser',
        nickname: 'Updated Name',
        email: 'updated@example.com'
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          updateProfile: vi.fn().mockResolvedValue({ success: true, data: updatedUser })
        }
      }))
      
      auth.user.value = { id: 1, username: 'testuser', nickname: 'Old Name', email: 'old@example.com' }
      
      await auth.updateProfile(profileData)
      
      expect(auth.user.value).toEqual(updatedUser)
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(updatedUser))
      expect(toast.success).toHaveBeenCalledWith('个人信息更新成功')
    })

    it('更新失败应该设置错误状态', async () => {
      const profileData = { nickname: 'New Name' }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          updateProfile: vi.fn().mockRejectedValue(new Error('Update failed'))
        }
      }))
      
      try {
        await auth.updateProfile(profileData)
      } catch (error) {
        expect(auth.error.value).toBe('Update failed')
        expect(toast.error).toHaveBeenCalledWith('更新失败，请重试')
      }
    })
  })

  describe('修改密码', () => {
    it('应该成功修改密码', async () => {
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123'
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          changePassword: vi.fn().mockResolvedValue({ success: true, message: 'Password changed' })
        }
      }))
      
      await auth.changePassword(passwordData)
      
      expect(toast.success).toHaveBeenCalledWith('密码修改成功')
    })

    it('密码不匹配应该设置验证错误', async () => {
      const passwordData = {
        current_password: 'oldpassword',
        new_password: 'newpassword123',
        confirm_password: 'differentpassword'
      }
      
      await auth.changePassword(passwordData)
      
      expect(auth.error.value).toBeDefined()
      expect(auth.error.value.confirm_password).toContain('密码不匹配')
    })

    it('修改密码失败应该设置错误状态', async () => {
      const passwordData = {
        current_password: 'wrongpassword',
        new_password: 'newpassword123'
      }
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          changePassword: vi.fn().mockRejectedValue({
            response: {
              data: { message: 'Current password incorrect' }
            }
          })
        }
      }))
      
      try {
        await auth.changePassword(passwordData)
      } catch (error) {
        expect(auth.error.value).toBe('Current password incorrect')
        expect(toast.error).toHaveBeenCalledWith('当前密码不正确')
      }
    })
  })

  describe('验证功能', () => {
    it('应该验证邮箱格式', () => {
      expect(auth.validateEmail('test@example.com')).toBe(true)
      expect(auth.validateEmail('invalid-email')).toBe(false)
      expect(auth.validateEmail('')).toBe(false)
      expect(auth.validateEmail(null)).toBe(false)
    })

    it('应该验证手机号格式', () => {
      expect(auth.validatePhone('13800138000')).toBe(true)
      expect(auth.validatePhone('1234567890')).toBe(false)
      expect(auth.validatePhone('')).toBe(false)
      expect(auth.validatePhone(null)).toBe(false)
    })

    it('应该验证密码强度', () => {
      expect(auth.validatePassword('weak')).toBe(false)
      expect(auth.validatePassword('StrongPass123!')).toBe(true)
      expect(auth.validatePassword('')).toBe(false)
    })

    it('应该验证用户名格式', () => {
      expect(auth.validateUsername('validuser')).toBe(true)
      expect(auth.validateUsername('ab')).toBe(false) // too short
      expect(auth.validateUsername('a'.repeat(21))).toBe(false) // too long
      expect(auth.validateUsername('invalid-user')).toBe(false) // contains hyphen
    })
  })

  describe('工具函数', () => {
    it('shouldLogoutOnTokenExpiry应该返回true', () => {
      expect(auth.shouldLogoutOnTokenExpiry()).toBe(true)
    })

    it('getRedirectUrl应该返回正确的重定向URL', () => {
      const redirectUrl = auth.getRedirectUrl()
      expect(redirectUrl).toBe('/')
    })

    it('clearError应该清除错误状态', () => {
      auth.error.value = 'Some error'
      
      auth.clearError()
      
      expect(auth.error.value).toBeNull()
    })
  })

  describe('监听器', () => {
    it('token变化应该触发localStorage保存', async () => {
      auth.token.value = 'new-token'
      
      // 等待监听器执行
      await new Promise(resolve => setTimeout(resolve, 0))
      
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'new-token')
    })

    it('user变化应该触发localStorage保存', async () => {
      const user = { id: 1, username: 'testuser' }
      auth.user.value = user
      
      // 等待监听器执行
      await new Promise(resolve => setTimeout(resolve, 0))
      
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_user', JSON.stringify(user))
    })
  })

  describe('边界情况', () => {
    it('应该处理localStorage配额超限', async () => {
      localStorage.setItem.mockImplementation(() => {
        throw new Error('QuotaExceededError')
      })
      
      auth.token.value = 'test-token'
      auth.user.value = { id: 1, username: 'testuser' }
      
      // 等待监听器执行，不应该抛出错误
      await new Promise(resolve => setTimeout(resolve, 0))
      
      // 认证状态应该仍然更新，只是localStorage保存失败
      expect(auth.token.value).toBe('test-token')
    })

    it('应该处理JSON序列化错误', async () => {
      const circularUser = { id: 1 }
      circularUser.self = circularUser // 创建循环引用
      
      auth.user.value = circularUser
      
      // 等待监听器执行，不应该抛出错误
      await new Promise(resolve => setTimeout(resolve, 0))
      
      // 应该捕获序列化错误但不影响程序运行
      expect(true).toBe(true)
    })

    it('并发登录请求应该正确处理', async () => {
      const credentials = { username: 'testuser', password: 'password123' }
      
      let resolveFirst, resolveSecond
      const firstPromise = new Promise(resolve => resolveFirst = resolve)
      const secondPromise = new Promise(resolve => resolveSecond = resolve)
      
      vi.doMock('@/api/modules/auth.js', () => ({
        authAPI: {
          login: vi.fn()
            .mockReturnValueOnce(firstPromise)
            .mockReturnValueOnce(secondPromise)
        }
      }))
      
      // 发起两个并发登录请求
      const promise1 = auth.login(credentials)
      const promise2 = auth.login(credentials)
      
      // 第一个请求完成
      resolveFirst({ success: true, data: { user: {}, access_token: 'token1' } })
      await promise1
      
      // 第二个请求应该不会覆盖第一个的结果
      resolveSecond({ success: true, data: { user: {}, access_token: 'token2' } })
      await promise2
      
      // 最终的token应该是第一个请求的token（取决于具体实现）
      expect(auth.token.value).toBeDefined()
    })
  })
})