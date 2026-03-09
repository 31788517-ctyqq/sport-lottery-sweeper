// frontend/src/utils/helpers.js

/**
 * 通用辅助函数
 */

/**
 * 生成唯一ID
 * @param {number} length - ID长度，默认为16
 * @returns {string} 唯一ID
 */
export function generateId(length = 16) {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  let result = ''
  for (let i = 0; i < length; i++) {
    result += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  return result
}

/**
 * 生成UUID
 * @returns {string} UUID字符串
 */
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

/**
 * 深度克隆对象
 * @param {*} obj - 要克隆的对象
 * @returns {*} 克隆后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof RegExp) return new RegExp(obj)
  
  if (Array.isArray(obj)) {
    const cloneArr = []
    for (let i = 0; i < obj.length; i++) {
      cloneArr[i] = deepClone(obj[i])
    }
    return cloneArr
  }
  
  const cloneObj = {}
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloneObj[key] = deepClone(obj[key])
    }
  }
  return cloneObj
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间（毫秒）
 * @param {boolean} immediate - 是否立即执行
 * @returns {Function} 防抖后的函数
 */
export function debounce(func, wait = 300, immediate = false) {
  let timeout
  
  return function executedFunction(...args) {
    const context = this
    
    const later = function() {
      timeout = null
      if (!immediate) func.apply(context, args)
    }
    
    const callNow = immediate && !timeout
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
    
    if (callNow) func.apply(context, args)
  }
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 限制时间（毫秒）
 * @returns {Function} 节流后的函数
 */
export function throttle(func, limit = 300) {
  let inThrottle
  let lastFunc
  let lastRan
  
  return function(...args) {
    const context = this
    
    if (!inThrottle) {
      func.apply(context, args)
      lastRan = Date.now()
      inThrottle = true
    } else {
      clearTimeout(lastFunc)
      lastFunc = setTimeout(function() {
        if (Date.now() - lastRan >= limit) {
          func.apply(context, args)
          lastRan = Date.now()
        }
      }, limit - (Date.now() - lastRan))
    }
  }
}

/**
 * 格式化错误对象
 * @param {Error|any} error - 错误对象
 * @returns {string} 格式化后的错误信息
 */
export function formatError(error) {
  if (!error) return '未知错误'
  
  if (typeof error === 'string') return error
  
  if (error.message) return error.message
  
  if (error.response && error.response.data) {
    if (typeof error.response.data === 'string') {
      return error.response.data
    }
    if (error.response.data.message) {
      return error.response.data.message
    }
    if (error.response.data.error) {
      return error.response.data.error
    }
    return JSON.stringify(error.response.data)
  }
  
  return error.toString()
}

/**
 * 睡眠函数（等待指定时间）
 * @param {number} ms - 等待的毫秒数
 * @returns {Promise} Promise对象
 */
export function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

/**
 * 安全执行函数，捕获异常
 * @param {Function} func - 要执行的函数
 * @param {*} defaultValue - 默认返回值
 * @param {...any} args - 函数参数
 * @returns {*} 函数执行结果或默认值
 */
export function safeExecute(func, defaultValue = null, ...args) {
  try {
    return func(...args)
  } catch (error) {
    console.error('函数执行失败:', error)
    return defaultValue
  }
}

/**
 * 检测运行环境
 * @returns {object} 环境信息对象
 */
export function getEnvironment() {
  const userAgent = navigator.userAgent.toLowerCase()
  
  return {
    isMobile: /mobile|iphone|ipad|android/.test(userAgent),
    isIOS: /iphone|ipad|ipod/.test(userAgent),
    isAndroid: /android/.test(userAgent),
    isWeChat: /micromessenger/.test(userAgent),
    isQQ: /qq\//.test(userAgent),
    isPC: !/mobile|iphone|ipad|android/.test(userAgent),
    browser: {
      isChrome: /chrome/.test(userAgent),
      isFirefox: /firefox/.test(userAgent),
      isSafari: /safari/.test(userAgent) && !/chrome/.test(userAgent),
      isEdge: /edg/.test(userAgent),
      isIE: /msie|trident/.test(userAgent)
    },
    platform: navigator.platform,
    language: navigator.language
  }
}

/**
 * 检测网络状态
 * @returns {Promise<boolean>} 是否有网络连接
 */
export function checkNetworkStatus() {
  return navigator.onLine
}

/**
 * 获取URL参数
 * @param {string} name - 参数名
 * @param {string} url - URL字符串，默认为当前URL
 * @returns {string|null} 参数值
 */
export function getUrlParam(name, url = window.location.href) {
  const params = new URLSearchParams(new URL(url).search)
  return params.get(name)
}

/**
 * 获取所有URL参数
 * @param {string} url - URL字符串，默认为当前URL
 * @returns {object} 参数对象
 */
export function getAllUrlParams(url = window.location.href) {
  const params = new URLSearchParams(new URL(url).search)
  const result = {}
  
  for (const [key, value] of params.entries()) {
    result[key] = value
  }
  
  return result
}

/**
 * 构建URL查询字符串
 * @param {object} params - 参数对象
 * @returns {string} 查询字符串
 */
export function buildQueryString(params) {
  const searchParams = new URLSearchParams()
  
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined) {
      searchParams.append(key, String(value))
    }
  }
  
  return searchParams.toString()
}

