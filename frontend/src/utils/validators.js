// frontend/src/utils/validators.js

/**
 * 表单验证工具
 */

// 正则表达式常量
const REGEX = {
  EMAIL: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/,
  PHONE: /^1[3-9]\d{9}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
  USERNAME: /^[a-zA-Z0-9_]{4,20}$/,
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  IP: /^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$/,
  DATE: /^\d{4}-\d{2}-\d{2}$/,
  TIME: /^([01]\d|2[0-3]):([0-5]\d)$/,
  NUMERIC: /^-?\d*\.?\d+$/,
  INTEGER: /^-?\d+$/,
  POSITIVE_INTEGER: /^\d+$/,
  CHINESE: /^[\u4e00-\u9fa5]+$/,
  ALPHANUMERIC: /^[a-zA-Z0-9]+$/,
  HEX_COLOR: /^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$/
}

/**
 * 必填字段验证
 * @param {*} value - 验证的值
 * @param {string} fieldName - 字段名称，用于错误消息
 * @returns {string|null} 错误消息或null
 */
export function required(value, fieldName = '该字段') {
  if (value === null || value === undefined) {
    return `${fieldName}不能为空`
  }
  
  if (typeof value === 'string' && value.trim() === '') {
    return `${fieldName}不能为空`
  }
  
  if (Array.isArray(value) && value.length === 0) {
    return `${fieldName}不能为空`
  }
  
  return null
}

/**
 * 邮箱验证
 * @param {string} email - 邮箱地址
 * @returns {string|null} 错误消息或null
 */
export function validateEmail(email) {
  if (!email) return '邮箱不能为空'
  if (!REGEX.EMAIL.test(email)) return '邮箱格式不正确'
  return null
}

/**
 * 手机号验证
 * @param {string} phone - 手机号码
 * @returns {string|null} 错误消息或null
 */
export function validatePhone(phone) {
  if (!phone) return '手机号不能为空'
  if (!REGEX.PHONE.test(phone)) return '手机号格式不正确'
  return null
}

/**
 * 密码强度验证
 * @param {string} password - 密码
 * @param {object} options - 配置选项
 * @returns {string|null} 错误消息或null
 */
export function validatePassword(password, options = {}) {
  const {
    minLength = 8,
    requireUppercase = true,
    requireLowercase = true,
    requireNumbers = true,
    requireSpecial = true
  } = options
  
  if (!password) return '密码不能为空'
  if (password.length < minLength) return `密码长度不能少于${minLength}位`
  
  if (requireUppercase && !/[A-Z]/.test(password)) {
    return '密码必须包含大写字母'
  }
  
  if (requireLowercase && !/[a-z]/.test(password)) {
    return '密码必须包含小写字母'
  }
  
  if (requireNumbers && !/\d/.test(password)) {
    return '密码必须包含数字'
  }
  
  if (requireSpecial && !/[@$!%*?&]/.test(password)) {
    return '密码必须包含特殊字符 (@$!%*?&)'
  }
  
  return null
}

/**
 * 用户名验证
 * @param {string} username - 用户名
 * @returns {string|null} 错误消息或null
 */
export function validateUsername(username) {
  if (!username) return '用户名不能为空'
  if (username.length < 4) return '用户名长度不能少于4位'
  if (username.length > 20) return '用户名长度不能超过20位'
  if (!REGEX.USERNAME.test(username)) return '用户名只能包含字母、数字和下划线'
  return null
}

/**
 * URL验证
 * @param {string} url - URL地址
 * @param {boolean} requireProtocol - 是否需要协议头
 * @returns {string|null} 错误消息或null
 */
export function validateURL(url, requireProtocol = false) {
  if (!url) return 'URL不能为空'
  
  if (requireProtocol && !url.startsWith('http://') && !url.startsWith('https://')) {
    return 'URL必须以http://或https://开头'
  }
  
  if (!REGEX.URL.test(url)) return 'URL格式不正确'
  return null
}

