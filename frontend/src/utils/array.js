// frontend/src/utils/array.js

/**
 * 数组处理工具
 */

/**
 * 数组去重
 * @param {Array} array - 原始数组
 * @param {Function} keyFn - 用于比较的key函数
 * @returns {Array} 去重后的数组
 */
export function unique(array, keyFn = null) {
  if (!Array.isArray(array)) return []
  
  if (keyFn) {
    const seen = new Set()
    return array.filter(item => {
      const key = keyFn(item)
      if (seen.has(key)) return false
      seen.add(key)
      return true
    })
  }
  
  return [...new Set(array)]
}

/**
 * 数组分块
 * @param {Array} array - 原始数组
 * @param {number} size - 块大小
 * @returns {Array} 分块后的二维数组
 */
export function chunk(array, size = 1) {
  if (!Array.isArray(array) || size < 1) return []
  
  const result = []
  for (let i = 0; i < array.length; i += size) {
    result.push(array.slice(i, i + size))
  }
  
  return result
}

/**
 * 数组扁平化
 * @param {Array} array - 原始数组
 * @param {number} depth - 扁平化深度
 * @returns {Array} 扁平化后的数组
 */
export function flatten(array, depth = 1) {
  if (!Array.isArray(array)) return []
  
  return array.flat(depth)
}

/**
 * 深度扁平化
 * @param {Array} array - 原始数组
 * @returns {Array} 完全扁平化的数组
 */
export function flattenDeep(array) {
  if (!Array.isArray(array)) return []
  
  const result = []
  
  function flattenRecursive(arr) {
    for (const item of arr) {
      if (Array.isArray(item)) {
        flattenRecursive(item)
      } else {
        result.push(item)
      }
    }
  }
  
  flattenRecursive(array)
  return result
}

/**
 * 数组分组
 * @param {Array} array - 原始数组
 * @param {Function} keyFn - 分组key函数
 * @returns {Object} 分组后的对象
 */
export function groupBy(array, keyFn) {
  if (!Array.isArray(array) || typeof keyFn !== 'function') {
    return {}
  }
  
  return array.reduce((result, item) => {
    const key = keyFn(item)
    if (!result[key]) {
      result[key] = []
    }
    result[key].push(item)
    return result
  }, {})
}

/**
 * 数组排序
 * @param {Array} array - 原始数组
 * @param {string|Function} key - 排序键或比较函数
 * @param {string} order - 排序顺序（'asc' 或 'desc'）
 * @returns {Array} 排序后的数组
 */
export function sortBy(array, key, order = 'asc') {
  if (!Array.isArray(array)) return []
  
  const sortOrder = order.toLowerCase() === 'desc' ? -1 : 1
  
  return [...array].sort((a, b) => {
    let aValue, bValue
    
    if (typeof key === 'function') {
      aValue = key(a)
      bValue = key(b)
    } else if (typeof key === 'string') {
      aValue = getProperty(a, key)
      bValue = getProperty(b, key)
    } else {
      aValue = a
      bValue = b
    }
    
    if (aValue < bValue) return -1 * sortOrder
    if (aValue > bValue) return 1 * sortOrder
    return 0
  })
}

/**
 * 获取对象属性（支持点符号）
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径
 * @returns {*} 属性值
 */
function getProperty(obj, path) {
  return path.split('.').reduce((current, key) => {
    return current ? current[key] : undefined
  }, obj)
}

/**
 * 数组过滤（支持复杂条件）
 * @param {Array} array - 原始数组
 * @param {Object|Function} condition - 过滤条件
 * @returns {Array} 过滤后的数组
 */
export function filter(array, condition) {
  if (!Array.isArray(array)) return []
  
  if (typeof condition === 'function') {
    return array.filter(condition)
  }
  
  if (typeof condition === 'object') {
    return array.filter(item => {
      return Object.entries(condition).every(([key, value]) => {
        if (typeof value === 'function') {
          return value(getProperty(item, key))
        }
        
        if (Array.isArray(value)) {
          return value.includes(getProperty(item, key))
        }
        
        return getProperty(item, key) === value
      })
    })
  }
  
  return array.filter(item => Boolean(item))
}