/**
 * 格式化文件类型
 * @param {string} filename - 文件名
 * @returns {string} 文件类型
 */
export function getFileType(filename) {
  if (!filename) return 'unknown'
  
  const extension = filename.split('.').pop().toLowerCase()
  
  const typeMap = {
    // 图片
    jpg: 'image', jpeg: 'image', png: 'image', gif: 'image',
    bmp: 'image', svg: 'image', webp: 'image',
    
    // 文档
    pdf: 'pdf',
    doc: 'word', docx: 'word',
    xls: 'excel', xlsx: 'excel',
    ppt: 'powerpoint', pptx: 'powerpoint',
    txt: 'text',
    
    // 压缩文件
    zip: 'archive', rar: 'archive', '7z': 'archive',
    tar: 'archive', gz: 'archive',
    
    // 音视频
    mp3: 'audio', wav: 'audio', ogg: 'audio',
    mp4: 'video', avi: 'video', mov: 'video',
    mkv: 'video', flv: 'video',
    
    // 代码
    js: 'javascript', ts: 'typescript',
    html: 'html', htm: 'html',
    css: 'css',
    json: 'json', xml: 'xml'
  }
  
  return typeMap[extension] || 'unknown'
}

/**
 * 生成随机颜色
 * @param {number} alpha - 透明度（0-1）
 * @returns {string} 颜色字符串
 */
export function getRandomColor(alpha = 1) {
  const r = Math.floor(Math.random() * 256)
  const g = Math.floor(Math.random() * 256)
  const b = Math.floor(Math.random() * 256)
  
  return alpha < 1 
    ? `rgba(${r}, ${g}, ${b}, ${alpha})`
    : `rgb(${r}, ${g}, ${b})`
}

/**
 * 获取球队主色调
 * @param {string} teamName - 球队名称
 * @returns {string} 颜色值
 */
export function getTeamColor(teamName) {
  if (!teamName) return '#999999'
  
  // 常见球队颜色映射
  const teamColors = {
    '皇家马德里': '#00529F',
    '巴塞罗那': '#A50044',
    '曼联': '#DA291C',
    '曼城': '#6CABDD',
    '利物浦': '#C8102E',
    '切尔西': '#034694',
    '阿森纳': '#EF0107',
    '拜仁慕尼黑': '#DC052D',
    '多特蒙德': '#FDE100',
    '尤文图斯': '#000000',
    'AC米兰': '#000000',
    '国际米兰': '#00529F',
    '巴黎圣日耳曼': '#004170',
    '马德里竞技': '#CB3524'
  }
  
  // 如果没有预定义颜色，使用哈希算法生成
  if (teamColors[teamName]) {
    return teamColors[teamName]
  }
  
  let hash = 0
  for (let i = 0; i < teamName.length; i++) {
    hash = teamName.charCodeAt(i) + ((hash << 5) - hash)
  }
  
  const hue = hash % 360
  return `hsl(${hue}, 70%, 50%)`
}

/**
 * 判断是否为空值
 * @param {*} value - 要判断的值
 * @returns {boolean} 是否为空
 */
export function isEmpty(value) {
  if (value === null || value === undefined) return true
  if (typeof value === 'string' && value.trim() === '') return true
  if (Array.isArray(value) && value.length === 0) return true
  if (typeof value === 'object' && Object.keys(value).length === 0) return true
  return false
}

/**
 * 格式化数据为可读字符串
 * @param {*} data - 数据
 * @returns {string} 可读字符串
 */
