// frontend/src/utils/string.js

/**
 * 字符串处理工具
 */

/**
 * 转换为驼峰命名
 * @param {string} str - 原始字符串
 * @returns {string} 驼峰命名字符串
 */
export function toCamelCase(str) {
  if (!str) return ''
  
  return str
    .replace(/[-_\s]+(.)?/g, (_, c) => c ? c.toUpperCase() : '')
    .replace(/^(.)/, (c) => c.toLowerCase())
}

/**
 * 转换为帕斯卡命名
 * @param {string} str - 原始字符串
 * @returns {string} 帕斯卡命名字符串
 */
export function toPascalCase(str) {
  if (!str) return ''
  
  const camelCase = toCamelCase(str)
  return camelCase.charAt(0).toUpperCase() + camelCase.slice(1)
}

/**
 * 转换为蛇形命名
 * @param {string} str - 原始字符串
 * @returns {string} 蛇形命名字符串
 */
export function toSnakeCase(str) {
  if (!str) return ''
  
  return str
    .replace(/([A-Z])/g, '_$1')
    .replace(/[-_\s]+/g, '_')
    .toLowerCase()
    .replace(/^_|_$/g, '')
}

/**
 * 转换为连字符命名
 * @param {string} str - 原始字符串
 * @returns {string} 连字符命名字符串
 */
export function toKebabCase(str) {
  if (!str) return ''
  
  return str
    .replace(/([A-Z])/g, '-$1')
    .replace(/[-_\s]+/g, '-')
    .toLowerCase()
    .replace(/^-|-$/g, '')
}

/**
 * 首字母大写
 * @param {string} str - 原始字符串
 * @returns {string} 首字母大写的字符串
 */
export function capitalize(str) {
  if (!str) return ''
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase()
}

/**
 * 每个单词首字母大写
 * @param {string} str - 原始字符串
 * @returns {string} 每个单词首字母大写的字符串
 */
export function capitalizeWords(str) {
  if (!str) return ''
  
  return str
    .split(/\s+/)
    .map(word => capitalize(word))
    .join(' ')
}

/**
 * 截断字符串
 * @param {string} str - 原始字符串
 * @param {number} length - 最大长度
 * @param {string} suffix - 后缀，默认为'...'
 * @returns {string} 截断后的字符串
 */
export function truncate(str, length = 100, suffix = '...') {
  if (!str) return ''
  
  if (str.length <= length) return str
  
  return str.substring(0, length - suffix.length) + suffix
}

/**
 * 截断中间字符串
 * @param {string} str - 原始字符串
 * @param {number} startLength - 开始部分长度
 * @param {number} endLength - 结束部分长度
 * @param {string} separator - 分隔符，默认为'...'
 * @returns {string} 截断后的字符串
 */
export function truncateMiddle(str, startLength = 10, endLength = 10, separator = '...') {
  if (!str) return ''
  
  if (str.length <= startLength + endLength + separator.length) {
    return str
  }
  
  const start = str.substring(0, startLength)
  const end = str.substring(str.length - endLength)
  
  return start + separator + end
}

/**
 * 移除HTML标签
 * @param {string} html - 包含HTML的字符串
 * @returns {string} 纯文本字符串
 */
export function stripHtmlTags(html) {
  if (!html) return ''
  
  return html.replace(/<[^>]*>/g, '')
}

/**
 * 移除多余空格
 * @param {string} str - 原始字符串
 * @returns {string} 处理后的字符串
 */
export function normalizeSpaces(str) {
  if (!str) return ''
  
  return str
    .replace(/\s+/g, ' ')
    .trim()
}

/**
 * 生成随机字符串
 * @param {number} length - 字符串长度
 * @param {string} charset - 字符集，默认为字母数字
 * @returns {string} 随机字符串
 */
export function randomString(length = 10, charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789') {
  let result = ''
  const charsetLength = charset.length
  
  for (let i = 0; i < length; i++) {
    result += charset.charAt(Math.floor(Math.random() * charsetLength))
  }
  
  return result
}

/**
 * 生成球队缩写
 * @param {string} teamName - 球队全名
 * @returns {string} 球队缩写
 */
