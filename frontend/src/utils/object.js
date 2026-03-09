// frontend/src/utils/object.js

/**
 * 对象处理工具
 */

/**
 * 深度合并对象
 * @param {Object} target - 目标对象
 * @param {...Object} sources - 源对象
 * @returns {Object} 合并后的对象
 */
export function deepMerge(target, ...sources) {
  if (!target) target = {}
  
  for (const source of sources) {
    if (!source || typeof source !== 'object') continue
    
    for (const key in source) {
      if (source.hasOwnProperty(key)) {
        const targetValue = target[key]
        const sourceValue = source[key]
        
        if (isObject(targetValue) && isObject(sourceValue)) {
          target[key] = deepMerge({}, targetValue, sourceValue)
        } else if (Array.isArray(targetValue) && Array.isArray(sourceValue)) {
          target[key] = [...targetValue, ...sourceValue]
        } else {
          target[key] = sourceValue
        }
      }
    }
  }
  
  return target
}

/**
 * 检查是否为普通对象
 * @param {*} value - 要检查的值
 * @returns {boolean} 是否为普通对象
 */
export function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
}

/**
 * 检查对象是否为空
 * @param {Object} obj - 对象
 * @returns {boolean} 是否为空
 */
export function isEmptyObject(obj) {
  if (!isObject(obj)) return true
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) return false
  }
  
  return true
}

/**
 * 深度克隆对象
 * @param {Object} obj - 要克隆的对象
 * @returns {Object} 克隆后的对象
 */
export function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj
  if (obj instanceof Date) return new Date(obj.getTime())
  if (obj instanceof RegExp) return new RegExp(obj)
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item))
  }
  
  const cloned = {}
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key])
    }
  }
  
  return cloned
}

/**
 * 获取对象属性（支持路径）
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径
 * @param {*} defaultValue - 默认值
 * @returns {*} 属性值
 */
export function get(obj, path, defaultValue = undefined) {
  if (!isObject(obj) || typeof path !== 'string') return defaultValue
  
  const keys = path.split('.')
  let result = obj
  
  for (const key of keys) {
    if (result === null || result === undefined) return defaultValue
    
    // 处理数组索引
    const match = key.match(/^(\w+)\[(\d+)\]$/)
    if (match) {
      const arrayKey = match[1]
      const arrayIndex = parseInt(match[2], 10)
      
      if (!Array.isArray(result[arrayKey])) return defaultValue
      result = result[arrayKey][arrayIndex]
    } else {
      result = result[key]
    }
    
    if (result === undefined) return defaultValue
  }
  
  return result
}

/**
 * 设置对象属性（支持路径）
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径
 * @param {*} value - 属性值
 * @returns {Object} 修改后的对象
 */
export function set(obj, path, value) {
  if (!isObject(obj) || typeof path !== 'string') return obj
  
  const keys = path.split('.')
  let current = obj
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    
    // 处理数组索引
    const match = key.match(/^(\w+)\[(\d+)\]$/)
    if (match) {
      const arrayKey = match[1]
      const arrayIndex = parseInt(match[2], 10)
      
      if (!current[arrayKey]) current[arrayKey] = []
      if (!Array.isArray(current[arrayKey])) {
        current[arrayKey] = [current[arrayKey]]
      }
      
      if (!current[arrayKey][arrayIndex]) {
        current[arrayKey][arrayIndex] = {}
      }
      
      current = current[arrayKey][arrayIndex]
    } else {
      if (!current[key] || !isObject(current[key])) {
        current[key] = {}
      }
      current = current[key]
    }
  }
  
  const lastKey = keys[keys.length - 1]
  const lastMatch = lastKey.match(/^(\w+)\[(\d+)\]$/)
  
  if (lastMatch) {
    const arrayKey = lastMatch[1]
    const arrayIndex = parseInt(lastMatch[2], 10)
    
    if (!current[arrayKey]) current[arrayKey] = []
    if (!Array.isArray(current[arrayKey])) {
      current[arrayKey] = [current[arrayKey]]
    }
    
    current[arrayKey][arrayIndex] = value
  } else {
    current[lastKey] = value
  }
  
  return obj
}

/**
 * 删除对象属性（支持路径）
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径
 * @returns {Object} 修改后的对象
 */
