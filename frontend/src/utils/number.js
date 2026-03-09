// frontend/src/utils/number.js

/**
 * 数字处理工具
 */

/**
 * 安全转换为数字
 * @param {*} value - 要转换的值
 * @param {number} defaultValue - 默认值，默认为0
 * @returns {number} 转换后的数字
 */
export function safeNumber(value, defaultValue = 0) {
  if (value === null || value === undefined) return defaultValue
  
  const num = Number(value)
  return isNaN(num) ? defaultValue : num
}

/**
 * 限制数字范围
 * @param {number} value - 原始值
 * @param {number} min - 最小值
 * @param {number} max - 最大值
 * @returns {number} 限制后的值
 */
export function clamp(value, min, max) {
  const num = safeNumber(value, min)
  return Math.min(Math.max(num, min), max)
}

/**
 * 将数字限制为整数
 * @param {number} value - 原始值
 * @param {object} options - 配置选项
 * @returns {number} 整数
 */
export function toInteger(value, options = {}) {
  const { min = null, max = null, defaultValue = 0 } = options
  
  let num = safeNumber(value, defaultValue)
  
  // 取整
  num = Math.round(num)
  
  // 应用范围限制
  if (min !== null) num = Math.max(num, min)
  if (max !== null) num = Math.min(num, max)
  
  return num
}

/**
 * 格式化数字（添加千位分隔符）
 * @param {number} value - 数值
 * @param {number} decimals - 小数位数
 * @returns {string} 格式化后的数字字符串
 */
export function formatNumber(value, decimals = 0) {
  const num = safeNumber(value, 0)
  
  // 处理小数
  const fixed = num.toFixed(decimals)
  
  // 添加千位分隔符
  const parts = fixed.split('.')
  parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  
  return parts.join('.')
}

/**
 * 计算百分比
 * @param {number} part - 部分值
 * @param {number} total - 总值
 * @param {number} decimals - 小数位数
 * @returns {number} 百分比
 */
export function calculatePercentage(part, total, decimals = 1) {
  const partNum = safeNumber(part, 0)
  const totalNum = safeNumber(total, 1)
  
  if (totalNum === 0) return 0
  
  const percentage = (partNum / totalNum) * 100
  return parseFloat(percentage.toFixed(decimals))
}

/**
 * 计算平均值
 * @param {number[]} numbers - 数字数组
 * @returns {number} 平均值
 */
export function calculateAverage(numbers) {
  if (!Array.isArray(numbers) || numbers.length === 0) return 0
  
  const validNumbers = numbers.filter(n => typeof n === 'number' && !isNaN(n))
  if (validNumbers.length === 0) return 0
  
  const sum = validNumbers.reduce((acc, num) => acc + num, 0)
  return sum / validNumbers.length
}

/**
 * 计算加权平均值
 * @param {number[]} values - 值数组
 * @param {number[]} weights - 权重数组
 * @returns {number} 加权平均值
 */
export function calculateWeightedAverage(values, weights) {
  if (!Array.isArray(values) || !Array.isArray(weights) || 
      values.length !== weights.length || values.length === 0) {
    return 0
  }
  
  let sumProducts = 0
  let sumWeights = 0
  
  for (let i = 0; i < values.length; i++) {
    const value = safeNumber(values[i], 0)
    const weight = safeNumber(weights[i], 0)
    
    sumProducts += value * weight
    sumWeights += weight
  }
  
  return sumWeights === 0 ? 0 : sumProducts / sumWeights
}

/**
 * 计算标准差
 * @param {number[]} numbers - 数字数组
 * @param {boolean} isSample - 是否为样本标准差
 * @returns {number} 标准差
 */
export function calculateStandardDeviation(numbers, isSample = true) {
  if (!Array.isArray(numbers) || numbers.length < 2) return 0
  
  const avg = calculateAverage(numbers)
  const squaredDiffs = numbers.map(num => Math.pow(num - avg, 2))
  const variance = calculateAverage(squaredDiffs)
  
  // 样本标准差使用 n-1，总体标准差使用 n
  const divisor = isSample ? numbers.length - 1 : numbers.length
  const sampleVariance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / divisor
  
  return Math.sqrt(sampleVariance)
}

