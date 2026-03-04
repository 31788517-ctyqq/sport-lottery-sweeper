// frontend/src/utils/date.js

/**
 * 日期时间处理工具
 */

// 日期格式化常量
export const DATE_FORMATS = {
  DATE: 'YYYY-MM-DD',
  DATETIME: 'YYYY-MM-DD HH:mm:ss',
  DATETIME_SHORT: 'YYYY-MM-DD HH:mm',
  TIME: 'HH:mm:ss',
  TIME_SHORT: 'HH:mm',
  MONTH_DAY: 'MM-DD',
  YEAR_MONTH: 'YYYY-MM',
  CHINESE_DATE: 'YYYY年MM月DD日',
  CHINESE_DATETIME: 'YYYY年MM月DD日 HH:mm:ss',
  RFC3339: 'YYYY-MM-DDTHH:mm:ssZ',
  ISO: 'YYYY-MM-DDTHH:mm:ss.SSSZ'
}

/**
 * 格式化日期时间
 * @param {Date|string|number} date - 日期对象或时间戳
 * @param {string} format - 格式字符串，默认为'YYYY-MM-DD HH:mm:ss'
 * @returns {string} 格式化后的日期字符串
 */
export function formatDate(date, format = DATE_FORMATS.DATETIME) {
  if (!date) return ''
  
  let dateObj
  if (date instanceof Date) {
    dateObj = date
  } else if (typeof date === 'string' || typeof date === 'number') {
    dateObj = new Date(date)
  } else {
    return ''
  }
  
  if (isNaN(dateObj.getTime())) return ''
  
  const pad = (num) => num.toString().padStart(2, '0')
  
  const tokens = {
    YYYY: dateObj.getFullYear(),
    YY: dateObj.getFullYear().toString().slice(-2),
    MM: pad(dateObj.getMonth() + 1),
    M: dateObj.getMonth() + 1,
    DD: pad(dateObj.getDate()),
    D: dateObj.getDate(),
    HH: pad(dateObj.getHours()),
    H: dateObj.getHours(),
    hh: pad(dateObj.getHours() % 12 || 12),
    h: dateObj.getHours() % 12 || 12,
    mm: pad(dateObj.getMinutes()),
    m: dateObj.getMinutes(),
    ss: pad(dateObj.getSeconds()),
    s: dateObj.getSeconds(),
    SSS: pad(dateObj.getMilliseconds(), 3),
    A: dateObj.getHours() < 12 ? 'AM' : 'PM',
    a: dateObj.getHours() < 12 ? 'am' : 'pm'
  }
  
  return format.replace(/YYYY|YY|MM|M|DD|D|HH|H|hh|h|mm|m|ss|s|SSS|A|a/g, (match) => tokens[match])
}

/**
 * 解析日期字符串
 * @param {string} dateString - 日期字符串
 * @param {string} format - 格式字符串
 * @returns {Date|null} 解析后的Date对象
 */
export function parseDate(dateString, format = DATE_FORMATS.DATE) {
  if (!dateString) return null
  
  try {
    // 简单实现，仅支持常见格式
    if (format === DATE_FORMATS.DATE) {
      const parts = dateString.split('-')
      if (parts.length === 3) {
        return new Date(parts[0], parts[1] - 1, parts[2])
      }
    } else if (format === DATE_FORMATS.DATETIME) {
      const [datePart, timePart] = dateString.split(' ')
      const dateParts = datePart.split('-')
      const timeParts = timePart.split(':')
      
      if (dateParts.length === 3 && timeParts.length === 3) {
        return new Date(
          dateParts[0], dateParts[1] - 1, dateParts[2],
          timeParts[0], timeParts[1], timeParts[2]
        )
      }
    }
    
    // 尝试使用Date构造函数
    const date = new Date(dateString)
    return isNaN(date.getTime()) ? null : date
  } catch {
    return null
  }
}

/**
 * 获取相对时间（如"刚刚"、"3分钟前"）
 * @param {Date|string|number} date - 日期对象或时间戳
 * @param {Date|string|number} baseDate - 基准日期，默认为当前时间
 * @returns {string} 相对时间字符串
 */
