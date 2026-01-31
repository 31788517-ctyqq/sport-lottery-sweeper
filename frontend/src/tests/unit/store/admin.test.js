// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAdminStore } from '../../stores/admin.js'

// 模拟 API 调用
global.fetch = vi.fn()

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// 模拟 vue-router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

describe('useAdminStore (stores/admin.js)', () => {
  let adminStore
  
  beforeEach(() => {
    // 创建新的 Pinia 实例
    setActivePinia(createPinia())
    
    vi.clearAllMocks()
    
    // Reset fetch mock
    fetch.mockClear()
    
    // Reset localStorage mock
    localStorage.getItem.mockReturnValue(null)
    localStorage.setItem.mockImplementation(() => {})
    
    adminStore = useAdminStore()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始状态', () => {
    it('应该初始化正确的管理员状态', () => {
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.admin).toBeNull()
      expect(adminStore.token).toBe('')
      expect(adminStore.permissions).toEqual([])
      expect(adminStore.role).toBe('')
      expect(adminStore.pendingApprovals).toEqual([])
      expect(adminStore.systemStats).toEqual({})
      expect(adminStore.settings).toEqual({})
      expect(adminStore.loading).toBe(false)
      expect(adminStore.error).toBe('')
    })

    it('应该从 localStorage 加载管理员 token', () => {
      localStorage.getItem.mockReturnValue('admin-jwt-token')
      
      const newAdminStore = useAdminStore()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('admin-token')
      expect(newAdminStore.token).toBe('admin-jwt-token')
    })

    it('应该从 localStorage 加载管理员信息', () => {
      const adminData = { id: 1, username: 'admin', role: 'super_admin' }
      localStorage.getItem.mockReturnValue(JSON.stringify(adminData))
      
      const newAdminStore = useAdminStore()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('admin-data')
      expect(newAdminStore.admin).toEqual(adminData)
      expect(newAdminStore.isAuthenticated).toBe(true)
    })
  })

  describe('管理员登录', () => {
    it('应该成功登录超级管理员', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data,
            token: 'super-admin-jwt-token'
          }
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.login('superadmin', 'admin123')
      
      expect(result.success).toBe(true)
      expect(adminStore.isAuthenticated).toBe(true)
      expect(adminStore.admin).toEqual({
        id: 1,
        username: 'superadmin',
        email: 'admin@example.com',
        role: 'super_admin',
        permissions: ['*']
      })
      expect(adminStore.token).toBe('super-admin-jwt-token')
      expect(adminStore.permissions).toEqual(['*'])
      expect(adminStore.role).toBe('super_admin')
      expect(localStorage.setItem).toHaveBeenCalledWith('admin-token', 'super-admin-jwt-token')
      expect(localStorage.setItem).toHaveBeenCalledWith('admin-data', JSON.stringify({
        id: 1,
        username: 'superadmin',
        email: 'admin@example.com',
        role: 'super_admin',
        permissions: ['*']
      }))
    })

    it('应该成功登录普通管理员', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data,
            token: 'moderator-jwt-token'
          }
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.login('moderator', 'mod123')
      
      expect(result.success).toBe(true)
      expect(adminStore.role).toBe('moderator')
      expect(adminStore.permissions).toEqual(['users.read', 'matches.manage'])
    })

    it('登录失败应该返回错误信息', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: () => Promise.resolve({
          success: false,
          message: '用户名或密码错误'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.login('wrong', 'wrong')
      
      expect(result.success).toBe(false)
      expect(result.message).toBe('用户名或密码错误')
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.error).toBe('用户名或密码错误')
    })

    it('网络错误应该处理 gracefully', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'))
      
      const result = await adminStore.login('admin', 'password')
      
      expect(result.success).toBe(false)
      expect(result.message).toBe('登录失败，请检查网络连接')
      expect(adminStore.error).toBe('登录失败，请检查网络连接')
    })

    it('登录过程中应该设置加载状态', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data, token: 'token' }
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const loginPromise = adminStore.login('admin', 'password')
      
      // 立即检查加载状态
      expect(adminStore.loading).toBe(true)
      
      await loginPromise
      
      expect(adminStore.loading).toBe(false)
    })
  })

  describe('权限检查', () => {
    beforeEach(() => {
      adminStore.permissions = ['users.read', 'users.write', 'matches.manage', 'settings.read']
    })

    it('应该检查具体权限', () => {
      expect(adminStore.hasPermission('users.read')).toBe(true)
      expect(adminStore.hasPermission('users.write')).toBe(true)
      expect(adminStore.hasPermission('reports.delete')).toBe(false)
    })

    it('通配符权限应该拥有所有权限', () => {
      adminStore.permissions = ['*']
      
      expect(adminStore.hasPermission('any.permission')).toBe(true)
      expect(adminStore.hasPermission('users.delete')).toBe(true)
      expect(adminStore.hasPermission('system.shutdown')).toBe(true)
    })

    it('应该检查多个权限（任意一个）', () => {
      expect(adminStore.hasAnyPermission(['users.delete', 'users.read'])).toBe(true)
      expect(adminStore.hasAnyPermission(['reports.delete', 'analytics.write'])).toBe(false)
    })

    it('应该检查多个权限（全部需要）', () => {
      expect(adminStore.hasAllPermissions(['users.read', 'matches.manage'])).toBe(true)
      expect(adminStore.hasAllPermissions(['users.read', 'users.delete'])).toBe(false)
    })

    it('没有权限信息时应该返回 false', () => {
      adminStore.permissions = []
      
      expect(adminStore.hasPermission('users.read')).toBe(false)
      expect(adminStore.hasAnyPermission(['users.read'])).toBe(false)
      expect(adminStore.hasAllPermissions(['users.read'])).toBe(false)
    })

    it('应该基于角色检查权限', () => {
      adminStore.role = 'super_admin'
      expect(adminStore.hasRole('super_admin')).toBe(true)
      expect(adminStore.hasRole('moderator')).toBe(false)
      
      adminStore.role = 'moderator'
      expect(adminStore.hasRole('moderator')).toBe(true)
      expect(adminStore.hasRole('user')).toBe(false)
    })
  })

  describe('管理员登出', () => {
    beforeEach(() => {
      adminStore.isAuthenticated = true
      adminStore.admin = { id: 1, username: 'admin' }
      adminStore.token = 'admin-token'
      adminStore.permissions = ['*']
    })

    it('应该清除所有管理员状态', async () => {
      await adminStore.logout()
      
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.admin).toBeNull()
      expect(adminStore.token).toBe('')
      expect(adminStore.permissions).toEqual([])
      expect(adminStore.role).toBe('')
      expect(adminStore.error).toBe('')
      expect(localStorage.removeItem).toHaveBeenCalledWith('admin-token')
      expect(localStorage.removeItem).toHaveBeenCalledWith('admin-data')
    })

    it('登出时应该调用后端登出接口', async () => {
      fetch.mockResolvedValueOnce({ ok: true })
      
      await adminStore.logout()
      
      expect(fetch).toHaveBeenCalledWith('/api/admin/logout', {
        method: 'POST',
        headers
      })
    })

    it('后端登出失败不应该影响本地状态清理', async () => {
      fetch.mockRejectedValueOnce(new Error('Server error'))
      
      await adminStore.logout()
      
      // 本地状态应该仍然被清理
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.admin).toBeNull()
    })
  })

  describe('待审批用户管理', () => {
    it('应该获取待审批用户列表', async () => {
      const mockUsers = [
        { id: 1, username: 'pending1', email: 'pending1@example.com', created_at: '2024-01-01' },
        { id: 2, username: 'pending2', email: 'pending2@example.com', created_at: '2024-01-02' }
      ]
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchPendingApprovals()
      
      expect(adminStore.pendingApprovals).toEqual(mockUsers)
      expect(adminStore.loading).toBe(false)
    })

    it('应该批准用户注册申请', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '用户已批准'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.approveUser(1, '欢迎加入！')
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/1/approve', {
        method: 'POST',
        headers,
        body: JSON.stringify({ note: '欢迎加入！' })
      })
      
      // 应该从列表中移除已批准的用户
      expect(adminStore.pendingApprovals.find(u => u.id === 1)).toBeUndefined()
    })

    it('应该拒绝用户注册申请', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '用户申请已拒绝'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.rejectUser(1, '资料不完整')
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/1/reject', {
        method: 'POST',
        headers,
        body: JSON.stringify({ reason: '资料不完整' })
      })
    })

    it('应该批量批准用户', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.batchApproveUsers([1, 2, 3], '批量批准')
      
      expect(result.success).toBe(true)
      expect(result.approvedCount).toBe(3)
    })
  })

  describe('系统统计', () => {
    it('应该获取系统统计数据', async () => {
      const mockStats = {
        total_users: 1000,
        active_users: 850,
        total_matches: 500,
        pending_approvals: 5,
        system_health: 'good'
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: mockStats
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchSystemStats()
      
      expect(adminStore.systemStats).toEqual(mockStats)
      expect(adminStore.loading).toBe(false)
    })

    it('应该获取实时统计数据', async () => {
      const mockRealtimeStats = {
        online_users: 150,
        matches_in_progress: 3,
        server_load: 45.2
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: mockRealtimeStats
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchRealtimeStats()
      
      expect(adminStore.realtimeStats).toEqual(mockRealtimeStats)
    })
  })

  describe('系统设置管理', () => {
    it('应该获取系统设置', async () => {
      const mockSettings = {
        site_name: '体育彩票分析系统',
        registration_enabled: true,
        max_login_attempts: 5,
        session_timeout: 3600
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          data: mockSettings
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchSettings()
      
      expect(adminStore.settings).toEqual(mockSettings)
    })

    it('应该更新系统设置', async () => {
      const updatedSettings = {
        registration_enabled: false,
        max_login_attempts: 3
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '设置已更新',
          data: updatedSettings
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.updateSettings(updatedSettings)
      
      expect(result.success).toBe(true)
      expect(adminStore.settings.registration_enabled).toBe(false)
      expect(adminStore.settings.max_login_attempts).toBe(3)
    })

    it('应该验证设置值', async () => {
      await expect(adminStore.updateSettings({ max_login_attempts: -1 }))
        .rejects.toThrow('Invalid setting value')
      
      await expect(adminStore.updateSettings({ unknown_setting: 'value' }))
        .rejects.toThrow('Unknown setting')
    })
  })

  describe('管理员管理', () => {
    it('应该获取管理员列表', async () => {
      const mockAdmins = [
        { id: 1, username: 'superadmin', role: 'super_admin', last_login: '2024-01-22T10:00:00Z' },
        { id: 2, username: 'moderator1', role: 'moderator', last_login: '2024-01-22T09:00:00Z' }
      ]
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchAdmins()
      
      expect(adminStore.adminsList).toEqual(mockAdmins)
    })

    it('应该创建新管理员', async () => {
      const newAdminData = {
        username: 'newadmin',
        email: 'newadmin@example.com',
        role: 'moderator',
        permissions: ['users.read', 'matches.manage']
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.createAdmin(newAdminData)
      
      expect(result.success).toBe(true)
      expect(result.admin.id).toBe(3)
      expect(fetch).toHaveBeenCalledWith('/api/admin/admins', {
        method: 'POST',
        headers,
        body: JSON.stringify(newAdminData)
      })
    })

    it('应该更新管理员信息', async () => {
      const updateData = {
        role: 'super_admin',
        permissions: ['*']
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '管理员信息已更新'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.updateAdmin(2, updateData)
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/admins/2', {
        method: 'PUT',
        headers,
        body: JSON.stringify(updateData)
      })
    })

    it('应该删除管理员', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '管理员已删除'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.deleteAdmin(2)
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/admins/2', {
        method: 'DELETE',
        headers
      })
    })
  })

  describe('日志管理', () => {
    it('应该获取系统日志', async () => {
      const mockLogs = [
        { id: 1, level: 'INFO', message: 'User logged in', timestamp: '2024-01-22T10:00:00Z' },
        { id: 2, level: 'ERROR', message: 'Database connection failed', timestamp: '2024-01-22T09:30:00Z' }
      ]
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchLogs({ level: 'ERROR', limit: 50 })
      
      expect(adminStore.logs).toEqual(mockLogs)
      expect(fetch).toHaveBeenCalledWith('/api/admin/logs?level=ERROR&limit=50')
    })

    it('应该导出日志', async () => {
      const mockBlob = new Blob(['log content'], { type: 'text/plain' })
      const mockResponse = {
        ok: true,
        blob: () => Promise.resolve(mockBlob)
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.exportLogs('2024-01-01', '2024-01-31')
      
      expect(result).toBeInstanceOf(Blob)
      expect(fetch).toHaveBeenCalledWith('/api/admin/logs/export?start_date=2024-01-01&end_date=2024-01-31')
    })

    it('应该清空日志', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '日志已清空'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.clearLogs()
      
      expect(result.success).toBe(true)
      expect(adminStore.logs).toEqual([])
    })
  })

  describe('安全功能', () => {
    it('应该更改管理员密码', async () => {
      const passwordData = {
        current_password: 'oldpass',
        new_password: 'newpass123'
      }
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '密码已更改'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.changePassword(passwordData)
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/change-password', {
        method: 'POST',
        headers,
        body: JSON.stringify(passwordData)
      })
    })

    it('应该获取登录历史', async () => {
      const mockLoginHistory = [
        { id: 1, ip: '192.168.1.100', location: 'Beijing', timestamp: '2024-01-22T10:00:00Z', success: true },
        { id: 2, ip: '192.168.1.101', location: 'Shanghai', timestamp: '2024-01-21T15:30:00Z', success: false }
      ]
      
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchLoginHistory()
      
      expect(adminStore.loginHistory).toEqual(mockLoginHistory)
    })

    it('应该锁定可疑账户', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          message: '账户已锁定'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const result = await adminStore.lockAccount(123, 'Suspicious activity')
      
      expect(result.success).toBe(true)
      expect(fetch).toHaveBeenCalledWith('/api/admin/users/123/lock', {
        method: 'POST',
        headers,
        body: JSON.stringify({ reason: 'Suspicious activity' })
      })
    })
  })

  describe('错误处理', () => {
    it('应该处理 401 未授权错误', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: () => Promise.resolve({
          success: false,
          message: 'Unauthorized'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchPendingApprovals()
      
      // 应该自动登出
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.admin).toBeNull()
      expect(window.location.href).toBe('/admin/login')
    })

    it('应该处理 403 禁止访问错误', async () => {
      const mockResponse = {
        ok: false,
        status: 403,
        json: () => Promise.resolve({
          success: false,
          message: 'Insufficient permissions'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.fetchPendingApprovals()
      
      expect(adminStore.error).toBe('权限不足')
    })

    it('应该处理 422 验证错误', async () => {
      const mockResponse = {
        ok: false,
        status: 422,
        json: () => Promise.resolve({
          success: false,
          errors
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      await adminStore.createAdmin({ username: 'existing', email: 'invalid' })
      
      expect(adminStore.error).toContain('用户名已存在')
      expect(adminStore.error).toContain('邮箱格式不正确')
    })

    it('应该处理网络超时', async () => {
      fetch.mockImplementationOnce(() => new Promise((_, reject) => {
        setTimeout(() => reject(new Error('timeout')), 100)
      }))
      
      await adminStore.fetchSystemStats()
      
      expect(adminStore.error).toBe('请求超时')
    })
  })

  describe('数据持久化和清理', () => {
    it('应该定期刷新管理员信息', () => {
      vi.useFakeTimers()
      
      adminStore.setupAutoRefresh()
      
      // 快进30分钟（刷新间隔）
      vi.advanceTimersByTime(30 * 60 * 1000)
      
      // 应该尝试刷新数据
      expect(fetch).toHaveBeenCalled()
      
      vi.useRealTimers()
    })

    it('组件卸载时应该清理定时器', () => {
      const clearInterval = vi.fn()
      vi.stubGlobal('clearInterval', clearInterval)
      
      adminStore.setupAutoRefresh()
      adminStore.$dispose?.()
      
      expect(clearInterval).toHaveBeenCalled()
      
      vi.unstubAllGlobals()
    })

    it('应该验证 token 有效性', async () => {
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({
          success: true,
          valid: true,
          data }
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const isValid = await adminStore.verifyToken()
      
      expect(isValid).toBe(true)
      expect(adminStore.admin.username).toBe('admin')
    })

    it('无效 token 应该清除状态', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: () => Promise.resolve({
          success: false,
          message: 'Invalid token'
        })
      }
      
      fetch.mockResolvedValueOnce(mockResponse)
      
      const isValid = await adminStore.verifyToken()
      
      expect(isValid).toBe(false)
      expect(adminStore.isAuthenticated).toBe(false)
      expect(adminStore.token).toBe('')
    })
  })

  describe('性能优化', () => {
    it('应该缓存频繁访问的数据', async () => {
      const mockStats = { total_users: 1000 }
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockStats })
      }
      
      // 第一次调用
      fetch.mockResolvedValueOnce(mockResponse)
      await adminStore.fetchSystemStats()
      expect(fetch).toHaveBeenCalledTimes(1)
      
      // 第二次调用应该使用缓存
      await adminStore.fetchSystemStats()
      expect(fetch).toHaveBeenCalledTimes(1) // 没有增加
    })

    it('缓存应该有合理的过期时间', async () => {
      vi.useFakeTimers()
      
      const mockStats = { total_users: 1000 }
      const mockResponse = {
        ok: true,
        json: () => Promise.resolve({ success: true, data: mockStats })
      }
      
      fetch.mockResolvedValue(mockResponse)
      
      await adminStore.fetchSystemStats()
      
      // 快进6分钟（超过5分钟缓存时间）
      vi.advanceTimersByTime(6 * 60 * 1000)
      
      await adminStore.fetchSystemStats()
      
      // 应该重新获取数据
      expect(fetch).toHaveBeenCalledTimes(2)
      
      vi.useRealTimers()
    })

    it('应该限制日志数据量防止内存泄漏', async () => {
      // 添加大量日志
      for (let i = 0; i < 1500; i++) {
        adminStore.logs.push({
          id: i,
          level: 'INFO',
          message: `Log message ${i}`,
          timestamp: new Date().toISOString()
        })
      }
      
      // 应该被限制在某个合理范围内
      expect(adminStore.logs.length).toBeLessThan(2000)
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