/**
 * 计算赔率期望值
 * @param {number} odds - 赔率
 * @param {number} probability - 概率（0-1）
 * @returns {number} 期望值
 */
export function calculateOddsExpectedValue(odds, probability) {
  const oddsNum = safeNumber(odds, 0)
  const probNum = clamp(safeNumber(probability, 0), 0, 1)
  
  return oddsNum * probNum - 1
}

/**
 * 计算凯利公式
 * @param {number} probability - 胜率（0-1）
 * @param {number} odds - 赔率
 * @param {number} bankroll - 资金比例（0-1）
 * @returns {number} 最佳投注比例
 */
export function calculateKellyCriterion(probability, odds, bankroll = 1) {
  const p = clamp(safeNumber(probability, 0), 0, 1)
  const b = safeNumber(odds, 1) - 1
  const q = 1 - p
  
  if (b <= 0) return 0
  
  const kelly = (p * b - q) / b
  const fraction = clamp(kelly, 0, 1) * bankroll
  
  return fraction
}

/**
 * 计算复利
 * @param {number} principal - 本金
 * @param {number} rate - 利率（小数形式）
 * @param {number} periods - 期数
 * @param {number} contributions - 每期追加金额
 * @returns {number} 最终金额
 */
export function calculateCompoundInterest(principal, rate, periods, contributions = 0) {
  const P = safeNumber(principal, 0)
  const r = safeNumber(rate, 0)
  const n = toInteger(periods, { min: 0 })
  const C = safeNumber(contributions, 0)
  
  if (r === 0) return P + C * n
  
  const amount = P * Math.pow(1 + r, n) + 
                 C * (Math.pow(1 + r, n) - 1) / r
  
  return amount
}

/**
 * 计算胜率
 * @param {number} wins - 胜利次数
 * @param {number} total - 总次数
 * @returns {number} 胜率（0-1）
 */
export function calculateWinRate(wins, total) {
  const winsNum = safeNumber(wins, 0)
  const totalNum = safeNumber(total, 0)
  
  if (totalNum === 0) return 0
  
  return clamp(winsNum / totalNum, 0, 1)
}

/**
 * 计算赔率转换
 * @param {number} decimalOdds - 十进制赔率
 * @param {string} format - 目标格式（'fractional', 'american', 'percentage'）
 * @returns {string|number} 转换后的赔率
 */
export function convertOdds(decimalOdds, format = 'fractional') {
  const odds = safeNumber(decimalOdds, 1)
  
  switch (format) {
    case 'fractional':
      // 转换为分数赔率
      const numerator = odds - 1
      if (numerator === 0) return '0/1'
      
      // 简化分数
      const gcd = (a, b) => b === 0 ? a : gcd(b, a % b)
      const denominator = 1
      const divisor = gcd(numerator * 100, denominator * 100)
      
      return `${(numerator * 100) / divisor}/${(denominator * 100) / divisor}`
      
    case 'american':
      // 转换为美式赔率
      if (odds >= 2) {
        return `+${Math.round((odds - 1) * 100)}`
      } else if (odds > 1) {
        return `-${Math.round(100 / (odds - 1))}`
      } else {
        return '0'
      }
      
    case 'percentage':
      // 转换为隐含概率
      const probability = (1 / odds) * 100
      return `${probability.toFixed(1)}%`
      
    default:
      return odds.toFixed(2)
  }
}

/**
 * 计算置信区间
 * @param {number[]} data - 数据数组
 * @param {number} confidenceLevel - 置信水平（0-1）
 * @returns {object} 置信区间
 */
export function calculateConfidenceInterval(data, confidenceLevel = 0.95) {
  if (!Array.isArray(data) || data.length < 2) {
    return { lower: 0, upper: 0, mean: 0 }
  }
  
  const mean = calculateAverage(data)
  const stdDev = calculateStandardDeviation(data, true)
  const n = data.length
  
  // Z分数（95%置信水平对应1.96）
  const zScore = 1.96 // 简单实现，实际应根据confidenceLevel查表
  
  const margin = zScore * (stdDev / Math.sqrt(n))
  
  return {
    lower: mean - margin,
    upper: mean + margin,
    mean,
    margin
  }
}

