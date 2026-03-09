// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { authAPI } from '@/api/modules/auth.js'

// 模拟 request 模块
global.fetch = vi.fn()

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// 模拟 router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

describe('authAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.getItem.mockReturnValue(null)
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('register', () => {
    it('应该成功注册用户', async () => {
      const mockResponse = {
        success: true,
        data,
          message: '注册成功，请等待管理员审核'
        }
      }
      
      // Mock the actual API call
      vi.doMock('../../utils/request.js', () => ({
        default
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const userData = {
        username: 'testuser',
        email: 'test@example.com',
        phone: '13800138000',
        password: 'password123',
        confirm_password: 'password123'
      }
      
      const result = await freshAuthAPI.register(userData)
      
      expect(result.success).toBe(true)
      expect(result.data.user.username).toBe('testuser')
      expect(result.data.user.is_active).toBe(false)
    })

    it('注册应该验证必填字段', async () => {
      const validationErrors = {
        username: ['用户名不能为空'],
        email: ['邮箱格式不正确']
      }
      
      vi.doMock('../../utils/request.js', () => ({
        default
            }
          })
        }
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      try {
        await freshAuthAPI.register({})
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(422)
        expect(error.response.data.errors).toEqual(validationErrors)
      }
    })
  })

  describe('login', () => {
    it('应该成功登录并返回用户信息和token', async () => {
      const mockResponse = {
        success: true,
        data,
          access_token: 'jwt-access-token',
          refresh_token: 'jwt-refresh-token'
        }
      }
      
      vi.doMock('../../utils/request.js', () => ({
        default
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const credentials = {
        username: 'testuser',
        password: 'password123'
      }
      
      const result = await freshAuthAPI.login(credentials)
      
      expect(result.success).toBe(true)
      expect(result.data.user.username).toBe('testuser')
      expect(result.data.access_token).toBe('jwt-access-token')
    })

    it('登录失败应该返回错误信息', async () => {
      vi.doMock('../../utils/request.js', () => ({
        default
            }
          })
        }
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      try {
        await freshAuthAPI.login({
          username: 'wronguser',
          password: 'wrongpass'
        })
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(401)
      }
    })
  })

  describe('logout', () => {
    it('应该成功登出', async () => {
      const mockResponse = {
        success: true,
        message: 'Logout successful'
      }
      
      vi.doMock('../../utils/request.js', () => ({
        default
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const result = await freshAuthAPI.logout()
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('successful')
    })
  })

  describe('getCurrentUser', () => {
    it('应该获取当前用户信息', async () => {
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
        balance: 1000.0
      }
      
      vi.doMock('../../utils/request.js', () => ({
        default)
        }
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const result = await freshAuthAPI.getCurrentUser()
      
      expect(result.success).toBe(true)
      expect(result.data.username).toBe('testuser')
    })
  })

  describe('updateProfile', () => {
    it('应该更新用户基本信息', async () => {
      const updatedUser = {
        id: 1,
        username: 'testuser',
        email: 'newemail@example.com',
        phone: '13900139000'
      }
      
      vi.doMock('../../utils/request.js', () => ({
        default)
        }
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const profileData = {
        email: 'newemail@example.com',
        phone: '13900139000'
      }
      
      const result = await freshAuthAPI.updateProfile(profileData)
      
      expect(result.success).toBe(true)
      expect(result.data.email).toBe('newemail@example.com')
    })
  })

  describe('changePassword', () => {
    it('应该成功修改密码', async () => {
      vi.doMock('../../utils/request.js', () => ({
        default)
        }
      }))
      
      vi.resetModules()
      const { authAPI: freshAuthAPI } = await import('../../api/modules/auth.js')
      
      const passwordData = {
        current_password: 'oldpassword123',
        new_password: 'newpassword123'
      }
      
      const result = await freshAuthAPI.changePassword(passwordData)
      
      expect(result.success).toBe(true)
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