/**
 * 数字范围验证
 * @param {number} value - 数值
 * @param {object} options - 配置选项
 * @returns {string|null} 错误消息或null
 */
export function validateNumber(value, options = {}) {
  const {
    min = null,
    max = null,
    integer = false,
    positive = false,
    fieldName = '数值'
  } = options
  
  if (value === null || value === undefined || value === '') {
    return `${fieldName}不能为空`
  }
  
  const numValue = Number(value)
  if (isNaN(numValue)) return `${fieldName}必须是有效的数字`
  
  if (integer && !REGEX.INTEGER.test(value.toString())) {
    return `${fieldName}必须是整数`
  }
  
  if (positive && numValue <= 0) {
    return `${fieldName}必须是正数`
  }
  
  if (min !== null && numValue < min) {
    return `${fieldName}不能小于${min}`
  }
  
  if (max !== null && numValue > max) {
    return `${fieldName}不能大于${max}`
  }
  
  return null
}

/**
 * 赔率验证
 * @param {number} odds - 赔率值
 * @returns {string|null} 错误消息或null
 */
export function validateOdds(odds) {
  return validateNumber(odds, {
    min: 1.0,
    max: 1000,
    positive: true,
    fieldName: '赔率'
  })
}

/**
 * 日期验证
 * @param {string} date - 日期字符串
 * @param {object} options - 配置选项
 * @returns {string|null} 错误消息或null
 */
export function validateDate(date, options = {}) {
  const { 
    minDate = null,
    maxDate = null,
    format = 'YYYY-MM-DD',
    fieldName = '日期'
  } = options
  
  if (!date) return `${fieldName}不能为空`
  
  if (!REGEX.DATE.test(date)) {
    return `${fieldName}格式不正确，应为YYYY-MM-DD`
  }
  
  const dateObj = new Date(date)
  if (isNaN(dateObj.getTime())) {
    return `${fieldName}无效`
  }
  
  if (minDate) {
    const minDateObj = new Date(minDate)
    if (dateObj < minDateObj) {
      return `${fieldName}不能早于${minDate}`
    }
  }
  
  if (maxDate) {
    const maxDateObj = new Date(maxDate)
    if (dateObj > maxDateObj) {
      return `${fieldName}不能晚于${maxDate}`
    }
  }
  
  return null
}

/**
 * 时间验证
 * @param {string} time - 时间字符串
 * @returns {string|null} 错误消息或null
 */
export function validateTime(time) {
  if (!time) return '时间不能为空'
  if (!REGEX.TIME.test(time)) return '时间格式不正确，应为HH:MM'
  return null
}

/**
 * 比赛时间验证
 * @param {string} date - 日期
 * @param {string} time - 时间
 * @returns {string|null} 错误消息或null
 */
export function validateMatchDateTime(date, time) {
  const dateError = validateDate(date, { fieldName: '比赛日期' })
  if (dateError) return dateError
  
  const timeError = validateTime(time)
  if (timeError) return timeError
  
  // 验证比赛时间不能是过去时间（对于新建比赛）
  const matchTime = new Date(`${date}T${time}`)
  const now = new Date()
  
  if (matchTime < now) {
    return '比赛时间不能是过去时间'
  }
  
  return null
}

/**
 * 球队名称验证
 * @param {string} teamName - 球队名称
 * @returns {string|null} 错误消息或null
 */
export function validateTeamName(teamName) {
  if (!teamName) return '球队名称不能为空'
  if (teamName.length < 2) return '球队名称长度不能少于2位'
  if (teamName.length > 50) return '球队名称长度不能超过50位'
  return null
}

/**
 * 联赛名称验证
 * @param {string} leagueName - 联赛名称
 * @returns {string|null} 错误消息或null
 */
export function validateLeagueName(leagueName) {
  if (!leagueName) return '联赛名称不能为空'
  if (leagueName.length < 2) return '联赛名称长度不能少于2位'
  if (leagueName.length > 100) return '联赛名称长度不能超过100位'
  return null
}

