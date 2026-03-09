// frontend/src/utils/authUtils.js

/**
 * 认证相关工具函数
 */

// Token管理
const TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'
const USER_INFO_KEY = 'user_info'

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否为有效邮箱
 */
export function validateEmail(email) {
  if (!email || typeof email !== 'string') return false
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @returns {object} 验证结果
 */
export function validatePassword(password) {
  if (!password || typeof password !== 'string') {
    return {
      isValid: false,
      errors: ['密码长度至少8位']
    }
  }
  
  const errors = []
  
  // 检查密码长度
  if (password.length < 8) {
    errors.push('密码长度至少8位')
  }
  
  // 检查是否包含大写字母
  if (!/[A-Z]/.test(password)) {
    errors.push('密码必须包含至少一个大写字母')
  }
  
  // 检查是否包含小写字母
  if (!/[a-z]/.test(password)) {
    errors.push('密码必须包含至少一个小写字母')
  }
  
  // 检查是否包含至少两个数字
  const digits = (password.match(/\d/g) || []).length
  if (digits < 2) {
    errors.push('密码必须包含至少两个数字')
  }
  
  // 检查是否包含特殊字符
  if (!/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    errors.push('密码必须包含至少一个特殊字符')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

/**
 * 设置认证token
 * @param {string} token - JWT token
 * @param {boolean} rememberMe - 是否记住用户（持久化存储）
 */
export function setAuthToken(token, rememberMe = false) {
  try {
    if (rememberMe) {
      localStorage.setItem(TOKEN_KEY, token)
      sessionStorage.removeItem(TOKEN_KEY)
    } else {
      sessionStorage.setItem(TOKEN_KEY, token)
      localStorage.removeItem(TOKEN_KEY)
    }
  } catch (error) {
    console.error('Failed to set auth token:', error)
  }
}

/**
 * 获取认证token
 * @returns {string|null} token或null
 */
export function getAuthToken() {
  try {
    return localStorage.getItem(TOKEN_KEY) || sessionStorage.getItem(TOKEN_KEY)
  } catch (error) {
    console.error('Failed to get auth token:', error)
    return null
  }
}

/**
 * 移除认证token
 */
export function removeAuthToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
    sessionStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    sessionStorage.removeItem(REFRESH_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to remove auth token:', error)
  }
}

/**
 * 设置刷新token
 * @param {string} refreshToken - 刷新token
 */
export function setRefreshToken(refreshToken) {
  try {
    // 统一使用sessionStorage，不进行持久化存储
    sessionStorage.setItem(REFRESH_TOKEN_KEY, refreshToken)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to set refresh token:', error)
  }
}

/**
 * 获取刷新token
 * @returns {string|null} refresh token或null
 */
export function getRefreshToken() {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY) || sessionStorage.getItem(REFRESH_TOKEN_KEY)
  } catch (error) {
    console.error('Failed to get refresh token:', error)
    return null
  }
}

/**
 * 检查token是否过期
 * @param {string} token - JWT token
 * @returns {boolean} 是否过期
 */
export function isTokenExpired(token) {
  if (!token) return true
  
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    const currentTime = Math.floor(Date.now() / 1000)
    return payload.exp < currentTime
  } catch (error) {
    console.error('Failed to check token expiration:', error)
    return true
  }
}

// 用户信息管理
/**
 * 设置用户信息
 * @param {object} userInfo - 用户信息
 */
export function setUserInfo(userInfo) {
  try {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo))
  } catch (error) {
    console.error('Failed to set user info:', error)
  }
}

/**
 * 获取用户信息
 * @returns {object|null} 用户信息或null
 */
export function getUserInfo() {
  try {
    const userInfo = localStorage.getItem(USER_INFO_KEY)
    return userInfo ? JSON.parse(userInfo) : null
  } catch (error) {
    console.error('Failed to get user info:', error)
    return null
  }
}

/**
 * 移除用户信息
 */
export function removeUserInfo() {
  try {
    localStorage.removeItem(USER_INFO_KEY)
  } catch (error) {
    console.error('Failed to remove user info:', error)
  }
}

