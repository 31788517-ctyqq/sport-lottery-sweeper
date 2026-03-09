/**
 * 前端接口调用示例
 * 基于已测试成功的后端接口
 */

import axios from 'axios'
import API_CONFIG from './config.js'

// 创建axios实例
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log(`🚀 API请求: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('❌ 请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log(`✅ API响应: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('❌ 响应错误:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * 1. 健康检查接口示例
 */
// 服务存活检查
export const checkServiceHealth = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HEALTH.LIVE)
    return response.data
  } catch (error) {
    throw new Error(`服务健康检查失败: ${error.message}`)
  }
}

// API服务状态检查
export const checkApiHealth = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.HEALTH.API)
    return response.data
  } catch (error) {
    throw new Error(`API健康检查失败: ${error.message}`)
  }
}

/**
 * 2. 用户认证接口示例
 */
// 用户登录 (v1 API)
export const loginUser = async (email, password) => {
  try {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.AUTH.LOGIN_V1, {
      email: email,
      password: password
    })
    return response.data
  } catch (error) {
    throw new Error(`登录失败: ${error.response?.data?.detail || error.message}`)
  }
}

// 用户注册 (v1 API)
export const registerUser = async (userData) => {
  try {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.AUTH.REGISTER_V1, userData)
    return response.data
  } catch (error) {
    throw new Error(`注册失败: ${error.response?.data?.detail || error.message}`)
  }
}

// 兼容前端登录接口
export const loginCompat = async (email, password) => {
  try {
    const response = await apiClient.post(API_CONFIG.ENDPOINTS.AUTH.LOGIN_COMPAT, {
      email: email,
      password: password
    })
    return response.data
  } catch (error) {
    throw new Error(`兼容登录失败: ${error.response?.data?.detail || error.message}`)
  }
}

// 获取用户信息
export const getUserProfile = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.AUTH.ME_V1)
    return response.data
  } catch (error) {
    throw new Error(`获取用户信息失败: ${error.message}`)
  }
}

/**
 * 3. 仪表板接口示例
 */
// 获取仪表板统计数据
export const getDashboardStats = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.DASHBOARD.SUMMARY)
    return response.data
  } catch (error) {
    throw new Error(`获取仪表板数据失败: ${error.message}`)
  }
}

/**
 * 4. 情报系统接口示例
 */
// 获取情报筛查列表
export const getIntelligenceScreeningList = async () => {
  try {
    const response = await apiClient.get(API_CONFIG.ENDPOINTS.INTELLIGENCE.SCREENING_LIST)
    return response.data
  } catch (error) {
    throw new Error(`获取情报列表失败: ${error.message}`)
  }
}

// 使用示例
/*
// 在Vue组件中使用示例
import { checkServiceHealth, loginUser, getDashboardStats } from '@/api/example.js'

export default {
  async mounted() {
    // 检查服务状态
    const health = await checkServiceHealth()
    console.log('服务状态:', health)
    
    // 登录示例
    try {
      const loginResult = await loginUser('admin@example.com', 'password')
      console.log('登录成功:', loginResult)
      
      // 获取仪表板数据
      const dashboardData = await getDashboardStats()
      console.log('仪表板数据:', dashboardData)
    } catch (error) {
      console.error('操作失败:', error.message)
    }
  }
}
*/