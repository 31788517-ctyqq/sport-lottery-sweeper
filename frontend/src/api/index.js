import axios from 'axios'
import { useUserStore } from '@/stores/user'
import router from '@/router'

// 创建axios实例
const apiClient = axios.create({
  // 优先使用环境变量，其次直连后端，避免Vite代理失效导致404
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || 30000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 从store获取token
    const userStore = useUserStore()
    const token = userStore.token
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加请求时间戳
    config.headers['X-Timestamp'] = Date.now()
    
    // 如果是文件上传，修改Content-Type
    if (config.data instanceof FormData) {
      config.headers['Content-Type'] = 'multipart/form-data'
    }

    // 规避 baseURL 含 /api 时重复拼接 /api
    const baseUrl = config.baseURL || apiClient.defaults.baseURL || ''
    if ((baseUrl.endsWith('/api') || baseUrl.endsWith('/api/')) && config.url?.startsWith('/api/')) {
      config.url = config.url.replace(/^\/api/, '')
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    // 统一处理响应数据格式
    if (response.data && typeof response.data === 'object') {
      return response.data
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config
    
    // 开发环境下简化处理401错误，避免刷新循环
    if (import.meta.env.MODE === 'development') {
      console.log('🔧 开发模式：跳过401错误处理')
      return Promise.reject(error)
    }
    
    // 处理401错误 - token过期
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      
      try {
        const userStore = useUserStore()
        await userStore.refreshTokenAction()
        
        // 重试原始请求
        return apiClient(originalRequest)
      } catch (refreshError) {
        // 刷新失败，跳转到登录页
        userStore.logout()
        router.push({ name: 'Login' })
        return Promise.reject(refreshError)
      }
    }
    
    // 处理403错误 - 权限不足
    if (error.response?.status === 403) {
      // 可以跳转到无权限页面或显示提示
      console.error('权限不足:', error)
    }
    
    // 处理500错误 - 服务器错误
    if (error.response?.status >= 500) {
      console.error('服务器错误:', error)
    }
    
    // 统一错误处理
    const errorMessage = error.response?.data?.message || 
                       error.response?.data?.error || 
                       error.message || 
                       '网络错误，请稍后重试'
    
    // 可以在这里显示全局错误提示
    if (typeof window !== 'undefined' && window.$toast) {
      window.$toast.error(errorMessage)
    }
    
    return Promise.reject({
      status: error.response?.status,
      message: errorMessage,
      data: error.response?.data,
      originalError: error
    })
  }
)

// API工具函数
export const setBaseURL = (url) => {
  apiClient.defaults.baseURL = url
}

export const setToken = (token) => {
  apiClient.defaults.headers.common['Authorization'] = `Bearer ${token}`
}

export const removeToken = () => {
  delete apiClient.defaults.headers.common['Authorization']
}

export const setLanguage = (language) => {
  apiClient.defaults.headers.common['Accept-Language'] = language
}

// API 模块统一导出
export * from './auth'
export * from './match'
export * from './admin'
export * from './crawler'
export * from './crawlerSource'
export * from './crawlerTask'
export * from './crawlerIntelligence'
export * from './crawlerConfig'
export * from './data'
export * from './intelligence'
export * from './lottery'
export * from './proxy'
export * from './system'
// AI_WORKING: coder1 @2026-02-01 - 添加通用数据管理API模块
export * from './modules/data-manager'
// AI_DONE: coder1 @2026-02-01

// 导出实例
export default apiClient
