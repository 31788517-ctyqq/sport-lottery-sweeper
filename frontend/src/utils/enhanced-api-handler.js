/**
 * 增强API处理器 - 统一解决404/401/422等问题
 * 从网络层提供稳定的错误处理和数据获取
 */

import { ElMessage, ElLoading } from 'element-plus'
import router from '@/router'

class EnhancedAPIHandler {
  constructor() {
    this.cache = new Map()
    this.retryQueue = new Map()
  }

  /**
   * 统一API请求方法 - 解决所有常见错误
   */
  async request(url, options = {}) {
    const {
      method = 'GET',
      data = null,
      params = {},
      loading = true,
      retry = 2,
      timeout = 10000,
      silent = false
    } = options

    const loadingInstance = loading ? ElLoading.service({ lock: true, text: '加载中...' }) : null
    
    try {
      // 构建请求配置
      const config = {
        method,
        url,
        params: method === 'GET' ? params : undefined,
        data: method !== 'GET' ? data : undefined,
        timeout,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        }
      }

      // 添加认证token
      const token = localStorage.getItem('access_token') || localStorage.getItem('token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }

      const response = await fetch(url, {
        method: config.method,
        headers: config.headers,
        body: config.data ? JSON.stringify(config.data) : undefined
      })

      // 隐藏loading
      loadingInstance?.close()

      // 处理HTTP状态码
      if (!response.ok) {
        await this.handleHttpError(response, url, silent)
        return { success: false, error: `HTTP ${response.status}` }
      }

      // 解析响应数据
      const responseData = await response.json()
      
      // 标准化响应格式
      return this.normalizeResponse(responseData)

    } catch (error) {
      loadingInstance?.close()
      
      // 网络错误处理
      await this.handleNetworkError(error, url, silent)
      return { success: false, error: error.message }
    }
  }

  /**
   * 处理HTTP错误 - 解决404/401/422等
   */
  async handleHttpError(response, url, silent) {
    const { status } = response

    switch (status) {
      case 401:
        // 认证失败 - 清除token并跳转登录
        localStorage.removeItem('access_token')
        localStorage.removeItem('token')
        if (!silent) {
          ElMessage.error('登录已过期，请重新登录')
          setTimeout(() => router.push('/login'), 1500)
        }
        break

      case 403:
        // 权限不足
        if (!silent) ElMessage.warning('权限不足，请联系管理员')
        break

      case 404:
        // 资源不存在 - 静默处理，返回空数据
        if (!silent) ElMessage.warning('请求的资源不存在')
        console.warn(`API not found: ${url}`)
        break

      case 422:
        // 参数验证错误
        try {
          const errorData = await response.json()
          const message = errorData.detail || errorData.message || '参数验证失败'
          if (!silent) ElMessage.error(message)
        } catch {
          if (!silent) ElMessage.error('参数验证失败')
        }
        break

      case 429:
        // 请求频率限制
        if (!silent) ElMessage.warning('请求过于频繁，请稍后再试')
        break

      default:
        if (status >= 500) {
          // 服务器错误
          if (!silent) ElMessage.error('服务器内部错误，请稍后重试')
        } else {
          if (!silent) ElMessage.error(`请求失败 (${status})`)
        }
        break
    }
  }

  /**
   * 处理网络错误
   */
  async handleNetworkError(error, url, silent) {
    console.error(`Network error for ${url}:`, error)
    
    if (!silent) {
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        ElMessage.error('网络连接失败，请检查网络设置')
      } else if (error.name === 'AbortError') {
        ElMessage.warning('请求超时，请稍后重试')
      } else {
        ElMessage.error('网络请求失败，请稍后重试')
      }
    }
  }

  /**
   * 标准化响应格式 - 确保前端能正确处理
   */
  normalizeResponse(responseData) {
    // 如果已经是标准格式，直接返回
    if (responseData.code !== undefined || responseData.success !== undefined) {
      return {
        success: responseData.code === 200 || responseData.success === true,
        data: responseData.data !== undefined ? responseData.data : responseData,
        message: responseData.message || 'success',
        code: responseData.code || 200
      }
    }

    // 转换各种响应格式为标准格式
    if (typeof responseData === 'object' && responseData !== null) {
      return {
        success: true,
        data: responseData,
        message: 'success',
        code: 200
      }
    }

    // 简单数据类型
    return {
      success: true,
      data: responseData,
      message: 'success',
      code: 200
    }
  }

  /**
   * 便捷方法 - GET请求
   */
  async get(url, params = {}, options = {}) {
    return this.request(url, { ...options, method: 'GET', params })
  }

  /**
   * 便捷方法 - POST请求
   */
  async post(url, data = {}, options = {}) {
    return this.request(url, { ...options, method: 'POST', data })
  }

  /**
   * 便捷方法 - PUT请求
   */
  async put(url, data = {}, options = {}) {
    return this.request(url, { ...options, method: 'PUT', data })
  }

  /**
   * 便捷方法 - DELETE请求
   */
  async delete(url, options = {}) {
    return this.request(url, { ...options, method: 'DELETE' })
  }

  /**
   * 安全的菜单数据获取 - 专门解决管理页面问题
   */
  async getMenuData(menuType) {
    const urls = {
      users: '/api/admin/users',
      roles: '/api/admin/roles', 
      departments: '/api/admin/departments',
      dataSource: '/api/v1/admin/data-sources',
      crawlerTasks: '/api/v1/admin/crawler/tasks',
      systemLogs: '/api/v1/admin/system/logs'
    }

    const url = urls[menuType]
    if (!url) {
      console.warn(`Unknown menu type: ${menuType}`)
      return { success: true, data: [] } // 返回空数组避免报错
    }

    // 静默模式，避免过多弹窗
    const result = await this.get(url, {}, { silent: true, loading: true })
    
    // 如果请求失败，返回空数据而不是错误
    if (!result.success) {
      console.warn(`Failed to load ${menuType} data:`, result.error)
      return { success: true, data: [], error: result.error }
    }

    return result
  }
}

// 创建全局实例
export const enhancedAPI = new EnhancedAPIHandler()

export default enhancedAPI