/**
 * 计算皮尔逊相关系数
 * @param {number[]} x - 变量X
 * @param {number[]} y - 变量Y
 * @returns {number} 相关系数
 */
export function calculateCorrelation(x, y) {
  if (!Array.isArray(x) || !Array.isArray(y) || 
      x.length !== y.length || x.length < 2) {
    return 0
  }
  
  const n = x.length
  
  // 计算平均值
  const meanX = calculateAverage(x)
  const meanY = calculateAverage(y)
  
  // 计算协方差和标准差
  let covariance = 0
  let stdDevX = 0
  let stdDevY = 0
  
  for (let i = 0; i < n; i++) {
    const diffX = x[i] - meanX
    const diffY = y[i] - meanY
    
    covariance += diffX * diffY
    stdDevX += diffX * diffX
    stdDevY += diffY * diffY
  }
  
  if (stdDevX === 0 || stdDevY === 0) return 0
  
  return covariance / Math.sqrt(stdDevX * stdDevY)
}

/**
 * 线性插值
 * @param {number} x - 输入值
 * @param {number[]} xValues - X值数组
 * @param {number[]} yValues - Y值数组
 * @returns {number} 插值结果
 */
export function linearInterpolation(x, xValues, yValues) {
  if (!Array.isArray(xValues) || !Array.isArray(yValues) || 
      xValues.length !== yValues.length || xValues.length < 2) {
    return 0
  }
  
  // 找到x所在的区间
  let i = 0
  while (i < xValues.length - 1 && x > xValues[i + 1]) {
    i++
  }
  
  if (i === xValues.length - 1) {
    return yValues[yValues.length - 1]
  }
  
  if (i === 0 && x < xValues[0]) {
    return yValues[0]
  }
  
  // 线性插值公式: y = y1 + (x - x1) * (y2 - y1) / (x2 - x1)
  const x1 = xValues[i]
  const x2 = xValues[i + 1]
  const y1 = yValues[i]
  const y2 = yValues[i + 1]
  
  return y1 + (x - x1) * (y2 - y1) / (x2 - x1)
}

/**
 * 计算移动平均
 * @param {number[]} data - 数据数组
 * @param {number} windowSize - 窗口大小
 * @returns {number[]} 移动平均值数组
 */
export function calculateMovingAverage(data, windowSize = 5) {
  if (!Array.isArray(data) || data.length < windowSize) {
    return data || []
  }
  
  const result = []
  const size = Math.min(windowSize, data.length)
  
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - size + 1)
    const end = i + 1
    const window = data.slice(start, end)
    
    const avg = calculateAverage(window)
    result.push(avg)
  }
  
  return result
}

/**
 * 计算指数移动平均
 * @param {number[]} data - 数据数组
 * @param {number} smoothingFactor - 平滑因子（0-1）
 * @returns {number[]} 指数移动平均值数组
 */
export function calculateExponentialMovingAverage(data, smoothingFactor = 0.2) {
  if (!Array.isArray(data) || data.length === 0) {
    return []
  }
  
  const result = [data[0]]
  const alpha = clamp(smoothingFactor, 0, 1)
  
  for (let i = 1; i < data.length; i++) {
    const ema = alpha * data[i] + (1 - alpha) * result[i - 1]
    result.push(ema)
  }
  
  return result
}

/**
 * 计算球员评分
 * @param {object} stats - 球员统计数据
 * @returns {number} 综合评分（0-10）
 */
export function calculatePlayerRating(stats) {
  if (!stats) return 5.0
  
  const weights = {
    goals: 2.0,
    assists: 1.5,
    passAccuracy: 0.05,
    tackles: 0.3,
    interceptions: 0.2,
    clearances: 0.1,
    saves: 0.5,
    keyPasses: 0.4,
    dribbles: 0.3,
    aerialDuelsWon: 0.2
  }
  
  let totalScore = 5.0 // 基准分
  
  for (const [stat, weight] of Object.entries(weights)) {
    const value = safeNumber(stats[stat], 0)
    totalScore += value * weight
  }
  
  return clamp(totalScore, 0, 10)
}

