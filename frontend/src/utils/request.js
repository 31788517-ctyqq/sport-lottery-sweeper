import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router' // 引入路由用于跳转

// API Configuration Constants
const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  TIMEOUT: 15000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000
}

// 创建 axios 实例
const request = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

// 动态获取 token（异步方式，避免 require 问题）
const getToken = async () => {
  try {
    const storeModule = await import('@/store/user')
    const { useUserStore } = storeModule
    const userStore = useUserStore()
    return userStore.token || null
  } catch (error) {
    return null
  }
}

// 请求拦截器
request.interceptors.request.use(
  async (config) => {
    const token = await getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    config.headers['Content-Type'] = 'application/json'
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    const { data, status } = response

    // HTTP 状态码 200 时，进一步检查业务 code
    if (status === 200) {
      // 假设后端成功返回 { code: 0, data: ..., message: '' }
      if (data && data.code === 0) {
        return data.data
      } else {
        ElMessage.error(data.message || '业务逻辑错误')
        return Promise.reject(new Error(data.message || '业务逻辑错误'))
      }
    }

    ElMessage.error(response.message || 'Error')
    return Promise.reject(new Error(response.message || 'Error'))
  },
  async (error) => {
    console.error('响应错误:', error)

    let message = '请求失败'

    if (error.response) {
      const { status, data } = error.response

      switch (status) {
        case 400:
          message = data.message || '请求参数错误'
          break
        case 401:
          message = '未授权，请重新登录'
          router.push('/login') // 修复：未授权跳转登录页
          break
        case 403:
          message = '拒绝访问'
          break
        case 404:
          message = '请求资源不存在'
          break
        case 500:
          message = '服务器内部错误'
          break
        default:
          message = data.message || `连接错误 ${status}`
      }
    } else if (error.request) {
      message = '网络连接失败，请检查网络'
    } else {
      message = error.message || '未知错误'
    }

    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
