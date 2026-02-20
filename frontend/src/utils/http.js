import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import router from '@/router'
import { useUserStore } from '@/stores/user'

// API配置
const API_CONFIG = {
  // 强制使用空字符串，通过 Vite proxy 转发到后端，避免重复/api路径
  BASE_URL: '',
  TIMEOUT: 15000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000
}

// 创建axios实例
const http = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求重试逻辑
const retryRequest = async (error, retryTimes = API_CONFIG.RETRY_TIMES) => {
  const config = error.config
  
  if (!config || !config.retryCount) {
    config.retryCount = 0
  }
  
  if (config.retryCount >= retryTimes) {
    return Promise.reject(error)
  }
  
  config.retryCount += 1
  
  // 延迟重试
  await new Promise(resolve => setTimeout(resolve, API_CONFIG.RETRY_DELAY))
  
  return http(config)
}

// 请求拦截器
http.interceptors.request.use(
  (config) => {
    // 获取 token：优先 admin_token，其次 access_token/token（兼容旧实现）
    const userStore = useUserStore()
    const token =
      userStore.token ||
      localStorage.getItem('admin_token') ||
      localStorage.getItem('access_token') ||
      localStorage.getItem('token')
    
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    // 添加时间戳防止缓存
    if (config.method?.toLowerCase() === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  (response) => {
    const { data, config } = response
    
    // 如果是文件下载，直接返回
    if (config.responseType === 'blob') {
      return response
    }
    
    // 根据后端响应格式处理
    if (data.code !== undefined) {
      if (data.code === 0 || data.code === 200) {
        return data.data !== undefined ? data.data : data
      } else {
        ElMessage.error(data.message || '请求失败')
        
        // 特定错误处理
        if (data.code === 401) {
          handleTokenExpired()
        } else if (data.code === 403) {
          ElMessage.warning('权限不足')
        } else if (data.code === 404) {
          ElMessage.warning('资源不存在')
        } else if (data.code >= 500) {
          ElMessage.error('服务器内部错误')
        }
        
        return Promise.reject(new Error(data.message || '请求失败'))
      }
    }
    
    // 如果没有code字段，假设是直接的数据响应
    return data
  },
  async (error) => {
    const { response, config } = error
    
    if (response) {
      const { status, data } = response
      
      switch (status) {
        case 401:
          handleTokenExpired()
          break
        case 403:
          ElMessage.warning('权限不足，请联系管理员')
          break
        case 404:
          ElMessage.warning('请求的资源不存在')
          break
        case 422:
          ElMessage.error(data.detail || '参数验证失败')
          break
        case 429:
          ElMessage.warning('请求过于频繁，请稍后再试')
          break
        case 500:
          ElMessage.error('服务器内部错误')
          break
        default:
          ElMessage.error(data.message || `请求失败 (${status})`)
      }
    } else if (error.code === 'NETWORK_ERROR') {
      ElMessage.error('网络连接失败，请检查网络设置')
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时，请稍后重试')
      
      // 超时重试
      if (config && !config._retry) {
        config._retry = true
        return retryRequest(error)
      }
    }
    
    return Promise.reject(error)
  }
)

// 处理token过期
const handleTokenExpired = () => {
  const userStore = useUserStore()
  
  ElMessageBox.confirm(
    '登录已过期，请重新登录',
    '提示',
    {
      confirmButtonText: '重新登录',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    userStore.logout()
    router.push('/login')
  }).catch(() => {
    // 用户取消，不做处理
  })
}

// 通用请求方法
const request = {
  get: (url, params, config = {}) => http.get(url, { params, ...config }),
  post: (url, data, config = {}) => http.post(url, data, config),
  put: (url, data, config = {}) => http.put(url, data, config),
  patch: (url, data, config = {}) => http.patch(url, data, config),
  delete: (url, config = {}) => http.delete(url, config),
  
  // 文件上传
  upload: (url, file, config = {}) => {
    const formData = new FormData()
    formData.append('file', file)
    return http.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      ...config
    })
  },
  
  // 文件下载
  download: (url, params, filename) => {
    return http.get(url, {
      params,
      responseType: 'blob'
    }).then(response => {
      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    })
  }
}

export { request }
export default http