export function toReadableString(data) {
  if (data === null) return 'null'
  if (data === undefined) return 'undefined'
  
  if (typeof data === 'boolean') return data ? '是' : '否'
  if (typeof data === 'number') return data.toString()
  if (typeof data === 'string') return data
  
  if (Array.isArray(data)) {
    return `[${data.map(item => toReadableString(item)).join(', ')}]`
  }
  
  if (typeof data === 'object') {
    try {
      return JSON.stringify(data, null, 2)
    } catch {
      return '[Object]'
    }
  }
  
  return String(data)
}

/**
 * 比较两个比赛是否相同
 * @param {object} match1 - 比赛1
 * @param {object} match2 - 比赛2
 * @returns {boolean} 是否相同
 */
export function isSameMatch(match1, match2) {
  if (!match1 || !match2) return false
  
  return (
    match1.id === match2.id ||
    (match1.homeTeam === match2.homeTeam &&
     match1.awayTeam === match2.awayTeam &&
     match1.matchDate === match2.matchDate)
  )
}

/**
 * 计算比赛重要度分数
 * @param {object} match - 比赛对象
 * @returns {number} 重要度分数（0-100）
 */
export function calculateMatchImportance(match) {
  if (!match) return 0
  
  let score = 0
  
  // 联赛级别（权重：40%）
  const leagueLevels = {
    '世界杯': 100,
    '欧洲杯': 95,
    '欧冠': 90,
    '英超': 85,
    '西甲': 85,
    '德甲': 80,
    '意甲': 80,
    '法甲': 75,
    '中超': 60
  }
  
  score += (leagueLevels[match.league] || 50) * 0.4
  
  // 比赛阶段（权重：30%）
  const stageLevels = {
    '决赛': 100,
    '半决赛': 90,
    '四分之一决赛': 80,
    '淘汰赛': 70,
    '小组赛': 60,
    '常规赛': 50,
    '友谊赛': 30
  }
  
  score += (stageLevels[match.stage] || 50) * 0.3
  
  // 球队排名（权重：30%）
  const avgRank = (match.homeTeamRank + match.awayTeamRank) / 2
  const rankScore = Math.max(0, 100 - avgRank)
  score += rankScore * 0.3
  
  return Math.min(100, Math.round(score))
}

/**
 * 生成数据加载占位符
 * @param {number} count - 占位符数量
 * @returns {array} 占位符数组
 */
export function generatePlaceholders(count) {
  return Array.from({ length: count }, (_, i) => ({
    id: `placeholder-${i}`,
    isLoading: true
  }))
}

/**
 * 检测页面可见性
 * @returns {boolean} 页面是否可见
 */
export function isPageVisible() {
  if (typeof document === 'undefined') return true
  
  if (document.visibilityState) {
    return document.visibilityState === 'visible'
  }
  
  return true
}

/**
 * 监听页面可见性变化
 * @param {Function} callback - 回调函数
 * @returns {Function} 清理函数
 */
export function onPageVisibilityChange(callback) {
  if (typeof document === 'undefined' || !document.addEventListener) {
    return () => {}
  }
  
  const handler = () => {
    callback(isPageVisible())
  }
  
  document.addEventListener('visibilitychange', handler)
  
  return () => {
    document.removeEventListener('visibilitychange', handler)
  }
}

/**
 * 复制文本到剪贴板
 * @param {string} text - 要复制的文本
 * @returns {Promise<boolean>} 是否复制成功
 */
export async function copyToClipboard(text) {
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
    
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    return true
  } catch (error) {
    console.error('复制失败:', error)
    return false
  }
}

/**
 * 下载文件
 * @param {string} content - 文件内容
 * @param {string} filename - 文件名
 * @param {string} type - MIME类型
 */
export function downloadFile(content, filename, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  
  URL.revokeObjectURL(url)
}

export default {
  generateId,
  generateUUID,
  deepClone,
  debounce,
  throttle,
  formatError,
  sleep,
  safeExecute,
  getEnvironment,
  checkNetworkStatus,
  getUrlParam,
  getAllUrlParams,
  buildQueryString,
  getFileType,
  getRandomColor,
  getTeamColor,
  isEmpty,
  toReadableString,
  isSameMatch,
  calculateMatchImportance,
  generatePlaceholders,
  isPageVisible,
  onPageVisibilityChange,
  copyToClipboard,
  downloadFile
}