/**
 * 数组查找
 * @param {Array} array - 原始数组
 * @param {Function} predicate - 查找条件函数
 * @param {number} fromIndex - 起始索引
 * @returns {*} 找到的元素或undefined
 */
export function find(array, predicate, fromIndex = 0) {
  if (!Array.isArray(array)) return undefined
  
  for (let i = fromIndex; i < array.length; i++) {
    if (predicate(array[i], i, array)) {
      return array[i]
    }
  }
  
  return undefined
}

/**
 * 数组查找（从后往前）
 * @param {Array} array - 原始数组
 * @param {Function} predicate - 查找条件函数
 * @param {number} fromIndex - 起始索引
 * @returns {*} 找到的元素或undefined
 */
export function findLast(array, predicate, fromIndex = array.length - 1) {
  if (!Array.isArray(array)) return undefined
  
  for (let i = fromIndex; i >= 0; i--) {
    if (predicate(array[i], i, array)) {
      return array[i]
    }
  }
  
  return undefined
}

/**
 * 获取数组中的最大值
 * @param {Array} array - 数组
 * @param {Function} iteratee - 迭代函数
 * @returns {*} 最大值
 */
export function max(array, iteratee = null) {
  if (!Array.isArray(array) || array.length === 0) return undefined
  
  if (iteratee) {
    return array.reduce((maxItem, item) => {
      const maxValue = iteratee(maxItem)
      const currentValue = iteratee(item)
      return currentValue > maxValue ? item : maxItem
    })
  }
  
  return Math.max(...array)
}

/**
 * 获取数组中的最小值
 * @param {Array} array - 数组
 * @param {Function} iteratee - 迭代函数
 * @returns {*} 最小值
 */
export function min(array, iteratee = null) {
  if (!Array.isArray(array) || array.length === 0) return undefined
  
  if (iteratee) {
    return array.reduce((minItem, item) => {
      const minValue = iteratee(minItem)
      const currentValue = iteratee(item)
      return currentValue < minValue ? item : minItem
    })
  }
  
  return Math.min(...array)
}

/**
 * 获取数组总和
 * @param {Array} array - 数组
 * @param {Function} iteratee - 迭代函数
 * @returns {number} 总和
 */
export function sum(array, iteratee = null) {
  if (!Array.isArray(array) || array.length === 0) return 0
  
  if (iteratee) {
    return array.reduce((total, item) => total + (iteratee(item) || 0), 0)
  }
  
  return array.reduce((total, num) => total + (num || 0), 0)
}

/**
 * 获取数组平均值
 * @param {Array} array - 数组
 * @param {Function} iteratee - 迭代函数
 * @returns {number} 平均值
 */
export function mean(array, iteratee = null) {
  if (!Array.isArray(array) || array.length === 0) return 0
  
  const total = sum(array, iteratee)
  const count = iteratee ? array.length : array.filter(n => n != null).length
  
  return count === 0 ? 0 : total / count
}

/**
 * 随机打乱数组
 * @param {Array} array - 原始数组
 * @returns {Array} 打乱后的数组
 */
export function shuffle(array) {
  if (!Array.isArray(array)) return []
  
  const result = [...array]
  
  for (let i = result.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[result[i], result[j]] = [result[j], result[i]]
  }
  
  return result
}

/**
 * 随机获取数组元素
 * @param {Array} array - 数组
 * @param {number} count - 要获取的数量
 * @returns {Array|*} 随机元素
 */
export function sample(array, count = 1) {
  if (!Array.isArray(array) || array.length === 0) {
    return count === 1 ? undefined : []
  }
  
  if (count === 1) {
    const index = Math.floor(Math.random() * array.length)
    return array[index]
  }
  
  const shuffled = shuffle(array)
  return shuffled.slice(0, Math.min(count, array.length))
}

/**
 * 数组交集
 * @param {Array} arrays - 多个数组
 * @returns {Array} 交集数组
 */
export function intersection(...arrays) {
  if (arrays.length === 0) return []
  
  return arrays.reduce((a, b) => {
    if (!Array.isArray(a) || !Array.isArray(b)) return []
    return a.filter(item => b.includes(item))
  })
}

