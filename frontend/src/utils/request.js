import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001',
  TIMEOUT: 15000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000
}

const request = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

// 请求拦截
request.interceptors.request.use(
  async (config) => {
    const token = localStorage.getItem('token') // 简单取本地 token
    if (token) config.headers.Authorization = `Bearer ${token}`
    config.headers['Content-Type'] = 'application/json'
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.message || 'Error')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    return res.data // 直接返回 data 部分
  },
  (error) => {
    ElMessage.error(error.response?.data?.message || error.message)
    return Promise.reject(error)
  }
)

export default request
