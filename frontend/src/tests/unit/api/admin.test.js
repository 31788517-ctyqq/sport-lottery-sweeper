import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { adminAPI } from '@/api/modules/admin.js'

// 模拟 request 模块
global.fetch = vi.fn()

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('adminAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.getItem.mockReturnValue('admin-jwt-token')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('login', () => {
    it('管理员应该成功登录', async () => {
      const mockResponse = {
        success: true,
        data: {
          admin: {
            id: 1,
            username: 'admin',
            email: 'admin@example.com',
            role: 'super_admin',
            permissions: ['*']
          },
          token: 'admin-jwt-token',
          expires_in: 7200
        }
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue(mockResponse)
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const credentials = {
        username: 'admin',
        password: 'admin123'
      }
      
      const result = await freshAdminAPI.login(credentials)
      
      expect(result.success).toBe(true)
      expect(result.data.admin.username).toBe('admin')
      expect(result.data.admin.role).toBe('super_admin')
      expect(result.data.admin.permissions).toContain('*')
    })

    it('普通用户不能管理员登录', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockRejectedValue({
            response: {
              status: 403,
              data: {
                success: false,
                message: 'Access denied: admin privileges required'
              }
            }
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      try {
        await freshAdminAPI.login({
          username: 'normaluser',
          password: 'password'
        })
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(403)
        expect(error.response.data.message).toContain('admin privileges')
      }
    })
  })

  describe('getPendingApprovals', () => {
    it('应该获取待审批用户列表', async () => {
      const mockUsers = [
        {
          id: 1,
          username: 'pending1',
          email: 'pending1@example.com',
          phone: '13800138001',
          created_at: '2024-01-22T10:00:00Z',
          registration_ip: '192.168.1.100'
        },
        {
          id: 2,
          username: 'pending2',
          email: 'pending2@example.com',
          phone: '13800138002',
          created_at: '2024-01-22T11:00:00Z',
          registration_ip: '192.168.1.101'
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockUsers,
            pagination: {
              page: 1,
              limit: 20,
              total: 2
            }
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.getPendingApprovals()
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(2)
      expect(result.data[0].username).toBe('pending1')
      expect(result.pagination.total).toBe(2)
    })
  })

  describe('approveUser', () => {
    it('应该批准用户注册申请', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            message: '用户已批准'
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.approveUser(1, '欢迎加入平台！')
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('批准')
    })

    it('应该拒绝用户注册申请', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            message: '用户申请已拒绝'
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.rejectUser(1, '资料不完整')
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('拒绝')
    })
  })

  describe('getSystemStats', () => {
    it('应该获取系统统计数据', async () => {
      const mockStats = {
        total_users: 1000,
        active_users: 850,
        total_matches: 500,
        pending_approvals: 5,
        total_bets: 10000,
        today_bets: 150,
        system_health: 'good',
        server_load: 45.2,
        database_size: '2.5GB'
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockStats
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.getSystemStats()
      
      expect(result.success).toBe(true)
      expect(result.data.total_users).toBe(1000)
      expect(result.data.active_users).toBe(850)
      expect(result.data.system_health).toBe('good')
    })
  })

  describe('getSystemLogs', () => {
    it('应该获取系统日志', async () => {
      const mockLogs = [
        {
          id: 1,
          level: 'INFO',
          message: 'User logged in',
          timestamp: '2024-01-22T10:00:00Z',
          user_id: 1
        },
        {
          id: 2,
          level: 'ERROR',
          message: 'Database connection failed',
          timestamp: '2024-01-22T09:30:00Z',
          user_id: null
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockLogs,
            pagination: {
              page: 1,
              limit: 50,
              total: 2
            }
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.getSystemLogs({ level: 'ERROR', limit: 50 })
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(2)
      expect(result.data[0].level).toBe('INFO')
      expect(result.pagination.total).toBe(2)
    })
  })

  describe('updateSettings', () => {
    it('应该更新系统设置', async () => {
      const updatedSettings = {
        registration_enabled: false,
        max_login_attempts: 3,
        maintenance_mode: false
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          put: vi.fn().mockResolvedValue({
            success: true,
            message: '设置已更新',
            data: updatedSettings
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.updateSettings(updatedSettings)
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('更新')
      expect(result.data.registration_enabled).toBe(false)
    })
  })

  describe('manageUser', () => {
    it('应该禁用用户账户', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            message: '用户已被禁用'
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.manageUser(1, 'disable', '违反平台规则')
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('禁用')
    })

    it('应该启用用户账户', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            message: '用户已启用'
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.manageUser(1, 'enable')
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('启用')
    })
  })

  describe('exportData', () => {
    it('应该导出用户数据', async () => {
      const mockBlob = new Blob(['csv,data'], { type: 'text/csv' })
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            data: mockBlob,
            headers: { 'content-disposition': 'attachment; filename="users.csv"' }
          })
        }
      }))
      
      vi.resetModules()
      const { adminAPI: freshAdminAPI } = await import('@/api/modules/admin.js')
      
      const result = await freshAdminAPI.exportData('users', { format: 'csv' })
      
      expect(result).toBeInstanceOf(Blob)
    })
  })
})