export function getRelativeTime(date, baseDate = new Date()) {
  const dateObj = date instanceof Date ? date : new Date(date)
  const baseDateObj = baseDate instanceof Date ? baseDate : new Date(baseDate)
  
  if (isNaN(dateObj.getTime())) return '无效日期'
  
  const diffMs = baseDateObj.getTime() - dateObj.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)
  const diffWeek = Math.floor(diffDay / 7)
  const diffMonth = Math.floor(diffDay / 30)
  const diffYear = Math.floor(diffDay / 365)
  
  if (diffSec < 5) return '刚刚'
  if (diffSec < 60) return `${diffSec}秒前`
  if (diffMin < 60) return `${diffMin}分钟前`
  if (diffHour < 24) return `${diffHour}小时前`
  if (diffDay < 7) return `${diffDay}天前`
  if (diffWeek < 4) return `${diffWeek}周前`
  if (diffMonth < 12) return `${diffMonth}个月前`
  return `${diffYear}年前`
}

/**
 * 获取比赛倒计时
 * @param {Date|string|number} matchTime - 比赛时间
 * @param {Date|string|number} currentTime - 当前时间，默认为现在
 * @returns {object} 倒计时对象
 */
export function getMatchCountdown(matchTime, currentTime = new Date()) {
  const matchDate = matchTime instanceof Date ? matchTime : new Date(matchTime)
  const currentDate = currentTime instanceof Date ? currentTime : new Date(currentTime)
  
  if (isNaN(matchDate.getTime())) {
    return {
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      totalSeconds: 0,
      isPast: true,
      display: '比赛时间无效'
    }
  }
  
  const diffMs = matchDate.getTime() - currentDate.getTime()
  const isPast = diffMs <= 0
  
  if (isPast) {
    return {
      days: 0,
      hours: 0,
      minutes: 0,
      seconds: 0,
      totalSeconds: 0,
      isPast: true,
      display: '比赛已开始'
    }
  }
  
  const totalSeconds = Math.floor(diffMs / 1000)
  const days = Math.floor(totalSeconds / (24 * 3600))
  const hours = Math.floor((totalSeconds % (24 * 3600)) / 3600)
  const minutes = Math.floor((totalSeconds % 3600) / 60)
  const seconds = totalSeconds % 60
  
  let display = ''
  if (days > 0) {
    display = `${days}天${hours}小时`
  } else if (hours > 0) {
    display = `${hours}小时${minutes}分`
  } else if (minutes > 0) {
    display = `${minutes}分${seconds}秒`
  } else {
    display = `${seconds}秒`
  }
  
  return {
    days,
    hours,
    minutes,
    seconds,
    totalSeconds,
    isPast,
    display
  }
}

/**
 * 获取日期范围
 * @param {string} period - 时间段
 * @returns {object} 包含开始和结束日期的对象
 */
export function getDateRange(period) {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  const periods = {
    today: {
      start: today,
      end: new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1)
    },
    yesterday: {
      start: new Date(today.getTime() - 24 * 60 * 60 * 1000),
      end: new Date(today.getTime() - 1)
    },
    thisWeek: {
      start: new Date(today.getTime() - today.getDay() * 24 * 60 * 60 * 1000),
      end: new Date(today.getTime() + (6 - today.getDay()) * 24 * 60 * 60 * 1000 + 24 * 60 * 60 * 1000 - 1)
    },
    lastWeek: {
      start: new Date(today.getTime() - (today.getDay() + 7) * 24 * 60 * 60 * 1000),
      end: new Date(today.getTime() - (today.getDay() + 1) * 24 * 60 * 60 * 1000 - 1)
    },
    thisMonth: {
      start: new Date(now.getFullYear(), now.getMonth(), 1),
      end: new Date(now.getFullYear(), now.getMonth() + 1, 0, 23, 59, 59, 999)
    },
    lastMonth: {
      start: new Date(now.getFullYear(), now.getMonth() - 1, 1),
      end: new Date(now.getFullYear(), now.getMonth(), 0, 23, 59, 59, 999)
    },
    thisYear: {
      start: new Date(now.getFullYear(), 0, 1),
      end: new Date(now.getFullYear() + 1, 0, 0, 23, 59, 59, 999)
    },
    lastYear: {
      start: new Date(now.getFullYear() - 1, 0, 1),
      end: new Date(now.getFullYear(), 0, 0, 23, 59, 59, 999)
    }
  }
  
  return periods[period] || {
    start: today,
    end: new Date(today.getTime() + 24 * 60 * 60 * 1000 - 1)
  }
}