/**
 * 数组并集
 * @param {Array} arrays - 多个数组
 * @returns {Array} 并集数组
 */
export function union(...arrays) {
  if (arrays.length === 0) return []
  
  const result = []
  const seen = new Set()
  
  for (const array of arrays) {
    if (Array.isArray(array)) {
      for (const item of array) {
        if (!seen.has(item)) {
          seen.add(item)
          result.push(item)
        }
      }
    }
  }
  
  return result
}

/**
 * 数组差集
 * @param {Array} array - 第一个数组
 * @param {...Array} others - 其他数组
 * @returns {Array} 差集数组
 */
export function difference(array, ...others) {
  if (!Array.isArray(array)) return []
  
  const otherValues = new Set(flatten(others))
  return array.filter(item => !otherValues.has(item))
}

/**
 * 数组分区
 * @param {Array} array - 原始数组
 * @param {Function} predicate - 分区条件函数
 * @returns {Array} [满足条件的数组, 不满足条件的数组]
 */
export function partition(array, predicate) {
  if (!Array.isArray(array)) return [[], []]
  
  const truthy = []
  const falsy = []
  
  for (const item of array) {
    if (predicate(item)) {
      truthy.push(item)
    } else {
      falsy.push(item)
    }
  }
  
  return [truthy, falsy]
}

/**
 * 数组映射（支持异步）
 * @param {Array} array - 原始数组
 * @param {Function} iteratee - 迭代函数
 * @returns {Promise<Array>} 映射后的数组
 */
export async function mapAsync(array, iteratee) {
  if (!Array.isArray(array)) return []
  
  const results = []
  for (let i = 0; i < array.length; i++) {
    results.push(await iteratee(array[i], i, array))
  }
  
  return results
}

/**
 * 数组过滤（支持异步）
 * @param {Array} array - 原始数组
 * @param {Function} predicate - 过滤条件函数
 * @returns {Promise<Array>} 过滤后的数组
 */
export async function filterAsync(array, predicate) {
  if (!Array.isArray(array)) return []
  
  const results = []
  for (let i = 0; i < array.length; i++) {
    if (await predicate(array[i], i, array)) {
      results.push(array[i])
    }
  }
  
  return results
}

/**
 * 数组归约（支持异步）
 * @param {Array} array - 原始数组
 * @param {Function} reducer - 归约函数
 * @param {*} initialValue - 初始值
 * @returns {Promise<*>} 归约结果
 */
export async function reduceAsync(array, reducer, initialValue) {
  if (!Array.isArray(array)) return initialValue
  
  let accumulator = initialValue
  for (let i = 0; i < array.length; i++) {
    accumulator = await reducer(accumulator, array[i], i, array)
  }
  
  return accumulator
}

/**
 * 数组批处理
 * @param {Array} array - 原始数组
 * @param {Function} processor - 处理函数
 * @param {number} batchSize - 批次大小
 * @returns {Promise<Array>} 处理结果
 */
export async function batchProcess(array, processor, batchSize = 10) {
  if (!Array.isArray(array)) return []
  
  const results = []
  const batches = chunk(array, batchSize)
  
  for (const batch of batches) {
    const batchResults = await Promise.all(
      batch.map((item, index) => processor(item, index))
    )
    results.push(...batchResults)
  }
  
  return results
}

/**
 * 比赛数组排序（按时间）
 * @param {Array} matches - 比赛数组
 * @param {string} order - 排序顺序
 * @returns {Array} 排序后的比赛数组
 */
export function sortMatchesByTime(matches, order = 'asc') {
  if (!Array.isArray(matches)) return []
  
  return sortBy(matches, match => {
    if (!match.matchDate || !match.matchTime) return Infinity
    
    try {
      const dateTime = new Date(`${match.matchDate}T${match.matchTime}`)
      return dateTime.getTime()
    } catch {
      return Infinity
    }
  }, order)
}

/**
 * 按联赛分组比赛
 * @param {Array} matches - 比赛数组
 * @returns {Object} 按联赛分组的比赛
 */
export function groupMatchesByLeague(matches) {
  if (!Array.isArray(matches)) return {}
  
  return groupBy(matches, match => match.league || '其他')
}