export function unset(obj, path) {
  if (!isObject(obj) || typeof path !== 'string') return obj
  
  const keys = path.split('.')
  let current = obj
  
  for (let i = 0; i < keys.length - 1; i++) {
    const key = keys[i]
    
    // 处理数组索引
    const match = key.match(/^(\w+)\[(\d+)\]$/)
    if (match) {
      const arrayKey = match[1]
      const arrayIndex = parseInt(match[2], 10)
      
      if (!Array.isArray(current[arrayKey]) || 
          !current[arrayKey][arrayIndex]) {
        return obj
      }
      
      current = current[arrayKey][arrayIndex]
    } else {
      if (!current[key] || !isObject(current[key])) {
        return obj
      }
      current = current[key]
    }
  }
  
  const lastKey = keys[keys.length - 1]
  const lastMatch = lastKey.match(/^(\w+)\[(\d+)\]$/)
  
  if (lastMatch) {
    const arrayKey = lastMatch[1]
    const arrayIndex = parseInt(lastMatch[2], 10)
    
    if (Array.isArray(current[arrayKey])) {
      current[arrayKey].splice(arrayIndex, 1)
    }
  } else {
    delete current[lastKey]
  }
  
  return obj
}

/**
 * 检查对象是否包含指定路径
 * @param {Object} obj - 对象
 * @param {string} path - 属性路径
 * @returns {boolean} 是否包含
 */
export function has(obj, path) {
  if (!isObject(obj) || typeof path !== 'string') return false
  
  const keys = path.split('.')
  let current = obj
  
  for (const key of keys) {
    const match = key.match(/^(\w+)\[(\d+)\]$/)
    
    if (match) {
      const arrayKey = match[1]
      const arrayIndex = parseInt(match[2], 10)
      
      if (!Array.isArray(current[arrayKey]) || 
          current[arrayKey][arrayIndex] === undefined) {
        return false
      }
      
      current = current[arrayKey][arrayIndex]
    } else {
      if (current[key] === undefined) return false
      current = current[key]
    }
  }
  
  return true
}

/**
 * 对象映射（类似数组map）
 * @param {Object} obj - 对象
 * @param {Function} iteratee - 迭代函数
 * @returns {Object} 映射后的对象
 */
export function mapObject(obj, iteratee) {
  if (!isObject(obj) || typeof iteratee !== 'function') return {}
  
  const result = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      result[key] = iteratee(obj[key], key, obj)
    }
  }
  
  return result
}

/**
 * 对象过滤
 * @param {Object} obj - 对象
 * @param {Function} predicate - 条件函数
 * @returns {Object} 过滤后的对象
 */
export function filterObject(obj, predicate) {
  if (!isObject(obj) || typeof predicate !== 'function') return {}
  
  const result = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      if (predicate(obj[key], key, obj)) {
        result[key] = obj[key]
      }
    }
  }
  
  return result
}

/**
 * 对象键值对转换
 * @param {Object} obj - 对象
 * @returns {Array} 键值对数组
 */
export function toPairs(obj) {
  if (!isObject(obj)) return []
  
  return Object.entries(obj)
}

/**
 * 键值对数组转换为对象
 * @param {Array} pairs - 键值对数组
 * @returns {Object} 对象
 */
export function fromPairs(pairs) {
  if (!Array.isArray(pairs)) return {}
  
  const result = {}
  
  for (const [key, value] of pairs) {
    result[key] = value
  }
  
  return result
}

/**
 * 对象键名转换
 * @param {Object} obj - 对象
 * @param {Function} keyFn - 键名转换函数
 * @returns {Object} 键名转换后的对象
 */
export function mapKeys(obj, keyFn) {
  if (!isObject(obj) || typeof keyFn !== 'function') return {}
  
  const result = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const newKey = keyFn(key, obj[key], obj)
      result[newKey] = obj[key]
    }
  }
  
  return result
}

/**
 * 对象值转换
 * @param {Object} obj - 对象
 * @param {Function} valueFn - 值转换函数
 * @returns {Object} 值转换后的对象
 */
export function mapValues(obj, valueFn) {
  if (!isObject(obj) || typeof valueFn !== 'function') return {}
  
  const result = {}
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      result[key] = valueFn(obj[key], key, obj)
    }
  }
  
  return result
}

