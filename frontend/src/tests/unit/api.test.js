/**
 * API 工具函数单元测试示例
 */
import { describe, it, expect, vi } from 'vitest'
import { request } from '@/utils/request'

// 模拟 axios
vi.mock('@/utils/request', () => ({
  request: vi.fn()
}))

describe('API 工具函数测试', () => {
  beforeEach(() => {
    // 清除所有 mock 调用
    vi.clearAllMocks()
  })

  it('request 函数应该正确处理 GET 请求', async () => {
    // 模拟成功响应
    request.mockResolvedValue({ data: { success: true } })
    
    const result = await request('/test-endpoint')
    
    expect(request).toHaveBeenCalledWith('/test-endpoint')
    expect(result.data.success).toBe(true)
  })

  it('request 函数应该正确处理错误', async () => {
    // 模拟错误响应
    request.mockRejectedValue(new Error('Network Error'))
    
    try {
      await request('/error-endpoint')
    } catch (error) {
      expect(error.message).toBe('Network Error')
    }
    
    expect(request).toHaveBeenCalledWith('/error-endpoint')
  })
})