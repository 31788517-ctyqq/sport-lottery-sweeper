import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { getToken, getRefreshToken, removeToken } from '@/utils/authUtils'

const service = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 15000
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

let isRefreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(cb) {
  refreshSubscribers.push(cb)
}

function onRefreshed(token) {
  refreshSubscribers.map(cb => cb(token))
}

// 响应拦截器
service.interceptors.response.use(
  response => {
    const res = response.data
    
    // 如果是文件下载请求，直接返回response
    if (response.config.responseType === 'blob') {
      return response
    }

    return res
  },
  async error => {
    const { response } = error
    const userStore = useUserStore()

    if (!response) {
      ElMessage({
        message: '网络连接失败',
        type: 'error',
        duration: 5 * 1000
      })
      return Promise.reject(error)
    }

    const { status, data } = response

    // Token过期处理
    if (status === 401) {
      if (!isRefreshing) {
        isRefreshing = true
        try {
          const refreshTokenValue = getRefreshToken()
          if (!refreshTokenValue) {
            throw new Error('No refresh token')
          }
          
          const refreshResponse = await service.post('/api/v1/auth/refresh', {
            refresh_token: refreshTokenValue
          })

          const { access_token, refresh_token } = refreshResponse.data
          userStore.token = access_token
          setToken(access_token, refresh_token)
          isRefreshing = false
          
          onRefreshed(access_token)
          refreshSubscribers = []
          
          // 重试原请求
          error.config.headers['Authorization'] = `Bearer ${access_token}`
          return service(error.config)
        } catch (refreshError) {
          isRefreshing = false
          refreshSubscribers = []
          userStore.resetState()
          
          ElMessageBox.confirm(
            '登录状态已过期，请重新登录',
            '系统提示',
            {
              confirmButtonText: '重新登录',
              cancelButtonText: '取消',
              type: 'warning'
            }
          ).then(() => {
            window.location.href = '/login'
          })
          
          return Promise.reject(refreshError)
        }
      } else {
        // 等待刷新完成
        return new Promise((resolve) => {
          subscribeTokenRefresh(token => {
            error.config.headers['Authorization'] = `Bearer ${token}`
            resolve(service(error.config))
          })
        })
      }
    }

    // 其他错误处理
    const message = data?.message || '请求失败'
    ElMessage({
      message,
      type: 'error',
      duration: 5 * 1000
    })

    return Promise.reject(error)
  }
)

export default service