/**
 * 计算球队实力评分
 * @param {object} teamData - 球队数据
 * @returns {number} 实力评分（0-100）
 */
export function calculateTeamStrength(teamData) {
  if (!teamData) return 50
  
  const factors = {
    // 近期战绩（权重：30%）
    recentForm: teamData.recentForm || 0.5,
    
    // 主客场表现（权重：25%）
    homePerformance: teamData.homePerformance || 0.5,
    awayPerformance: teamData.awayPerformance || 0.5,
    
    // 进攻能力（权重：20%）
    attackStrength: teamData.attackStrength || 0.5,
    
    // 防守能力（权重：15%）
    defenseStrength: teamData.defenseStrength || 0.5,
    
    // 伤病影响（权重：10%）
    injuryImpact: teamData.injuryImpact || 0.5
  }
  
  const weights = {
    recentForm: 0.3,
    homePerformance: 0.125,
    awayPerformance: 0.125,
    attackStrength: 0.2,
    defenseStrength: 0.15,
    injuryImpact: 0.1
  }
  
  let totalScore = 0
  
  for (const [factor, weight] of Object.entries(weights)) {
    totalScore += factors[factor] * weight * 100
  }
  
  return clamp(totalScore, 0, 100)
}

/**
 * 计算情报置信度
 * @param {object} intelligence - 情报数据
 * @returns {number} 置信度（0-1）
 */
export function calculateIntelligenceConfidence(intelligence) {
  if (!intelligence) return 0
  
  const factors = {
    // 来源可靠性（权重：40%）
    sourceReliability: intelligence.sourceReliability || 0.5,
    
    // 时效性（权重：30%）
    timeliness: intelligence.timeliness || 0.5,
    
    // 一致性（权重：20%）
    consistency: intelligence.consistency || 0.5,
    
    // 详细程度（权重：10%）
    detailLevel: intelligence.detailLevel || 0.5
  }
  
  const weights = {
    sourceReliability: 0.4,
    timeliness: 0.3,
    consistency: 0.2,
    detailLevel: 0.1
  }
  
  let confidence = 0
  
  for (const [factor, weight] of Object.entries(weights)) {
    confidence += factors[factor] * weight
  }
  
  return clamp(confidence, 0, 1)
}

/**
 * 计算风险评分
 * @param {object} factors - 风险因素
 * @returns {number} 风险评分（0-10）
 */
export function calculateRiskScore(factors) {
  if (!factors) return 5
  
  const riskFactors = {
    // 比赛重要性（权重：25%）
    matchImportance: factors.matchImportance || 0.5,
    
    // 数据不确定性（权重：20%）
    dataUncertainty: factors.dataUncertainty || 0.5,
    
    // 市场波动性（权重：20%）
    marketVolatility: factors.marketVolatility || 0.5,
    
    // 外部因素（权重：15%）
    externalFactors: factors.externalFactors || 0.5,
    
    // 历史表现（权重：10%）
    historicalPerformance: factors.historicalPerformance || 0.5,
    
    // 分析师分歧（权重：10%）
    analystDivergence: factors.analystDivergence || 0.5
  }
  
  const weights = {
    matchImportance: 0.25,
    dataUncertainty: 0.2,
    marketVolatility: 0.2,
    externalFactors: 0.15,
    historicalPerformance: 0.1,
    analystDivergence: 0.1
  }
  
  let riskScore = 0
  
  for (const [factor, weight] of Object.entries(weights)) {
    riskScore += riskFactors[factor] * weight * 10
  }
  
  return clamp(riskScore, 0, 10)
}

export default {
  safeNumber,
  clamp,
  toInteger,
  formatNumber,
  calculatePercentage,
  calculateAverage,
  calculateWeightedAverage,
  calculateStandardDeviation,
  calculateOddsExpectedValue,
  calculateKellyCriterion,
  calculateCompoundInterest,
  calculateWinRate,
  convertOdds,
  calculateConfidenceInterval,
  calculateCorrelation,
  linearInterpolation,
  calculateMovingAverage,
  calculateExponentialMovingAverage,
  calculatePlayerRating,
  calculateTeamStrength,
  calculateIntelligenceConfidence,
  calculateRiskScore
}