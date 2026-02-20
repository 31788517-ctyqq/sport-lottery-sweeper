import axios from 'axios'
import { ElMessage } from 'element-plus'

let isHandlingUnauthorized = false

const getSafeToken = () => {
  try {
    return (
      localStorage.getItem('access_token') ||
      localStorage.getItem('token') ||
      localStorage.getItem('auth_token') ||
      localStorage.getItem('admin_token') ||
      ''
    )
  } catch (e) {
    console.warn('读取本地 token 失败:', e)
    return ''
  }
}

const clearAuthTokensSafely = () => {
  try {
    ;['admin_token', 'access_token', 'token', 'auth_token', 'refresh_token'].forEach((key) => {
      try {
        localStorage.removeItem(key)
      } catch (e) {
        console.warn(`清理 token 失败: ${key}`, e)
      }
    })
  } catch (e) {
    console.warn('清理本地登录态失败:', e)
  }
}

const redirectToLogin = () => {
  if (typeof window === 'undefined') return
  window.location.href = '/#/login'
}

const request = axios.create({
  baseURL: '',
  timeout: 15000
})

request.interceptors.request.use(
  (config) => {
    const token = getSafeToken()
    if (token && token !== 'undefined' && token !== 'null') {
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

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.data !== undefined) {
      const success = res.success !== undefined ? res.success : true
      if (!success) {
        console.error('API响应包含错误消息:', res.message || '')
        ElMessage.error(res.message || 'Error')
        return Promise.reject(new Error(res.message || 'Error'))
      }
      return res.data
    }
    return res
  },
  (error) => {
    const suppressErrorMessage = !!error?.config?.suppressErrorMessage
    if (!suppressErrorMessage) {
      console.error('API响应错误:', error)
    }

    if (error.response && error.response.status === 401) {
      console.error('认证失败: 令牌无效或已过期')

      if (!isHandlingUnauthorized) {
        isHandlingUnauthorized = true
        clearAuthTokensSafely()
        ElMessage.error('认证失败，请重新登录')
        setTimeout(() => {
          redirectToLogin()
          isHandlingUnauthorized = false
        }, 300)
      }

      return Promise.reject(error)
    }

    const errorMessage = error.response?.data?.message || error.message || '网络错误'
    if (!suppressErrorMessage) {
      ElMessage.error(errorMessage)
    }
    return Promise.reject(error)
  }
)

export default request