/**
 * 计算两个日期之间的天数差
 * @param {Date|string|number} date1 - 日期1
 * @param {Date|string|number} date2 - 日期2
 * @returns {number} 天数差
 */
export function getDaysBetween(date1, date2 = new Date()) {
  const d1 = date1 instanceof Date ? date1 : new Date(date1)
  const d2 = date2 instanceof Date ? date2 : new Date(date2)
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) return 0
  
  const diffMs = Math.abs(d2.getTime() - d1.getTime())
  return Math.floor(diffMs / (1000 * 60 * 60 * 24))
}

/**
 * 添加天数
 * @param {Date|string|number} date - 日期
 * @param {number} days - 要添加的天数
 * @returns {Date} 新的日期对象
 */
export function addDays(date, days) {
  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return new Date()
  
  const result = new Date(dateObj)
  result.setDate(result.getDate() + days)
  return result
}

/**
 * 添加小时
 * @param {Date|string|number} date - 日期
 * @param {number} hours - 要添加的小时数
 * @returns {Date} 新的日期对象
 */
export function addHours(date, hours) {
  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return new Date()
  
  const result = new Date(dateObj)
  result.setHours(result.getHours() + hours)
  return result
}

/**
 * 获取比赛时间段
 * @param {Date|string|number} matchDate - 比赛日期
 * @returns {string} 时间段描述
 */
export function getMatchTimeSlot(matchDate) {
  const dateObj = matchDate instanceof Date ? matchDate : new Date(matchDate)
  if (isNaN(dateObj.getTime())) return '未知'
  
  const hour = dateObj.getHours()
  
  if (hour >= 0 && hour < 6) return '凌晨'
  if (hour >= 6 && hour < 9) return '早晨'
  if (hour >= 9 && hour < 12) return '上午'
  if (hour >= 12 && hour < 14) return '中午'
  if (hour >= 14 && hour < 18) return '下午'
  if (hour >= 18 && hour < 21) return '傍晚'
  return '晚上'
}

/**
 * 格式化比赛日期时间
 * @param {Date|string|number} matchDateTime - 比赛日期时间
 * @param {boolean} includeWeekday - 是否包含星期几
 * @returns {string} 格式化后的字符串
 */
export function formatMatchDateTime(matchDateTime, includeWeekday = true) {
  const dateObj = matchDateTime instanceof Date ? matchDateTime : new Date(matchDateTime)
  if (isNaN(dateObj.getTime())) return '时间待定'
  
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000)
  const yesterday = new Date(today.getTime() - 24 * 60 * 60 * 1000)
  
  const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  
  if (dateObj >= today && dateObj < tomorrow) {
    return `今天 ${formatDate(dateObj, 'HH:mm')}`
  } else if (dateObj >= yesterday && dateObj < today) {
    return `昨天 ${formatDate(dateObj, 'HH:mm')}`
  } else if (dateObj >= tomorrow && dateObj < new Date(tomorrow.getTime() + 24 * 60 * 60 * 1000)) {
    return `明天 ${formatDate(dateObj, 'HH:mm')}`
  } else {
    const weekday = weekdays[dateObj.getDay()]
    const datePart = formatDate(dateObj, 'MM-DD')
    const timePart = formatDate(dateObj, 'HH:mm')
    
    if (includeWeekday) {
      return `${datePart} ${weekday} ${timePart}`
    } else {
      return `${datePart} ${timePart}`
    }
  }
}

/**
 * 判断是否为同一天
 * @param {Date|string|number} date1 - 日期1
 * @param {Date|string|number} date2 - 日期2
 * @returns {boolean} 是否为同一天
 */
