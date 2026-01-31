// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
/**
 * API 工具函数单元测试示例
 */
import { describe, it, expect, vi } from 'vitest'
import { request } from '@/utils/request'
import axios from 'axios'

// 模拟axios
vi.mock('axios', () => {
  const mockAxios = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
  return { default: mockAxios }
})

describe('API 工具函数测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('request 函数应该正确处理 GET 请求', async () => {
    const mockResponse = { data: { success: true, message: '操作成功' } }
    axios.get.mockResolvedValue(mockResponse)
    
    const result = await request('/test-endpoint')
    
    expect(axios.get).toHaveBeenCalledWith('/test-endpoint')
    expect(result.data.success).toBe(true)
  })

  it('request 函数应该正确处理错误', async () => {
    const error = new Error('Network Error')
    axios.get.mockRejectedValue(error)
    
    try {
      await request('/error-endpoint')
    } catch (err) {
      expect(err.message).toBe('Network Error')
    }
    
    expect(axios.get).toHaveBeenCalledWith('/error-endpoint')
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