/**
 * 对象差集
 * @param {Object} obj1 - 对象1
 * @param {Object} obj2 - 对象2
 * @returns {Object} 差集对象
 */
export function differenceObject(obj1, obj2) {
  if (!isObject(obj1) || !isObject(obj2)) return {}
  
  const result = {}
  
  for (const key in obj1) {
    if (obj1.hasOwnProperty(key) && !obj2.hasOwnProperty(key)) {
      result[key] = obj1[key]
    }
  }
  
  return result
}

/**
 * 对象交集
 * @param {Object} obj1 - 对象1
 * @param {Object} obj2 - 对象2
 * @returns {Object} 交集对象
 */
export function intersectionObject(obj1, obj2) {
  if (!isObject(obj1) || !isObject(obj2)) return {}
  
  const result = {}
  
  for (const key in obj1) {
    if (obj1.hasOwnProperty(key) && obj2.hasOwnProperty(key)) {
      result[key] = obj1[key]
    }
  }
  
  return result
}

/**
 * 对象合并（浅合并）
 * @param {Object} target - 目标对象
 * @param {...Object} sources - 源对象
 * @returns {Object} 合并后的对象
 */
export function assign(target, ...sources) {
  if (!target) target = {}
  
  for (const source of sources) {
    if (isObject(source)) {
      Object.assign(target, source)
    }
  }
  
  return target
}

/**
 * 对象属性选择
 * @param {Object} obj - 对象
 * @param {Array|string} props - 属性名或数组
 * @returns {Object} 选择后的对象
 */
export function pick(obj, props) {
  if (!isObject(obj)) return {}
  
  const result = {}
  
  if (Array.isArray(props)) {
    for (const prop of props) {
      if (obj.hasOwnProperty(prop)) {
        result[prop] = obj[prop]
      }
    }
  } else if (typeof props === 'string') {
    if (obj.hasOwnProperty(props)) {
      result[props] = obj[props]
    }
  }
  
  return result
}

/**
 * 对象属性排除
 * @param {Object} obj - 对象
 * @param {Array|string} props - 属性名或数组
 * @returns {Object} 排除后的对象
 */
export function omit(obj, props) {
  if (!isObject(obj)) return {}
  
  const result = { ...obj }
  
  if (Array.isArray(props)) {
    for (const prop of props) {
      delete result[prop]
    }
  } else if (typeof props === 'string') {
    delete result[props]
  }
  
  return result
}

/**
 * 对象比较
 * @param {Object} obj1 - 对象1
 * @param {Object} obj2 - 对象2
 * @param {boolean} deep - 是否深度比较
 * @returns {boolean} 是否相等
 */
export function isEqual(obj1, obj2, deep = false) {
  if (obj1 === obj2) return true
  if (!isObject(obj1) || !isObject(obj2)) return false
  
  const keys1 = Object.keys(obj1)
  const keys2 = Object.keys(obj2)
  
  if (keys1.length !== keys2.length) return false
  
  for (const key of keys1) {
    const val1 = obj1[key]
    const val2 = obj2[key]
    
    if (deep) {
      if (!isEqual(val1, val2, true)) return false
    } else {
      if (val1 !== val2) return false
    }
  }
  
  return true
}

/**
 * 对象序列化（排除特定属性）
 * @param {Object} obj - 对象
 * @param {Array} exclude - 要排除的属性名数组
 * @returns {string} JSON字符串
 */
export function serialize(obj, exclude = []) {
  if (!isObject(obj)) return '{}'
  
  const filtered = filterObject(obj, (value, key) => {
    return !exclude.includes(key)
  })
  
  try {
    return JSON.stringify(filtered, null, 2)
  } catch {
    return '{}'
  }
}

/**
 * 对象反序列化
 * @param {string} str - JSON字符串
 * @param {Object} defaultValue - 默认值
 * @returns {Object} 对象
 */
export function deserialize(str, defaultValue = {}) {
  if (typeof str !== 'string') return defaultValue
  
  try {
    const parsed = JSON.parse(str)
    return isObject(parsed) ? parsed : defaultValue
  } catch {
    return defaultValue
  }
}

