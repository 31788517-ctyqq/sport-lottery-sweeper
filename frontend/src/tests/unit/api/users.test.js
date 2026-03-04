// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
// AI_WORKING: coder1 @2025-01-31 12:00:00 - 修复http导入错误，http是默认导出
import http from '../../utils/http'
import * as usersApi from '../../api/modules/users'
// AI_DONE: coder1 @2025-01-31 12:00:00

// AI_WORKING: coder1 @2026-01-29 - 修复 svi 拼写错误，应为 vi
// Mock http module

}))

describe('Users API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  afterEach(() => {
    vi.resetAllMocks()
  })

  describe('getUserList', () => {
    it('should call http.get with correct parameters', async () => {
      const mockParams = { page: 1, size: 20 }
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        size: 20
      }
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserList(mockParams)
      
      expect(http.get).toHaveBeenCalledWith('/admin/users', { params: mockParams })
      expect(result).toEqual(mockResponse)
    })

    it('should handle empty params', async () => {
      const mockResponse = {
        items: [],
        total: 0,
        page: 1,
        size: 20
      }
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserList()
      
      expect(http.get).toHaveBeenCalledWith('/admin/users', { params })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getUserDetail', () => {
    it('should call http.get with correct id', async () => {
      const userId = 1
      const mockResponse = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com'
      }
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserDetail(userId)
      
      expect(http.get).toHaveBeenCalledWith('/admin/users/1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('createUser', () => {
    it('should call http.post with correct data', async () => {
      const userData = {
        username: 'newuser',
        email: 'new@example.com',
        password: 'password123'
      }
      const mockResponse = { id: 2, ...userData }
      
      http.post.mockResolvedValue(mockResponse)
      
      const result = await usersApi.createUser(userData)
      
      expect(http.post).toHaveBeenCalledWith('/admin/users', userData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateUser', () => {
    it('should call http.put with correct id and data', async () => {
      const userId = 1
      const updateData = { email: 'updated@example.com' }
      const mockResponse = { id: 1, email: 'updated@example.com' }
      
      http.put.mockResolvedValue(mockResponse)
      
      const result = await usersApi.updateUser(userId, updateData)
      
      expect(http.put).toHaveBeenCalledWith('/admin/users/1', updateData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('deleteUser', () => {
    it('should call http.delete with correct id', async () => {
      const userId = 1
      const mockResponse = { success: true }
      
      http.delete.mockResolvedValue(mockResponse)
      
      const result = await usersApi.deleteUser(userId)
      
      expect(http.delete).toHaveBeenCalledWith('/admin/users/1')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('batchDeleteUsers', () => {
    it('should call http.delete with correct ids', async () => {
      const userIds = [1, 2, 3]
      const mockResponse = { success: true, deletedCount: 3 }
      
      http.delete.mockResolvedValue(mockResponse)
      
      const result = await usersApi.batchDeleteUsers(userIds)
      
      expect(http.delete).toHaveBeenCalledWith('/admin/users/batch', { 
        
      })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('updateUserStatus', () => {
    it('should call http.patch with correct id and status', async () => {
      const userId = 1
      const status = 'disabled'
      const mockResponse = { id: 1, status: 'disabled' }
      
      http.patch.mockResolvedValue(mockResponse)
      
      const result = await usersApi.updateUserStatus(userId, status)
      
      expect(http.patch).toHaveBeenCalledWith('/admin/users/1/status', { status })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('resetUserPassword', () => {
    it('should call http.post with correct id and data', async () => {
      const userId = 1
      const passwordData = { newPassword: 'newpass123', confirmPassword: 'newpass123' }
      const mockResponse = { success: true }
      
      http.post.mockResolvedValue(mockResponse)
      
      const result = await usersApi.resetUserPassword(userId, passwordData)
      
      expect(http.post).toHaveBeenCalledWith('/admin/users/1/reset-password', passwordData)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getUserRoles', () => {
    it('should call http.get with correct id', async () => {
      const userId = 1
      const mockResponse = [{ id: 1, name: 'admin' }, { id: 2, name: 'user' }]
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserRoles(userId)
      
      expect(http.get).toHaveBeenCalledWith('/admin/users/1/roles')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('assignUserRoles', () => {
    it('should call http.post with correct id and roleIds', async () => {
      const userId = 1
      const roleIds = [1, 2]
      const mockResponse = { success: true }
      
      http.post.mockResolvedValue(mockResponse)
      
      const result = await usersApi.assignUserRoles(userId, roleIds)
      
      expect(http.post).toHaveBeenCalledWith('/admin/users/1/roles', { roleIds })
      expect(result).toEqual(mockResponse)
    })
  })

  describe('importUsers', () => {
    it('should call http.upload with correct file', async () => {
      const mockFile = new File(['test'], 'users.xlsx', { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      const mockResponse = { success: true, importedCount: 10 }
      
      http.upload.mockResolvedValue(mockResponse)
      
      const result = await usersApi.importUsers(mockFile)
      
      expect(http.upload).toHaveBeenCalledWith('/admin/users/import', mockFile)
      expect(result).toEqual(mockResponse)
    })
  })

  describe('exportUsers', () => {
    it('should call http.download with correct parameters', async () => {
      const mockParams = { format: 'xlsx' }
      const mockResponse = new Blob(['test'])
      
      http.download.mockResolvedValue(mockResponse)
      
      const result = await usersApi.exportUsers(mockParams)
      
      expect(http.download).toHaveBeenCalledWith('/admin/users/export', mockParams, 'users.xlsx')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getUserStats', () => {
    it('should call http.get for stats endpoint', async () => {
      const mockResponse = {
        total: 100,
        active: 85,
        inactive: 15
      }
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserStats()
      
      expect(http.get).toHaveBeenCalledWith('/admin/users/stats')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('unlockUser', () => {
    it('should call http.post to unlock user', async () => {
      const userId = 1
      const mockResponse = { success: true }
      
      http.post.mockResolvedValue(mockResponse)
      
      const result = await usersApi.unlockUser(userId)
      
      expect(http.post).toHaveBeenCalledWith('/admin/users/1/unlock')
      expect(result).toEqual(mockResponse)
    })
  })

  describe('getUserLoginHistory', () => {
    it('should call http.get with correct id and params', async () => {
      const userId = 1
      const mockParams = { page: 1, size: 10 }
      const mockResponse = {
        items: [],
        total: 0
      }
      
      http.get.mockResolvedValue(mockResponse)
      
      const result = await usersApi.getUserLoginHistory(userId, mockParams)
      
      expect(http.get).toHaveBeenCalledWith('/admin/users/1/login-history', { params: mockParams })
      expect(result).toEqual(mockResponse)
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
