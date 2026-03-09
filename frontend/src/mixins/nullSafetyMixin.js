/**
 * Vue全局混入 - Null安全防护
 * 提供安全属性访问、空值回退和组件数据自动防护功能
 */

export default {
  created() {
    // 确保组件数据具有默认值
    this.$nullSafeData()
  },
  
  methods: {
    /**
     * 安全获取嵌套属性值
     * @param {Object} obj - 目标对象
     * @param {string} path - 属性路径，如 'user.profile.name'
     * @param {*} defaultValue - 默认值，当路径不存在时返回
     * @returns {*} 属性值或默认值
     * @example this.$safeGet(user, 'profile.name', '未知')
     */
    $safeGet(obj, path, defaultValue = null) {
      if (!obj || typeof obj !== 'object') {
        return defaultValue
      }
      
      const keys = path.split('.')
      let current = obj
      
      for (const key of keys) {
        if (current === null || current === undefined) {
          return defaultValue
        }
        current = current[key]
      }
      
      return current === undefined || current === null ? defaultValue : current
    },
    
    /**
     * 确保值不为null/undefined，否则返回回退值
     * @param {*} value - 要检查的值
     * @param {*} fallback - 回退值
     * @returns {*} 非空值或回退值
     * @example this.$ensureNotNull(data.name, '未命名')
     */
    $ensureNotNull(value, fallback) {
      return value !== null && value !== undefined ? value : fallback
    },
    
    /**
     * 空值回退链，返回第一个非空值
     * @param {...*} values - 多个值
     * @returns {*} 第一个非空值，或最后一个值
     * @example this.$coalesce(data.name, config.name, '默认')
     */
    $coalesce(...values) {
      for (const value of values) {
        if (value !== null && value !== undefined) {
          return value
        }
      }
      return values[values.length - 1]
    },
    
    /**
     * 组件数据自动防护，确保所有响应式数据都有默认值
     * 防止模板访问未定义属性时出错
     */
    $nullSafeData() {
      if (!this.$options.data) {
        return
      }
      
      const originalData = this.$options.data.call(this)
      const defaultData = this.$options.defaultData ? this.$options.defaultData.call(this) : {}
      
      // 遍历所有数据属性，确保没有undefined
      for (const key in originalData) {
        if (originalData[key] === undefined) {
          // 尝试从defaultData获取默认值，否则使用null
          this[key] = defaultData[key] !== undefined ? defaultData[key] : null
        }
      }
    },
    
    /**
     * 深度防护对象，递归确保所有嵌套属性都有默认值
     * @param {Object} obj - 要防护的对象
     * @param {Object} defaults - 默认值映射
     * @returns {Object} 防护后的对象
     */
    $deepNullGuard(obj, defaults = {}) {
      if (!obj || typeof obj !== 'object') {
        return obj
      }
      
      const result = Array.isArray(obj) ? [] : {}
      
      for (const key in obj) {
        const value = obj[key]
        const defaultValue = defaults[key]
        
        if (value === null || value === undefined) {
          result[key] = defaultValue
        } else if (typeof value === 'object') {
          // 递归防护嵌套对象
          const nestedDefaults = typeof defaultValue === 'object' ? defaultValue : {}
          result[key] = this.$deepNullGuard(value, nestedDefaults)
        } else {
          result[key] = value
        }
      }
      
      return result
    }
  },
  
  /**
   * 自定义选项，用于定义组件数据的默认值
   */
  defaultData() {
    return {}
  }
}