/**
 * 对象转查询字符串
 * @param {Object} obj - 对象
 * @returns {string} 查询字符串
 */
export function toQueryString(obj) {
  if (!isObject(obj)) return ''
  
  const params = new URLSearchParams()
  
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key]
      if (value !== null && value !== undefined) {
        params.append(key, String(value))
      }
    }
  }
  
  return params.toString()
}

/**
 * 查询字符串转对象
 * @param {string} queryString - 查询字符串
 * @returns {Object} 对象
 */
export function fromQueryString(queryString) {
  if (typeof queryString !== 'string') return {}
  
  const params = new URLSearchParams(queryString)
  const result = {}
  
  for (const [key, value] of params.entries()) {
    result[key] = value
  }
  
  return result
}

/**
 * 格式化比赛对象
 * @param {Object} match - 比赛对象
 * @returns {Object} 格式化后的比赛对象
 */
export function formatMatchObject(match) {
  if (!isObject(match)) return {}
  
  const defaults = {
    id: '',
    homeTeam: '',
    awayTeam: '',
    league: '',
    matchDate: '',
    matchTime: '',
    status: 'scheduled',
    odds: {},
    stats: {},
    intelligence: []
  }
  
  return deepMerge(defaults, match)
}

/**
 * 格式化球员对象
 * @param {Object} player - 球员对象
 * @returns {Object} 格式化后的球员对象
 */
export function formatPlayerObject(player) {
  if (!isObject(player)) return {}
  
  const defaults = {
    id: '',
    name: '',
    number: 0,
    position: '',
    team: '',
    nationality: '',
    age: 0,
    height: 0,
    weight: 0,
    stats: {}
  }
  
  return deepMerge(defaults, player)
}

/**
 * 格式化情报对象
 * @param {Object} intelligence - 情报对象
 * @returns {Object} 格式化后的情报对象
 */
export function formatIntelligenceObject(intelligence) {
  if (!isObject(intelligence)) return {}
  
  const defaults = {
    id: '',
    type: '',
    source: '',
    content: '',
    confidence: 0.5,
    matchId: '',
    teamId: '',
    playerId: '',
    createdAt: '',
    updatedAt: ''
  }
  
  return deepMerge(defaults, intelligence)
}

/**
 * 合并比赛情报
 * @param {Object} match - 比赛对象
 * @param {Array} intelligenceList - 情报列表
 * @returns {Object} 合并后的比赛对象
 */
export function mergeMatchIntelligence(match, intelligenceList) {
  if (!isObject(match) || !Array.isArray(intelligenceList)) return match
  
  const formattedMatch = formatMatchObject(match)
  formattedMatch.intelligence = intelligenceList.map(formatIntelligenceObject)
  
  return formattedMatch
}

/**
 * 提取比赛关键信息
 * @param {Object} match - 比赛对象
 * @returns {Object} 关键信息对象
 */
export function extractMatchKeyInfo(match) {
  if (!isObject(match)) return {}
  
  return pick(match, [
    'id',
    'homeTeam',
    'awayTeam',
    'league',
    'matchDate',
    'matchTime',
    'status',
    'homeScore',
    'awayScore'
  ])
}

/**
 * 计算比赛对象哈希
 * @param {Object} match - 比赛对象
 * @returns {string} 哈希值
 */
export function calculateMatchHash(match) {
  if (!isObject(match)) return ''
  
  const keyInfo = extractMatchKeyInfo(match)
  const str = JSON.stringify(keyInfo)
  
  // 简单哈希函数
  let hash = 0
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash
  }
  
  return Math.abs(hash).toString(16)
}

export default {
  deepMerge,
  isObject,
  isEmptyObject,
  deepClone,
  get,
  set,
  unset,
  has,
  mapObject,
  filterObject,
  toPairs,
  fromPairs,
  mapKeys,
  mapValues,
  differenceObject,
  intersectionObject,
  assign,
  pick,
  omit,
  isEqual,
  serialize,
  deserialize,
  toQueryString,
  fromQueryString,
  formatMatchObject,
  formatPlayerObject,
  formatIntelligenceObject,
  mergeMatchIntelligence,
  extractMatchKeyInfo,
  calculateMatchHash
}