export function generateTeamAbbreviation(teamName) {
  if (!teamName) return ''
  
  // 移除常见前缀和后缀
  const cleaned = teamName
    .replace(/^(FC|SC|SV|TSV|VfB|VfL|1\.|Borussia|Real|Atletico|AC|AS|Inter|Juventus|Olympique|Paris|Manchester|Liverpool|Chelsea|Arsenal|Tottenham)\s+/i, '')
    .replace(/\s+(FC|United|City|Hotspur|Wanderers|Rovers|Athletic|Club|Sporting|Stadium)$/i, '')
  
  // 提取首字母
  const words = cleaned.split(/\s+/)
  if (words.length >= 2) {
    return words
      .map(word => word.charAt(0).toUpperCase())
      .join('')
      .substring(0, 3)
  }
  
  // 如果只有一个单词，取前三个字母
  return cleaned.substring(0, 3).toUpperCase()
}

/**
 * 生成球员号码显示
 * @param {number|string} number - 球员号码
 * @returns {string} 格式化后的号码
 */
export function formatPlayerNumber(number) {
  if (number === null || number === undefined) return ''
  
  const num = Number(number)
  if (isNaN(num)) return String(number)
  
  return num < 10 ? `0${num}` : String(num)
}

/**
 * 生成联赛简称
 * @param {string} leagueName - 联赛全名
 * @returns {string} 联赛简称
 */
export function generateLeagueShortName(leagueName) {
  if (!leagueName) return ''
  
  const shortNames = {
    '英格兰足球超级联赛': '英超',
    '西班牙足球甲级联赛': '西甲',
    '德国足球甲级联赛': '德甲',
    '意大利足球甲级联赛': '意甲',
    '法国足球甲级联赛': '法甲',
    '中国足球协会超级联赛': '中超',
    '欧洲冠军联赛': '欧冠',
    '欧罗巴联赛': '欧联',
    '欧洲协会联赛': '欧协联',
    '英格兰足球冠军联赛': '英冠',
    '西班牙足球乙级联赛': '西乙',
    '德国足球乙级联赛': '德乙',
    '意大利足球乙级联赛': '意乙'
  }
  
  return shortNames[leagueName] || leagueName
}

/**
 * 生成比赛标题
 * @param {string} homeTeam - 主队名称
 * @param {string} awayTeam - 客队名称
 * @returns {string} 比赛标题
 */
export function generateMatchTitle(homeTeam, awayTeam) {
  if (!homeTeam || !awayTeam) return ''
  
  const homeAbbr = generateTeamAbbreviation(homeTeam)
  const awayAbbr = generateTeamAbbreviation(awayTeam)
  
  return `${homeAbbr} vs ${awayAbbr}`
}

/**
 * 生成情报摘要
 * @param {string} content - 情报内容
 * @param {number} maxLength - 最大长度
 * @returns {string} 情报摘要
 */
export function generateIntelligenceSummary(content, maxLength = 100) {
  if (!content) return ''
  
  // 移除HTML标签和多余空格
  const cleanContent = stripHtmlTags(content)
    .replace(/\s+/g, ' ')
    .trim()
  
  return truncate(cleanContent, maxLength)
}

/**
 * 生成赔率变化描述
 * @param {number} oldOdds - 旧赔率
 * @param {number} newOdds - 新赔率
 * @returns {string} 赔率变化描述
 */
export function generateOddsChangeDescription(oldOdds, newOdds) {
  if (oldOdds === null || newOdds === null) {
    return '赔率暂无变化'
  }
  
  const change = newOdds - oldOdds
  const percentChange = (change / oldOdds) * 100
  
  if (Math.abs(percentChange) < 0.1) {
    return '赔率基本稳定'
  }
  
  const direction = change > 0 ? '上升' : '下降'
  const absPercent = Math.abs(percentChange).toFixed(1)
  
  return `赔率${direction}${absPercent}%`
}

/**
 * 生成伤病状态描述
 * @param {string} status - 伤病状态
 * @param {string} expectedReturn - 预计回归时间
 * @returns {string} 伤病状态描述
 */
export function generateInjuryDescription(status, expectedReturn) {
  if (!status) return '状态正常'
  
  const statusMap = {
    'doubtful': '出战存疑',
    'out': '确认缺席',
    'injured': '受伤',
    'suspended': '停赛',
    'rested': '轮休'
  }
  
  const description = statusMap[status] || status
  
  if (expectedReturn) {
    return `${description}，预计${expectedReturn}回归`
  }
  
  return description
}

/**
 * 生成天气描述
 * @param {string} condition - 天气状况
 * @param {number} temperature - 温度
 * @returns {string} 天气描述
 */
