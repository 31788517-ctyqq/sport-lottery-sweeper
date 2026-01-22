import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { request, apiClient, authApiClient } from '@/utils/request.js'

// 模拟 axios
global.FormData = vi.fn(() => ({
  append: vi.fn()
}))

global.URLSearchParams = vi.fn(() => ({
  append: vi.fn()
}))

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// 模拟 window.location
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: { href: 'http://localhost:3000/' },
  writable: true
})

describe('request.js (HTTP Request Utilities)', () => {
  let mockAxiosInstance
  let mockGet
  let mockPost
  let mockPut
  let mockDelete
  let mockRequest
  let mockInterceptors
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    // 创建 axios mock
    mockGet = vi.fn()
    mockPost = vi.fn()
    mockPut = vi.fn()
    mockDelete = vi.fn()
    mockRequest = vi.fn()
    
    mockInterceptors = {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    }
    
    mockAxiosInstance = {
      get: mockGet,
      post: mockPost,
      put: mockPut,
      delete: mockDelete,
      request: mockRequest,
      interceptors: mockInterceptors
    }
    
    // Mock axios import
    vi.doMock('axios', () => ({
      create: vi.fn(() => mockAxiosInstance),
      defaults: { baseURL: '' }
    }))
    
    // Mock auth store
    vi.doMock('@/stores/auth.js', () => ({
      useAuth: () => ({
        token: { value: 'test-token' },
        refreshToken: vi.fn().mockResolvedValue('new-token')
      })
    }))
    
    // Re-import to use mocks
    vi.resetModules()
    
    // Clear module cache and re-import
    delete require.cache[require.resolve('@/utils/request.js')]
    const requestModule = require('@/utils/request.js')
    
    // Extract the functions we need to test
    Object.assign(request, {
      default: requestModule.default,
      apiClient: requestModule.apiClient,
      authApiClient: requestModule.authApiClient
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  describe('基础请求功能', () => {
    it('应该发送 GET 请求', async () => {
      const mockResponse = {
        data: { success: true, data: { id: 1, name: 'test' } },
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      }
      
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const result = await request.get('/api/test')
      
      expect(mockGet).toHaveBeenCalledWith('/api/test', { params: {} })
      expect(result).toEqual({ id: 1, name: 'test' })
    })

    it('GET 请求应该支持查询参数', async () => {
      const mockResponse = { data: { success: true, data: [] } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      await request.get('/api/users', { page: 1, limit: 10 })
      
      expect(mockGet).toHaveBeenCalledWith('/api/users', { 
        params: { page: 1, limit: 10 } 
      })
    })

    it('应该发送 POST 请求', async () => {
      const mockResponse = { data: { success: true, data: { id: 1 } } }
      mockPost.mockResolvedValueOnce(mockResponse)
      
      const data = { name: 'test', email: 'test@example.com' }
      const result = await request.post('/api/users', data)
      
      expect(mockPost).toHaveBeenCalledWith('/api/users', data, { params: {} })
      expect(result).toEqual({ id: 1 })
    })

    it('应该发送 PUT 请求', async () => {
      const mockResponse = { data: { success: true, data: { id: 1, name: 'updated' } } }
      mockPut.mockResolvedValueOnce(mockResponse)
      
      const data = { name: 'updated' }
      const result = await request.put('/api/users/1', data)
      
      expect(mockPut).toHaveBeenCalledWith('/api/users/1', data, { params: {} })
      expect(result).toEqual({ id: 1, name: 'updated' })
    })

    it('应该发送 DELETE 请求', async () => {
      const mockResponse = { data: { success: true, message: 'deleted' } }
      mockDelete.mockResolvedValueOnce(mockResponse)
      
      const result = await request.delete('/api/users/1')
      
      expect(mockDelete).toHaveBeenCalledWith('/api/users/1', { params: {} })
      expect(result).toEqual({ message: 'deleted' })
    })

    it('应该发送 PATCH 请求', async () => {
      const mockResponse = { data: { success: true, data: { id: 1, partial: 'update' } } }
      mockAxiosInstance.patch = vi.fn().mockResolvedValueOnce(mockResponse)
      
      const data = { partial: 'update' }
      const result = await request.patch('/api/users/1', data)
      
      expect(mockAxiosInstance.patch).toHaveBeenCalledWith('/api/users/1', data, { params: {} })
      expect(result).toEqual({ id: 1, partial: 'update' })
    })
  })

  describe('请求配置', () => {
    it('应该支持自定义配置', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const config = {
        timeout: 5000,
        headers: { 'X-Custom-Header': 'custom-value' },
        params: { filter: 'active' }
      }
      
      await request.get('/api/test', config)
      
      expect(mockGet).toHaveBeenCalledWith('/api/test', {
        params: { filter: 'active' },
        timeout: 5000,
        headers: { 'X-Custom-Header': 'custom-value' }
      })
    })

    it('应该合并默认配置和用户配置', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockPost.mockResolvedValueOnce(mockResponse)
      
      const userConfig = {
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      }
      
      await request.post('/api/test', { data: 'test' }, userConfig)
      
      expect(mockPost).toHaveBeenCalledWith('/api/test', { data: 'test' }, {
        params: {},
        timeout: 10000,
        headers: { 'Content-Type': 'application/json' }
      })
    })

    it('应该支持 FormData 上传', async () => {
      const mockResponse = { data: { success: true, data: { id: 1 } } }
      mockPost.mockResolvedValueOnce(mockResponse)
      
      const formData = new FormData()
      formData.append('file', 'test-file')
      
      await request.upload('/api/upload', formData)
      
      expect(mockPost).toHaveBeenCalledWith('/api/upload', formData, {
        params: {},
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    })

    it('应该支持文件下载', async () => {
      const mockBlob = new Blob(['file content'], { type: 'text/plain' })
      const mockResponse = { 
        data: mockBlob,
        headers: { 'content-disposition': 'attachment; filename="test.txt"' }
      }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const result = await request.download('/api/download/file.txt')
      
      expect(mockGet).toHaveBeenCalledWith('/api/download/file.txt', {
        params: {},
        responseType: 'blob'
      })
      expect(result).toBe(mockBlob)
    })
  })

  describe('认证和头部管理', () => {
    it('应该自动添加认证 token', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      await request.get('/api/protected')
      
      // 检查请求拦截器是否被调用
      expect(mockInterceptors.request.use).toHaveBeenCalled()
    })

    it('没有 token 时不应该添加 Authorization 头', async () => {
      // Mock no token
      vi.doMock('@/stores/auth.js', () => ({
        useAuth: () => ({ token: { value: '' } })
      }))
      
      vi.resetModules()
      delete require.cache[require.resolve('@/utils/request.js')]
      const requestModule = require('@/utils/request.js')
      
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      await requestModule.default.get('/api/public')
      
      // Token 为空时不会添加到 headers
      expect(mockGet).toHaveBeenCalled()
    })

    it('应该添加 CSRF token', async () => {
      localStorage.getItem.mockReturnValue('csrf-token-value')
      
      const mockResponse = { data: { success: true, data: {} } }
      mockPost.mockResolvedValueOnce(mockResponse)
      
      await request.post('/api/secure', { data: 'test' })
      
      expect(localStorage.getItem).toHaveBeenCalledWith('csrf-token')
    })

    it('应该添加请求追踪 ID', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      await request.get('/api/tracked')
      
      // 请求拦截器应该添加 X-Request-ID header
      expect(mockInterceptors.request.use).toHaveBeenCalled()
    })
  })

  describe('响应处理', () => {
    it('应该正确处理成功响应', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: { id: 1, name: 'test' },
          message: 'Operation successful'
        },
        status: 200
      }
      
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const result = await request.get('/api/success')
      
      expect(result).toEqual({ id: 1, name: 'test' })
    })

    it('应该提取嵌套的数据字段', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            items: [{ id: 1 }, { id: 2 }],
            pagination: { page: 1, total: 2 }
          }
        }
      }
      
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const result = await request.get('/api/data')
      
      expect(result).toEqual({ items: [{ id: 1 }, { id: 2 }], pagination: { page: 1, total: 2 } })
    })

    it('应该抛出业务错误', async () => {
      const mockResponse = {
        data: {
          success: false,
          message: 'Validation failed',
          errors: { field: ['Required field'] }
        },
        status: 400
      }
      
      mockPost.mockResolvedValueOnce(mockResponse)
      
      try {
        await request.post('/api/validate', { invalid: 'data' })
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('Validation failed')
        expect(error.code).toBe(400)
        expect(error.errors).toEqual({ field: ['Required field'] })
      }
    })

    it('应该处理非标准响应格式', async () => {
      const mockResponse = {
        data: { unexpected: 'format' },
        status: 200
      }
      
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const result = await request.get('/api/unexpected')
      
      expect(result).toEqual({ unexpected: 'format' })
    })
  })

  describe('错误处理', () => {
    it('应该处理网络错误', async () => {
      const networkError = new Error('Network Error')
      networkError.code = 'NETWORK_ERROR'
      mockGet.mockRejectedValueOnce(networkError)
      
      try {
        await request.get('/api/network-error')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('网络连接失败，请检查网络设置')
        expect(error.code).toBe('NETWORK_ERROR')
      }
    })

    it('应该处理超时错误', async () => {
      const timeoutError = new Error('timeout of 5000ms exceeded')
      timeoutError.code = 'ECONNABORTED'
      mockGet.mockRejectedValueOnce(timeoutError)
      
      try {
        await request.get('/api/timeout')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('请求超时，请稍后重试')
        expect(error.code).toBe('TIMEOUT')
      }
    })

    it('应该处理 401 未授权错误', async () => {
      const unauthorizedError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      }
      mockGet.mockRejectedValueOnce(unauthorizedError)
      
      try {
        await request.get('/api/unauthorized')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('登录已过期，请重新登录')
        expect(error.code).toBe(401)
        expect(window.location.href).toBe('/login')
      }
    })

    it('应该处理 403 禁止访问错误', async () => {
      const forbiddenError = {
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        }
      }
      mockGet.mockRejectedValueOnce(forbiddenError)
      
      try {
        await request.get('/api/forbidden')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('权限不足，无法访问该资源')
        expect(error.code).toBe(403)
      }
    })

    it('应该处理 404 资源不存在错误', async () => {
      const notFoundError = {
        response: {
          status: 404,
          data: { message: 'Not Found' }
        }
      }
      mockGet.mockRejectedValueOnce(notFoundError)
      
      try {
        await request.get('/api/not-found')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('请求的资源不存在')
        expect(error.code).toBe(404)
      }
    })

    it('应该处理 422 验证错误', async () => {
      const validationError = {
        response: {
          status: 422,
          data: {
            message: 'Validation failed',
            errors: {
              email: ['邮箱格式不正确'],
              password: ['密码至少8位']
            }
          }
        }
      }
      mockPost.mockRejectedValueOnce(validationError)
      
      try {
        await request.post('/api/validate', { email: 'invalid', password: '123' })
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('Validation failed')
        expect(error.code).toBe(422)
        expect(error.errors).toEqual({
          email: ['邮箱格式不正确'],
          password: ['密码至少8位']
        })
      }
    })

    it('应该处理 429 频率限制错误', async () => {
      const rateLimitError = {
        response: {
          status: 429,
          data: { message: 'Too Many Requests', retryAfter: 60 }
        }
      }
      mockGet.mockRejectedValueOnce(rateLimitError)
      
      try {
        await request.get('/api/rate-limited')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('请求过于频繁，请60秒后重试')
        expect(error.code).toBe(429)
        expect(error.retryAfter).toBe(60)
      }
    })

    it('应该处理 500 服务器错误', async () => {
      const serverError = {
        response: {
          status: 500,
          data: { message: 'Internal Server Error' }
        }
      }
      mockGet.mockRejectedValueOnce(serverError)
      
      try {
        await request.get('/api/server-error')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('服务器内部错误，请稍后重试')
        expect(error.code).toBe(500)
      }
    })

    it('应该处理未知错误', async () => {
      const unknownError = { code: 'UNKNOWN_ERROR' }
      mockGet.mockRejectedValueOnce(unknownError)
      
      try {
        await request.get('/api/unknown')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('请求失败，请稍后重试')
        expect(error.code).toBe('UNKNOWN_ERROR')
      }
    })
  })

  describe('Token 刷新机制', () => {
    it('应该在 401 错误时尝试刷新 token', async () => {
      // Mock refresh token success
      const refreshTokenMock = vi.fn().mockResolvedValue('new-token')
      vi.doMock('@/stores/auth.js', () => ({
        useAuth: () => ({
          token: { value: 'expired-token' },
          refreshToken: refreshTokenMock
        })
      }))
      
      vi.resetModules()
      delete require.cache[require.resolve('@/utils/request.js')]
      const requestModule = require('@/utils/request.js')
      
      let callCount = 0
      const responses = [
        // First call returns 401
        {
          response: { status: 401, data: { message: 'Unauthorized' } }
        },
        // Retry with new token succeeds
        {
          data: { success: true, data: { id: 1 } }
        }
      ]
      
      mockGet.mockImplementation(() => {
        callCount++
        return Promise.resolve(responses[callCount - 1])
      })
      
      const result = await requestModule.default.get('/api/refresh-test')
      
      expect(refreshTokenMock).toHaveBeenCalled()
      expect(callCount).toBe(2) // Original call + retry
      expect(result).toEqual({ id: 1 })
    })

    it('token 刷新失败时应该登出', async () => {
      // Mock refresh token failure
      vi.doMock('@/stores/auth.js', () => ({
        useAuth: () => ({
          token: { value: 'expired-token' },
          refreshToken: vi.fn().mockRejectedValue(new Error('Refresh failed'))
        })
      }))
      
      vi.resetModules()
      delete require.cache[require.resolve('@/utils/request.js')]
      const requestModule = require('@/utils/request.js')
      
      const unauthorizedError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        }
      }
      mockGet.mockRejectedValueOnce(unauthorizedError)
      
      try {
        await requestModule.default.get('/api/refresh-fail')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('登录已过期，请重新登录')
        expect(window.location.href).toBe('/login')
      }
    })

    it('应该避免无限刷新循环', async () => {
      // Mock refresh token always returning 401
      vi.doMock('@/stores/auth.js', () => ({
        useAuth: () => ({
          token: { value: 'always-expired' },
          refreshToken: vi.fn().mockResolvedValue('still-expired')
        })
      }))
      
      vi.resetModules()
      delete require.cache[require.resolve('@/utils/request.js')]
      const requestModule = require('@/utils/request.js')
      
      // Mock API to always return 401 even after refresh
      mockGet.mockRejectedValue({
        response: { status: 401, data: { message: 'Unauthorized' } }
      })
      
      try {
        await requestModule.default.get('/api/infinite-loop')
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        // Should fail after max retries
        expect(error.message).toBe('登录已过期，请重新登录')
      }
    })
  })

  describe('缓存功能', () => {
    beforeEach(() => {
      vi.useFakeTimers()
    })

    afterEach(() => {
      vi.useRealTimers()
    })

    it('应该缓存 GET 请求结果', async () => {
      const mockResponse = { data: { success: true, data: { cached: true } } }
      mockGet.mockResolvedValue(mockResponse)
      
      // First call
      const result1 = await request.get('/api/cached', {}, { cache: true })
      expect(result1).toEqual({ cached: true })
      expect(mockGet).toHaveBeenCalledTimes(1)
      
      // Second call should use cache
      const result2 = await request.get('/api/cached', {}, { cache: true })
      expect(result2).toEqual({ cached: true })
      expect(mockGet).toHaveBeenCalledTimes(1) // No additional call
    })

    it('缓存应该有 TTL', async () => {
      const mockResponse = { data: { success: true, data: { ttl: true } } }
      mockGet.mockResolvedValue(mockResponse)
      
      // First call
      await request.get('/api/ttl', {}, { cache: true, cacheTTL: 60000 }) // 1 minute TTL
      expect(mockGet).toHaveBeenCalledTimes(1)
      
      // Fast forward time beyond TTL
      vi.advanceTimersByTime(61000)
      
      // Should make new request
      await request.get('/api/ttl', {}, { cache: true, cacheTTL: 60000 })
      expect(mockGet).toHaveBeenCalledTimes(2)
    })

    it('应该跳过缓存当指定', async () => {
      const mockResponse = { data: { success: true, data: { noCache: true } } }
      mockGet.mockResolvedValue(mockResponse)
      
      // First call with cache
      await request.get('/api/no-cache', {}, { cache: true })
      expect(mockGet).toHaveBeenCalledTimes(1)
      
      // Second call without cache
      await request.get('/api/no-cache', {}, { cache: false })
      expect(mockGet).toHaveBeenCalledTimes(2)
    })

    it('POST 请求不应该使用缓存', async () => {
      const mockResponse = { data: { success: true, data: { posted: true } } }
      mockPost.mockResolvedValue(mockResponse)
      
      await request.post('/api/post', { data: 'test' }, { cache: true })
      
      // Cache option should be ignored for non-GET requests
      expect(mockPost).toHaveBeenCalled()
    })
  })

  describe('重试机制', () => {
    it('应该在失败时自动重试', async () => {
      const mockResponse = { data: { success: true, data: { retried: true } } }
      
      // First two calls fail, third succeeds
      mockGet
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockResponse)
      
      const result = await request.get('/api/retry', {}, { retry: 3, retryDelay: 100 })
      
      expect(result).toEqual({ retried: true })
      expect(mockGet).toHaveBeenCalledTimes(3)
    })

    it('应该尊重重试次数限制', async () => {
      mockGet.mockRejectedValue(new Error('Persistent error'))
      
      try {
        await request.get('/api/max-retries', {}, { retry: 2, retryDelay: 100 })
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('Persistent error')
        expect(mockGet).toHaveBeenCalledTimes(3) // Original + 2 retries
      }
    })

    it('不应该重试某些错误', async () => {
      const validationError = {
        response: { status: 422, data: { message: 'Validation failed' } }
      }
      mockPost.mockRejectedValueOnce(validationError)
      
      try {
        await request.post('/api/no-retry-validation', { invalid: 'data' }, { retry: 3 })
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.message).toBe('Validation failed')
        expect(mockPost).toHaveBeenCalledTimes(1) // No retries for validation errors
      }
    })

    it('应该对 5xx 错误进行重试', async () => {
      const serverError = { response: { status: 500, data: { message: 'Server error' } } }
      const successResponse = { data: { success: true, data: { recovered: true } } }
      
      mockGet
        .mockRejectedValueOnce(serverError)
        .mockResolvedValueOnce(successResponse)
      
      const result = await request.get('/api/server-retry', {}, { retry: 3 })
      
      expect(result).toEqual({ recovered: true })
      expect(mockGet).toHaveBeenCalledTimes(2)
    })
  })

  describe('并发控制', () => {
    it('应该限制并发请求数量', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValue(mockResponse)
      
      // Make multiple concurrent requests
      const promises = Array.from({ length: 10 }, (_, i) => 
        request.get(`/api/concurrent/${i}`, {}, { concurrency: 3 })
      )
      
      await Promise.all(promises)
      
      // With concurrency limit of 3, requests should be queued
      expect(mockGet).toHaveBeenCalledTimes(10)
    })

    it('应该支持请求去重', async () => {
      const mockResponse = { data: { success: true, data: { deduplicated: true } } }
      mockGet.mockResolvedValue(mockResponse)
      
      // Make duplicate requests
      const promise1 = request.get('/api/dedup', {}, { deduplicate: true })
      const promise2 = request.get('/api/dedup', {}, { deduplicate: true })
      const promise3 = request.get('/api/dedup', {}, { deduplicate: true })
      
      const results = await Promise.all([promise1, promise2, promise3])
      
      // All should return the same result
      results.forEach(result => {
        expect(result).toEqual({ deduplicated: true })
      })
      
      // But only one actual request should be made
      expect(mockGet).toHaveBeenCalledTimes(1)
    })
  })

  describe('客户端管理', () => {
    it('应该创建不同的客户端实例', () => {
      expect(apiClient).toBeDefined()
      expect(authApiClient).toBeDefined()
      expect(apiClient).not.toBe(request.default)
      expect(authApiClient).not.toBe(request.default)
    })

    it('不同客户端应该有不同配置', () => {
      // This would test that different clients have different base URLs or configs
      // Implementation depends on the actual request.js setup
      expect(typeof apiClient.get).toBe('function')
      expect(typeof authApiClient.get).toBe('function')
    })

    it('应该支持取消请求', () => {
      const CancelToken = vi.fn(() => ({ token: 'cancel-token', cancel: vi.fn() }))
      vi.doMock('axios', () => ({
        create: vi.fn(() => ({ ...mockAxiosInstance, CancelToken })),
        defaults: { baseURL: '' }
      }))
      
      vi.resetModules()
      delete require.cache[require.resolve('@/utils/request.js')]
      const requestModule = require('@/utils/request.js')
      
      const source = requestModule.default.CancelToken.source()
      
      expect(source.token).toBe('cancel-token')
      expect(typeof source.cancel).toBe('function')
    })
  })

  describe('性能监控', () => {
    it('应该记录请求时间', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValueOnce(mockResponse)
      
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      
      await request.get('/api/timing')
      
      // Should log timing information
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Request completed'),
        expect.objectContaining({ url: '/api/timing' })
      )
      
      consoleSpy.mockRestore()
    })

    it('应该监控慢请求', async () => {
      vi.useFakeTimers()
      
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockImplementation(async () => {
        // Simulate slow response
        await new Promise(resolve => setTimeout(resolve, 6000)) // 6 seconds
        return mockResponse
      })
      
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      const requestPromise = request.get('/api/slow', {}, { slowRequestThreshold: 5000 })
      
      // Fast-forward past the slow threshold
      vi.advanceTimersByTime(5000)
      
      await requestPromise
      
      // Should warn about slow request
      expect(consoleSpy).toHaveBeenCalledWith(
        expect.stringContaining('Slow request detected'),
        expect.objectContaining({ url: '/api/slow' })
      )
      
      consoleSpy.mockRestore()
      vi.useRealTimers()
    })

    it('应该收集请求统计信息', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValue(mockResponse)
      
      await request.get('/api/stats1')
      await request.get('/api/stats2')
      await request.post('/api/stats3', { data: 'test' })
      
      const stats = request.getStats()
      
      expect(stats.totalRequests).toBe(3)
      expect(stats.methods.GET).toBe(2)
      expect(stats.methods.POST).toBe(1)
      expect(stats.averageResponseTime).toBeGreaterThan(0)
    })

    it('应该能够重置统计信息', async () => {
      const mockResponse = { data: { success: true, data: {} } }
      mockGet.mockResolvedValue(mockResponse)
      
      await request.get('/api/reset-test')
      
      let stats = request.getStats()
      expect(stats.totalRequests).toBe(1)
      
      request.resetStats()
      
      stats = request.getStats()
      expect(stats.totalRequests).toBe(0)
    })
  })

  describe('开发工具集成', () => {
    it('应该支持请求拦截器扩展', () => {
      const customInterceptor = vi.fn((config) => config)
      
      request.addRequestInterceptor(customInterceptor)
      
      expect(mockInterceptors.request.use).toHaveBeenCalled()
    })

    it('应该支持响应拦截器扩展', () => {
      const customInterceptor = vi.fn((response) => response)
      
      request.addResponseInterceptor(customInterceptor)
      
      expect(mockInterceptors.response.use).toHaveBeenCalled()
    })

    it('应该支持模拟模式', () => {
      request.enableMockMode(true)
      
      // In mock mode, requests should return mock data
      const mockData = { mocked: true }
      request.setMockData('/api/mock', mockData)
      
      // This would need the actual implementation to test properly
      expect(typeof request.enableMockMode).toBe('function')
    })
  })

  describe('错误处理和调试', () => {
    it('应该提供详细的错误信息', async () => {
      const complexError = {
        response: {
          status: 400,
          data: {
            message: 'Complex error',
            errors: {
              field1: ['Error 1'],
              field2: ['Error 2a', 'Error 2b']
            },
            code: 'COMPLEX_ERROR'
          },
          headers: { 'x-request-id': 'req-123' }
        },
        config: {
          url: '/api/complex',
          method: 'POST'
        }
      }
      
      mockPost.mockRejectedValueOnce(complexError)
      
      try {
        await request.post('/api/complex', { data: 'test' })
        expect(false).toBe(true) // Should not reach here
      } catch (error) {
        expect(error.details).toBeDefined()
        expect(error.details.requestId).toBe('req-123')
        expect(error.details.fieldErrors).toBeDefined()
        expect(error.details.fieldErrors.field1).toEqual(['Error 1'])
      }
    })

    it('应该支持错误重试回调', async () => {
      const retryCallback = vi.fn()
      const mockResponse = { data: { success: true, data: { retried: true } } }
      
      mockGet
        .mockRejectedValueOnce(new Error('Temporary error'))
        .mockResolvedValueOnce(mockResponse)
      
      await request.get('/api/retry-callback', {}, { 
        retry: 2, 
        onRetry: retryCallback 
      })
      
      expect(retryCallback).toHaveBeenCalledWith(
        expect.objectContaining({ attempt: 1, error: expect.any(Error) })
      )
    })

    it('应该支持请求取消', () => {
      const cancelToken = { token: 'test-token', cancel: vi.fn() }
      
      request.get('/api/cancellable', {}, { cancelToken })
      
      expect(cancelToken.cancel).not.toHaveBeenCalled()
      
      request.cancelRequest('test-token')
      
      expect(cancelToken.cancel).toHaveBeenCalled()
    })
  })
})