// 密码强度计算
/**
 * 计算密码强度
 * @param {string} password - 密码
 * @returns {object} 强度信息
 */
export function calculatePasswordStrength(password) {
  if (!password) {
    return { score: 0, level: '无', colorClass: 'bg-gray-300' }
  }
  
  let score = 0
  
  // 长度检查
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  
  // 字符类型检查 - 不包括特殊字符
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  if (/\d/.test(password)) score += 1
  
  // 确定等级和颜色
  let level, colorClass
  switch (score) {
    case 0:
    case 1:
      level = '很弱'
      colorClass = 'bg-red-500'
      break
    case 2:
      level = '较弱'
      colorClass = 'bg-orange-500'
      break
    case 3:
      level = '一般'
      colorClass = 'bg-yellow-500'
      break
    case 4:
      level = '强'  // 4分对应"强"
      colorClass = 'bg-green-500'  // 4分对应绿色（根据测试期望）
      break
    case 5:
    case 6:
      level = '很强'  // 5分及以上对应"很强"
      colorClass = 'bg-green-500'  // 5分及以上也是绿色
      break
    default:
      level = '很弱'
      colorClass = 'bg-red-500'
  }
  
  return { score, level, colorClass }
}

// 验证码生成和验证
/**
 * 生成验证码文本
 * @param {number} length - 验证码长度
 * @returns {string} 验证码
 */
export function generateCaptchaText(length = 4) {
  const chars = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 验证验证码
 * @param {string} input - 用户输入
 * @param {string} captcha - 正确验证码
 * @returns {boolean} 是否有效
 */
export function validateCaptcha(input, captcha) {
  if (!input || !captcha) return false
  return input.toUpperCase() === captcha.toUpperCase()
}

// 时间格式化
/**
 * 格式化最后登录时间
 * @param {string} timestamp - 时间戳
 * @returns {string} 格式化后的时间
 */
export function formatLastLoginTime(timestamp) {
  if (!timestamp) return '未知时间'
  
  try {
    const date = new Date(timestamp)
    if (isNaN(date.getTime())) return '未知时间'
    
    const now = new Date()
    const diff = now - date
    
    // 相对时间
    if (diff < 60000) return '刚刚'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
    if (diff < 86400000) return `${Math.floor(diff / 60000)}小时前`
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
    
    // 绝对时间
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '未知时间'
  }
}

// 通用工具函数
/**
 * 防抖函数
 * @param {function} func - 要防抖的函数
 * @param {number} delay - 延迟时间(ms)
 * @returns {function} 防抖后的函数
 */
export function debounce(func, delay) {
  let timeoutId
  return function(...args) {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => func.apply(this, args), delay)
  }
}

/**
 * 节流函数
 * @param {function} func - 要节流的函数
 * @param {number} limit - 时间间隔(ms)
 * @returns {function} 节流后的函数
 */
export function throttle(func, limit) {
  let inThrottle
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}

/**
 * 深拷贝
 * @param {any} obj - 要拷贝的对象
 * @param {WeakMap} visited - 用于检测循环引用
 * @returns {any} 拷贝后的对象
 */
export function deepClone(obj, visited = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj
  if (visited.has(obj)) return obj  // 如果已访问过，直接返回原对象，避免循环引用
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof Array) {
    visited.set(obj, true)
    return obj.map(item => deepClone(item, visited))
  }
  if (typeof obj === 'object') {
    visited.set(obj, true)
    const clonedObj = {}
    for (let key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key], visited)
      }
    }
    return clonedObj
  }
}

export default {
  validateEmail,
  validatePassword,
  setAuthToken,
  getAuthToken,
  removeAuthToken,
  setRefreshToken,
  getRefreshToken,
  isTokenExpired,
  setUserInfo,
  getUserInfo,
  removeUserInfo,
  calculatePasswordStrength,
  generateCaptchaText,
  validateCaptcha,
  formatLastLoginTime,
  debounce,
  throttle,
  deepClone
}