export function generateWeatherDescription(condition, temperature) {
  if (!condition) return '天气信息未知'
  
  const conditionMap = {
    'sunny': '晴朗',
    'cloudy': '多云',
    'partly_cloudy': '局部多云',
    'rainy': '雨天',
    'stormy': '雷雨',
    'snowy': '雪天',
    'foggy': '雾天',
    'windy': '大风'
  }
  
  const chineseCondition = conditionMap[condition] || condition
  
  if (temperature !== null && temperature !== undefined) {
    return `${chineseCondition}，${temperature}°C`
  }
  
  return chineseCondition
}

/**
 * 生成裁判信息描述
 * @param {string} refereeName - 裁判姓名
 * @param {object} stats - 裁判统计数据
 * @returns {string} 裁判信息描述
 */
export function generateRefereeDescription(refereeName, stats = {}) {
  if (!refereeName) return '裁判未确定'
  
  const parts = [refereeName]
  
  if (stats.avgCardsPerGame) {
    parts.push(`场均${stats.avgCardsPerGame.toFixed(1)}张牌`)
  }
  
  if (stats.avgFoulsPerGame) {
    parts.push(`场均${stats.avgFoulsPerGame.toFixed(1)}次犯规`)
  }
  
  return parts.join('，')
}

/**
 * 生成战术描述
 * @param {string} formation - 阵型
 * @param {string} style - 战术风格
 * @returns {string} 战术描述
 */
export function generateTacticsDescription(formation, style) {
  const parts = []
  
  if (formation) {
    parts.push(`${formation}阵型`)
  }
  
  if (style) {
    const styleMap = {
      'attacking': '进攻型',
      'defensive': '防守型',
      'possession': '控球型',
      'counter': '反击型',
      'pressing': '高压逼抢'
    }
    
    parts.push(styleMap[style] || style)
  }
  
  return parts.join('，') || '战术信息未知'
}

/**
 * 格式化比赛统计数据
 * @param {object} stats - 统计数据
 * @returns {string} 格式化后的统计描述
 */
export function formatMatchStats(stats) {
  if (!stats) return '暂无统计'
  
  const parts = []
  
  if (stats.possession !== undefined) {
    parts.push(`控球率${stats.possession}%`)
  }
  
  if (stats.shots !== undefined) {
    parts.push(`${stats.shots}次射门`)
  }
  
  if (stats.shotsOnTarget !== undefined) {
    parts.push(`${stats.shotsOnTarget}次射正`)
  }
  
  if (stats.corners !== undefined) {
    parts.push(`${stats.corners}个角球`)
  }
  
  if (stats.fouls !== undefined) {
    parts.push(`${stats.fouls}次犯规`)
  }
  
  if (stats.yellowCards !== undefined) {
    parts.push(`${stats.yellowCards}张黄牌`)
  }
  
  if (stats.redCards !== undefined) {
    parts.push(`${stats.redCards}张红牌`)
  }
  
  return parts.join('，') || '暂无详细统计'
}

/**
 * 生成球员技术统计描述
 * @param {object} playerStats - 球员统计数据
 * @returns {string} 技术统计描述
 */
export function generatePlayerStatsDescription(playerStats) {
  if (!playerStats) return '暂无技术统计'
  
  const parts = []
  
  if (playerStats.goals !== undefined && playerStats.goals > 0) {
    parts.push(`${playerStats.goals}球`)
  }
  
  if (playerStats.assists !== undefined && playerStats.assists > 0) {
    parts.push(`${playerStats.assists}助`)
  }
  
  if (playerStats.passes !== undefined) {
    parts.push(`${playerStats.passes}次传球`)
  }
  
  if (playerStats.passAccuracy !== undefined) {
    parts.push(`${playerStats.passAccuracy}%传球成功率`)
  }
  
  if (playerStats.tackles !== undefined) {
    parts.push(`${playerStats.tackles}次抢断`)
  }
  
  if (playerStats.interceptions !== undefined) {
    parts.push(`${playerStats.interceptions}次拦截`)
  }
  
  return parts.join('，') || '暂无详细统计'
}

/**
 * 生成社交媒体摘要
 * @param {string} content - 社交媒体内容
 * @param {number} maxLength - 最大长度
 * @returns {string} 摘要
 */