export function isSameDay(date1, date2) {
  const d1 = date1 instanceof Date ? date1 : new Date(date1)
  const d2 = date2 instanceof Date ? date2 : new Date(date2)
  
  if (isNaN(d1.getTime()) || isNaN(d2.getTime())) return false
  
  return (
    d1.getFullYear() === d2.getFullYear() &&
    d1.getMonth() === d2.getMonth() &&
    d1.getDate() === d2.getDate()
  )
}

/**
 * 获取年龄（根据出生日期）
 * @param {Date|string|number} birthDate - 出生日期
 * @param {Date|string|number} referenceDate - 参考日期，默认为当前日期
 * @returns {number} 年龄
 */
export function getAge(birthDate, referenceDate = new Date()) {
  const birth = birthDate instanceof Date ? birthDate : new Date(birthDate)
  const reference = referenceDate instanceof Date ? referenceDate : new Date(referenceDate)
  
  if (isNaN(birth.getTime()) || isNaN(reference.getTime())) return 0
  
  let age = reference.getFullYear() - birth.getFullYear()
  const monthDiff = reference.getMonth() - birth.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && reference.getDate() < birth.getDate())) {
    age--
  }
  
  return age
}

/**
 * 获取赛季年份
 * @param {Date|string|number} date - 日期
 * @returns {string} 赛季年份（如"2023-2024"）
 */
export function getSeasonYear(date = new Date()) {
  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return ''
  
  const year = dateObj.getFullYear()
  const month = dateObj.getMonth() + 1
  
  // 假设赛季从7月开始
  if (month >= 7) {
    return `${year}-${year + 1}`
  } else {
    return `${year - 1}-${year}`
  }
}

/**
 * 获取比赛日状态
 * @param {Date|string|number} matchDate - 比赛日期
 * @param {Date|string|number} currentDate - 当前日期
 * @returns {string} 状态（'past', 'today', 'future'）
 */
export function getMatchDayStatus(matchDate, currentDate = new Date()) {
  const match = matchDate instanceof Date ? matchDate : new Date(matchDate)
  const current = currentDate instanceof Date ? currentDate : new Date(currentDate)
  
  if (isNaN(match.getTime()) || isNaN(current.getTime())) return 'unknown'
  
  const matchDay = new Date(match.getFullYear(), match.getMonth(), match.getDate())
  const currentDay = new Date(current.getFullYear(), current.getMonth(), current.getDate())
  
  if (matchDay < currentDay) return 'past'
  if (matchDay > currentDay) return 'future'
  return 'today'
}

/**
 * 生成日期序列
 * @param {Date|string|number} startDate - 开始日期
 * @param {Date|string|number} endDate - 结束日期
 * @param {string} format - 格式
 * @returns {string[]} 日期序列
 */
export function generateDateSequence(startDate, endDate, format = DATE_FORMATS.DATE) {
  const start = startDate instanceof Date ? startDate : new Date(startDate)
  const end = endDate instanceof Date ? endDate : new Date(endDate)
  
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || start > end) {
    return []
  }
  
  const dates = []
  const current = new Date(start)
  
  while (current <= end) {
    dates.push(formatDate(current, format))
    current.setDate(current.getDate() + 1)
  }
  
  return dates
}

/**
 * 获取工作时间段
 * @param {Date|string|number} date - 日期
 * @returns {boolean} 是否为工作时间（9:00-18:00）
 */
export function isWorkingTime(date = new Date()) {
  const dateObj = date instanceof Date ? date : new Date(date)
  if (isNaN(dateObj.getTime())) return false
  
  const hour = dateObj.getHours()
  const day = dateObj.getDay()
  
  // 周一至周五，9:00-18:00
  return day >= 1 && day <= 5 && hour >= 9 && hour < 18
}

export default {
  DATE_FORMATS,
  formatDate,
  parseDate,
  getRelativeTime,
  getMatchCountdown,
  getDateRange,
  getDaysBetween,
  addDays,
  addHours,
  getMatchTimeSlot,
  formatMatchDateTime,
  isSameDay,
  getAge,
  getSeasonYear,
  getMatchDayStatus,
  generateDateSequence,
  isWorkingTime
}