/**
 * 按状态筛选比赛
 * @param {Array} matches - 比赛数组
 * @param {string} status - 比赛状态
 * @returns {Array} 筛选后的比赛
 */
export function filterMatchesByStatus(matches, status) {
  if (!Array.isArray(matches)) return []
  
  return filter(matches, { status })
}

/**
 * 获取今日比赛
 * @param {Array} matches - 比赛数组
 * @returns {Array} 今日比赛
 */
export function getTodayMatches(matches) {
  if (!Array.isArray(matches)) return []
  
  const today = new Date().toISOString().split('T')[0]
  
  return matches.filter(match => match.matchDate === today)
}

/**
 * 获取未来比赛
 * @param {Array} matches - 比赛数组
 * @param {number} days - 未来天数
 * @returns {Array} 未来比赛
 */
export function getUpcomingMatches(matches, days = 7) {
  if (!Array.isArray(matches)) return []
  
  const today = new Date()
  const futureDate = new Date(today)
  futureDate.setDate(today.getDate() + days)
  
  return matches.filter(match => {
    if (!match.matchDate || !match.matchTime) return false
    
    try {
      const matchDateTime = new Date(`${match.matchDate}T${match.matchTime}`)
      return matchDateTime >= today && matchDateTime <= futureDate
    } catch {
      return false
    }
  })
}

/**
 * 获取历史比赛
 * @param {Array} matches - 比赛数组
 * @param {number} days - 历史天数
 * @returns {Array} 历史比赛
 */
export function getHistoricalMatches(matches, days = 30) {
  if (!Array.isArray(matches)) return []
  
  const today = new Date()
  const pastDate = new Date(today)
  pastDate.setDate(today.getDate() - days)
  
  return matches.filter(match => {
    if (!match.matchDate || !match.matchTime) return false
    
    try {
      const matchDateTime = new Date(`${match.matchDate}T${match.matchTime}`)
      return matchDateTime >= pastDate && matchDateTime <= today
    } catch {
      return false
    }
  })
}

/**
 * 按球队筛选比赛
 * @param {Array} matches - 比赛数组
 * @param {string} teamName - 球队名称
 * @returns {Array} 相关比赛
 */
export function getMatchesByTeam(matches, teamName) {
  if (!Array.isArray(matches) || !teamName) return []
  
  return matches.filter(match => 
    match.homeTeam === teamName || 
    match.awayTeam === teamName ||
    match.homeTeam?.includes(teamName) || 
    match.awayTeam?.includes(teamName)
  )
}

/**
 * 获取重要比赛（根据赔率）
 * @param {Array} matches - 比赛数组
 * @param {number} threshold - 赔率阈值
 * @returns {Array} 重要比赛
 */
export function getImportantMatches(matches, threshold = 2.0) {
  if (!Array.isArray(matches)) return []
  
  return matches.filter(match => {
    const odds = match.odds || {}
    return Object.values(odds).some(odd => odd <= threshold)
  })
}

/**
 * 获取高风险比赛（根据赔率差）
 * @param {Array} matches - 比赛数组
 * @param {number} diffThreshold - 赔率差阈值
 * @returns {Array} 高风险比赛
 */
export function getHighRiskMatches(matches, diffThreshold = 0.5) {
  if (!Array.isArray(matches)) return []
  
  return matches.filter(match => {
    const odds = match.odds || {}
    const values = Object.values(odds).filter(v => typeof v === 'number')
    
    if (values.length < 2) return false
    
    const maxOdds = Math.max(...values)
    const minOdds = Math.min(...values)
    
    return maxOdds - minOdds >= diffThreshold
  })
}

export default {
  unique,
  chunk,
  flatten,
  flattenDeep,
  groupBy,
  sortBy,
  filter,
  find,
  findLast,
  max,
  min,
  sum,
  mean,
  shuffle,
  sample,
  intersection,
  union,
  difference,
  partition,
  mapAsync,
  filterAsync,
  reduceAsync,
  batchProcess,
  sortMatchesByTime,
  groupMatchesByLeague,
  filterMatchesByStatus,
  getTodayMatches,
  getUpcomingMatches,
  getHistoricalMatches,
  getMatchesByTeam,
  getImportantMatches,
  getHighRiskMatches
}