export function generateSocialMediaSummary(content, maxLength = 140) {
  if (!content) return ''
  
  // 移除URL和@提及
  const cleanContent = content
    .replace(/https?:\/\/\S+/g, '')
    .replace(/@\w+/g, '')
    .replace(/#\w+/g, '')
    .replace(/\s+/g, ' ')
    .trim()
  
  return truncate(cleanContent, maxLength)
}

/**
 * 生成数据源可靠性描述
 * @param {string} source - 数据源
 * @param {number} reliability - 可靠性评分（0-100）
 * @returns {string} 可靠性描述
 */
export function generateSourceReliabilityDescription(source, reliability) {
  if (!source) return '来源未知'
  
  let level = '一般'
  let color = '#666'
  
  if (reliability >= 90) {
    level = '极高'
    color = '#4CAF50'
  } else if (reliability >= 70) {
    level = '高'
    color = '#8BC34A'
  } else if (reliability >= 50) {
    level = '中等'
    color = '#FFC107'
  } else if (reliability >= 30) {
    level = '较低'
    color = '#FF9800'
  } else {
    level = '低'
    color = '#F44336'
  }
  
  return `<span style="color: ${color}">${source} (${level})</span>`
}

/**
 * 生成比赛预测摘要
 * @param {object} prediction - 预测数据
 * @returns {string} 预测摘要
 */
export function generatePredictionSummary(prediction) {
  if (!prediction) return '暂无预测'
  
  const parts = []
  
  if (prediction.homeWinProbability !== undefined) {
    parts.push(`主胜: ${(prediction.homeWinProbability * 100).toFixed(1)}%`)
  }
  
  if (prediction.drawProbability !== undefined) {
    parts.push(`平局: ${(prediction.drawProbability * 100).toFixed(1)}%`)
  }
  
  if (prediction.awayWinProbability !== undefined) {
    parts.push(`客胜: ${(prediction.awayWinProbability * 100).toFixed(1)}%`)
  }
  
  if (prediction.expectedGoals !== undefined) {
    parts.push(`预期进球: ${prediction.expectedGoals.toFixed(1)}`)
  }
  
  return parts.join(' | ')
}

/**
 * 生成风险等级描述
 * @param {number} riskLevel - 风险等级（0-10）
 * @returns {string} 风险描述
 */
export function generateRiskLevelDescription(riskLevel) {
  if (riskLevel === undefined || riskLevel === null) {
    return '风险未知'
  }
  
  let level = ''
  let color = ''
  
  if (riskLevel >= 8) {
    level = '极高风险'
    color = '#F44336'
  } else if (riskLevel >= 6) {
    level = '高风险'
    color = '#FF9800'
  } else if (riskLevel >= 4) {
    level = '中等风险'
    color = '#FFC107'
  } else if (riskLevel >= 2) {
    level = '低风险'
    color = '#8BC34A'
  } else {
    level = '极低风险'
    color = '#4CAF50'
  }
  
  return `<span style="color: ${color}">${level}</span>`
}

/**
 * 生成密码强度描述
 * @param {string} password - 密码
 * @returns {object} 包含强度和描述的
 */
export function generatePasswordStrength(password) {
  if (!password) {
    return { score: 0, level: '无', description: '未输入密码' }
  }
  
  let score = 0
  const descriptions = []
  
  // 长度检查
  if (password.length >= 8) score += 1
  if (password.length >= 12) score += 1
  
  // 大小写字母检查
  if (/[a-z]/.test(password)) score += 1
  if (/[A-Z]/.test(password)) score += 1
  
  // 数字检查
  if (/\d/.test(password)) score += 1
  
  // 特殊字符检查
  if (/[^a-zA-Z0-9]/.test(password)) score += 1
  
  // 生成描述
  let level = '弱'
  let color = '#F44336'
  
  if (score >= 5) {
    level = '强'
    color = '#4CAF50'
  } else if (score >= 3) {
    level = '中等'
    color = '#FFC107'
  }
  
  return {
    score,
    level,
    color,
    description: `密码强度: ${level}`
  }
}

export default {
  toCamelCase,
  toPascalCase,
  toSnakeCase,
  toKebabCase,
  capitalize,
  capitalizeWords,
  truncate,
  truncateMiddle,
  stripHtmlTags,
  normalizeSpaces,
  randomString,
  generateTeamAbbreviation,
  formatPlayerNumber,
  generateLeagueShortName,
  generateMatchTitle,
  generateIntelligenceSummary,
  generateOddsChangeDescription,
  generateInjuryDescription,
  generateWeatherDescription,
  generateRefereeDescription,
  generateTacticsDescription,
  formatMatchStats,
  generatePlayerStatsDescription,
  generateSocialMediaSummary,
  generateSourceReliabilityDescription,
  generatePredictionSummary,
  generateRiskLevelDescription,
  generatePasswordStrength
}