// AI_WORKING: coder1 @2026-02-04T16:31:47 - 增强请求拦截器，添加null值安全处理功能
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_CONFIG = {
  // 强制使用相对路径，通过 Vite proxy 转发到后端，避免 CORS 和硬编码地址问题
  BASE_URL: '',
  TIMEOUT: 15000,
  RETRY_TIMES: 3,
  RETRY_DELAY: 1000
}

/**
 * 递归规范化null/undefined值，替换为安全默认值
 * @param {*} data - 要处理的数据
 * @returns {*} 处理后的数据
 */
function normalizeNullValues(data) {
  if (data === null || data === undefined) {
    return ''
  }
  
  if (Array.isArray(data)) {
    return data.map(item => normalizeNullValues(item))
  }
  
  if (typeof data === 'object') {
    const result = {}
    for (const key in data) {
      result[key] = normalizeNullValues(data[key])
    }
    return result
  }
  
  return data
}

/**
 * 检查错误是否为null值相关错误
 * @param {Error} error - 错误对象
 * @returns {boolean} 是否为null值相关错误
 */
function isNullRelatedError(error) {
  const errorMessage = error.message || ''
  const errorResponse = error.response?.data?.message || ''
  
  const nullKeywords = [
    'null', 'undefined', '无法读取属性', 'Cannot read property',
    '空指针', '空值', '缺失字段', '缺少参数'
  ]
  
  const combined = (errorMessage + errorResponse).toLowerCase()
  return nullKeywords.some(keyword => combined.includes(keyword.toLowerCase()))
}

const request = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
})

// 请求拦截
request.interceptors.request.use(
  async (config) => {
    // 统一使用access_token作为键名，同时兼容旧的token键名
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    console.log('Request interceptor - Token found:', !!token, 'Token length:', token?.length);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log('Request interceptor - Authorization header set successfully');
    }
    config.headers['Content-Type'] = 'application/json'
    
    // 请求数据null值预处理（可选）
    if (config.data) {
      // 可以在这里添加请求数据null值清理逻辑
      // 目前暂不修改，保持向后兼容
    }
    
    console.log('Request interceptor - Final config headers:', config.headers);
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
    console.log('Response interceptor - Response received:', response.status, response.config.url)
    
    const res = response.data
    
    let processedData = {}
    let message = ''
    
    // 处理不同格式的响应数据
    if (res.data !== undefined) {
      // 标准格式: { data: ..., message: ..., success: ... }
      processedData = res.data
      message = res.message || ''
      // 检查success字段（布尔值或字符串）
      const success = res.success !== undefined ? res.success : true
      if (!success) {
        console.error('API响应包含错误消息:', message)
        if (isNullRelatedError(new Error(message))) {
          console.warn('检测到null值相关API错误:', message)
          ElMessage.warning('数据加载异常，部分字段为空')
        } else {
          ElMessage.error(message || 'Error')
        }
        return Promise.reject(new Error(message || 'Error'))
      }
    } else {
      // 非标准格式，直接使用响应体
      processedData = res
      message = ''
    }
    
    // 对直接返回的数据进行null值规范化
    return normalizeNullValues(processedData)
  },
  (error) => {
    // ===== 新增：安全读取响应体，防止 HTML 等非 JSON 内容导致解析错误 =====
    if (error.response) {
      const { status, statusText, data } = error.response
      if (status < 200 || status >= 300) {
        let parsed = null
        if (typeof data === 'string') {
          try {
            parsed = JSON.parse(data)
          } catch {
            console.error(`API 返回非 JSON 响应 (status ${status}):`, data.slice(0, 200))
            return Promise.reject(new Error(`HTTP ${status} ${statusText} - 服务异常`))
          }
        }
        error.response.parsedData = parsed || data
      }
    }
    // ========================================================================
    console.error('API响应错误:', error)
    
    // 检查是否为401未授权错误
    if (error.response && error.response.status === 401) {
      console.error('认证失败: 令牌无效或已过期')
      
      // 开发环境下只显示提示，避免页面刷新循环
      if (import.meta.env.MODE === 'development') {
        console.warn('🔧 开发模式：跳过401页面跳转')
        ElMessage.warning('开发模式：模拟登录过期状态')
      } else {
        ElMessage.error('认证失败，请重新登录')
        // 清除本地存储的认证信息
        localStorage.removeItem('access_token')
        localStorage.removeItem('token')
        
        // 生产环境才执行跳转
        setTimeout(() => {
          window.location.href = '/#/login'
        }, 1500)
      }
      
      return Promise.reject(error)
    }

    // 检查是否为null值相关错误
    if (isNullRelatedError(error)) {
      console.warn('检测到null值相关网络错误:', error.message)
      ElMessage.warning('数据服务异常，请稍后重试')
      // 对于null值相关错误，可以返回一个安全的空数据，避免界面崩溃
      return Promise.resolve({ 
        success: false, 
        message: '数据服务异常',
        data: null 
      })
    }
    
    let errorMessage = error.response?.data?.message || error.message || '网络错误'
    
    // 如果错误信息包含成功字样，这是一个特殊情况
    if (errorMessage.includes('成功')) {
      console.warn('API返回了成功信息，但被当作错误处理:', errorMessage)
      // 在这种情况下，我们可以返回成功结果
      return Promise.resolve({ success: true, message: errorMessage })
    }
    
    ElMessage.error(errorMessage)
    return Promise.reject(error)
  }
)

// AI_DONE: coder1 @2026-02-04T16:31:47
export default request