/**
 * 球员姓名验证
 * @param {string} playerName - 球员姓名
 * @returns {string|null} 错误消息或null
 */
export function validatePlayerName(playerName) {
  if (!playerName) return '球员姓名不能为空'
  if (playerName.length < 2) return '球员姓名长度不能少于2位'
  if (playerName.length > 50) return '球员姓名长度不能超过50位'
  return null
}

/**
 * 球员号码验证
 * @param {number} number - 球员号码
 * @returns {string|null} 错误消息或null
 */
export function validatePlayerNumber(number) {
  return validateNumber(number, {
    min: 0,
    max: 99,
    integer: true,
    fieldName: '球员号码'
  })
}

/**
 * IP地址验证
 * @param {string} ip - IP地址
 * @returns {string|null} 错误消息或null
 */
export function validateIP(ip) {
  if (!ip) return 'IP地址不能为空'
  if (!REGEX.IP.test(ip)) return 'IP地址格式不正确'
  return null
}

/**
 * 端口号验证
 * @param {number} port - 端口号
 * @returns {string|null} 错误消息或null
 */
export function validatePort(port) {
  return validateNumber(port, {
    min: 1,
    max: 65535,
    integer: true,
    fieldName: '端口号'
  })
}

/**
 * 验证多个字段
 * @param {object} validations - 验证配置对象
 * @returns {object} 包含验证结果和错误消息的对象
 */
export function validateFields(validations) {
  const errors = {}
  let isValid = true
  
  for (const [fieldName, validation] of Object.entries(validations)) {
    const { value, rules } = validation
    
    for (const rule of rules) {
      const error = rule(value, fieldName)
      if (error) {
        errors[fieldName] = error
        isValid = false
        break
      }
    }
  }
  
  return { isValid, errors }
}

/**
 * 创建验证器函数
 * @param {object} schema - 验证模式
 * @returns {function} 验证器函数
 */
export function createValidator(schema) {
  return function (data) {
    const errors = {}
    let isValid = true
    
    for (const [field, rules] of Object.entries(schema)) {
      const value = data[field]
      
      for (const rule of rules) {
        const error = rule(value, field)
        if (error) {
          errors[field] = error
          isValid = false
          break
        }
      }
    }
    
    return { isValid, errors }
  }
}

/**
 * 比赛数据验证
 * @param {object} matchData - 比赛数据
 * @returns {object} 验证结果
 */
export function validateMatchData(matchData) {
  const schema = {
    homeTeam: [required, validateTeamName],
    awayTeam: [required, validateTeamName],
    league: [required, validateLeagueName],
    matchDate: [required, validateDate],
    matchTime: [required, validateTime]
  }
  
  return createValidator(schema)(matchData)
}

/**
 * 用户注册验证
 * @param {object} userData - 用户数据
 * @returns {object} 验证结果
 */
export function validateUserRegistration(userData) {
  const schema = {
    username: [required, validateUsername],
    email: [required, validateEmail],
    phone: [required, validatePhone],
    password: [required, (value) => validatePassword(value, {
      minLength: 8,
      requireUppercase: true,
      requireLowercase: true,
      requireNumbers: true,
      requireSpecial: true
    })]
  }
  
  return createValidator(schema)(userData)
}

/**
 * 登录表单验证
 * @param {object} loginData - 登录数据
 * @returns {object} 验证结果
 */
export function validateLogin(loginData) {
  const schema = {
    username: [required],
    password: [required]
  }
  
  return createValidator(schema)(loginData)
}

export default {
  required,
  validateEmail,
  validatePhone,
  validatePassword,
  validateUsername,
  validateURL,
  validateNumber,
  validateOdds,
  validateDate,
  validateTime,
  validateMatchDateTime,
  validateTeamName,
  validateLeagueName,
  validatePlayerName,
  validatePlayerNumber,
  validateIP,
  validatePort,
  validateFields,
  createValidator,
  validateMatchData,
  validateUserRegistration,
  validateLogin,
  REGEX
}