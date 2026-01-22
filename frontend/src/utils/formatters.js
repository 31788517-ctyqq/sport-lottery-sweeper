// frontend/src/utils/formatters.js

/**
 * 数字格式化工具
 */

/**
 * 格式化货币数字
 * @param {number} value - 数值
 * @param {string} currency - 货币符号，默认为空
 * @param {number} decimals - 小数位数，默认为2
 * @returns {string} 格式化后的货币字符串
 */
export function formatCurrency(value, currency = '', decimals = 2) {
  if (value === null || value === undefined) return 'N/A'
  
  const numValue = Number(value)
  if (isNaN(numValue)) return 'N/A'
  
  const fixedValue = numValue.toFixed(decimals)
  const parts = fixedValue.split('.')
  const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const decimalPart = parts[1] ? `.${parts[1]}` : ''
  
  return `${currency}${integerPart}${decimalPart}`
}

/**
 * 格式化百分比
 * @param {number} value - 数值（0-1之间）
 * @param {number} decimals - 小数位数，默认为1
 * @param {boolean} withSymbol - 是否包含百分号，默认为true
 * @returns {string} 格式化后的百分比字符串
 */
export function formatPercent(value, decimals = 1, withSymbol = true) {
  if (value === null || value === undefined) return 'N/A'
  
  const numValue = Number(value) * 100
  if (isNaN(numValue)) return 'N/A'
  
  const symbol = withSymbol ? '%' : ''
  return `${numValue.toFixed(decimals)}${symbol}`
}

/**
 * 格式化赔率（保留两位小数）
 * @param {number} odds - 赔率值
 * @returns {string} 格式化后的赔率字符串
 */
export function formatOdds(odds) {
  if (odds === null || odds === undefined) return 'N/A'
  
  const numOdds = Number(odds)
  if (isNaN(numOdds)) return 'N/A'
  
  return numOdds.toFixed(2)
}

/**
 * 格式化数字缩写（如1.5K、2.3M）
 * @param {number} value - 数值
 * @param {number} decimals - 小数位数，默认为1
 * @returns {string} 缩写后的字符串
 */
export function formatAbbreviation(value, decimals = 1) {
  if (value === null || value === undefined) return 'N/A'
  
  const numValue = Number(value)
  if (isNaN(numValue)) return 'N/A'
  
  const absValue = Math.abs(numValue)
  const sign = numValue < 0 ? '-' : ''
  
  if (absValue >= 1000000000) {
    return `${sign}${(absValue / 1000000000).toFixed(decimals)}B`
  }
  if (absValue >= 1000000) {
    return `${sign}${(absValue / 1000000).toFixed(decimals)}M`
  }
  if (absValue >= 1000) {
    return `${sign}${(absValue / 1000).toFixed(decimals)}K`
  }
  
  return `${sign}${absValue.toFixed(decimals)}`
}

/**
 * 格式化比赛得分
 * @param {number} homeScore - 主队得分
 * @param {number} awayScore - 客队得分
 * @returns {string} 格式化后的比分字符串
 */
export function formatScore(homeScore, awayScore) {
  const home = homeScore === null || homeScore === undefined ? '-' : homeScore
  const away = awayScore === null || awayScore === undefined ? '-' : awayScore
  return `${home} - ${away}`
}

/**
 * 格式化球队名称缩写
 * @param {string} teamName - 球队全名
 * @param {number} maxLength - 最大长度，默认为3
 * @returns {string} 缩写后的球队名称
 */
export function formatTeamAbbreviation(teamName, maxLength = 3) {
  if (!teamName || typeof teamName !== 'string') return 'N/A'
  
  // 移除特殊字符和空格，取前三个字符大写
  const cleaned = teamName.replace(/[^a-zA-Z]/g, '').toUpperCase()
  return cleaned.substring(0, maxLength)
}

/**
 * 格式化比赛时间状态
 * @param {string} status - 比赛状态
 * @param {number} minute - 比赛分钟数
 * @returns {string} 格式化后的状态字符串
 */
export function formatMatchStatus(status, minute = null) {
  const statusMap = {
    'scheduled': '未开始',
    'live': minute ? `${minute}'` : '进行中',
    'halftime': '中场休息',
    'finished': '已结束',
    'postponed': '延期',
    'cancelled': '取消',
    'abandoned': '中止'
  }
  
  return statusMap[status] || status
}

/**
 * 格式化数据置信度
 * @param {number} confidence - 置信度（0-1）
 * @returns {string} 置信度描述
 */
export function formatConfidence(confidence) {
  if (confidence >= 0.9) return '极高'
  if (confidence >= 0.7) return '高'
  if (confidence >= 0.5) return '中'
  if (confidence >= 0.3) return '低'
  return '极低'
}

/**
 * 格式化文件大小
 * @param {number} bytes - 字节数
 * @param {number} decimals - 小数位数，默认为2
 * @returns {string} 格式化后的文件大小
 */
export function formatFileSize(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const dm = decimals < 0 ? 0 : decimals
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']
  
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i]
}

/**
 * 格式化社交数字（点赞、评论等）
 * @param {number} count - 数量
 * @returns {string} 格式化后的社交数字
 */
export function formatSocialCount(count) {
  if (count === null || count === undefined) return '0'
  
  const numCount = Number(count)
  if (isNaN(numCount)) return '0'
  
  if (numCount >= 1000000) {
    return (numCount / 1000000).toFixed(1).replace(/\.0$/, '') + 'M'
  }
  if (numCount >= 1000) {
    return (numCount / 1000).toFixed(1).replace(/\.0$/, '') + 'K'
  }
  return numCount.toString()
}

/**
 * 格式化比赛赔率变化趋势
 * @param {number} oldOdds - 旧赔率
 * @param {number} newOdds - 新赔率
 * @returns {object} 包含变化值和方向的格式化对象
 */
export function formatOddsChange(oldOdds, newOdds) {
  if (oldOdds === null || newOdds === null) {
    return { value: 'N/A', direction: 'neutral', change: 0 }
  }
  
  const change = newOdds - oldOdds
  const percentChange = (change / oldOdds) * 100
  
  let direction = 'neutral'
  if (change > 0) direction = 'up'
  else if (change < 0) direction = 'down'
  
  return {
    value: newOdds.toFixed(2),
    direction,
    change: change.toFixed(2),
    percentChange: percentChange.toFixed(2),
    rawChange: change
  }
}

/**
 * 格式化球员评分
 * @param {number} rating - 评分（0-10）
 * @returns {object} 格式化后的评分对象
 */
export function formatPlayerRating(rating) {
  if (rating === null || rating === undefined) {
    return { value: 'N/A', color: '#999', level: '暂无评分' }
  }
  
  const numRating = Number(rating)
  
  let color = '#999'
  let level = '一般'
  
  if (numRating >= 8.5) {
    color = '#4CAF50'
    level = '杰出'
  } else if (numRating >= 7.5) {
    color = '#8BC34A'
    level = '优秀'
  } else if (numRating >= 6.5) {
    color = '#FFC107'
    level = '良好'
  } else if (numRating >= 5.5) {
    color = '#FF9800'
    level = '及格'
  } else {
    color = '#F44336'
    level = '较差'
  }
  
  return {
    value: numRating.toFixed(1),
    color,
    level
  }
}

export default {
  formatCurrency,
  formatPercent,
  formatOdds,
  formatAbbreviation,
  formatScore,
  formatTeamAbbreviation,
  formatMatchStatus,
  formatConfidence,
  formatFileSize,
  formatSocialCount,
  formatOddsChange,
  formatPlayerRating
}