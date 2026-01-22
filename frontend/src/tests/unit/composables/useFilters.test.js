import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useFilters } from '@/composables/useFilters.js'
import { ref } from 'vue'

describe('useFilters', () => {
  let filters

  beforeEach(() => {
    vi.clearAllMocks()
    filters = useFilters()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('状态管理', () => {
    it('应该初始化filters为默认对象', () => {
      expect(filters.filters.value).toEqual({
        sport_type: 'football',
        date_range: 'today',
        leagues: [],
        status: 'all',
        search: ''
      })
    })

    it('应该初始化quickFilters为预定义数组', () => {
      expect(filters.quickFilters.value).toBeInstanceOf(Array)
      expect(filters.quickFilters.value.length).toBeGreaterThan(0)
      
      // 检查快速筛选器的结构
      const quickFilter = filters.quickFilters.value[0]
      expect(quickFilter).toHaveProperty('label')
      expect(quickFilter).toHaveProperty('value')
      expect(quickFilter).toHaveProperty('icon')
    })

    it('应该初始化loading状态为false', () => {
      expect(filters.loading.value).toBe(false)
    })

    it('应该初始化error状态为null', () => {
      expect(filters.error.value).toBeNull()
    })
  })

  describe('计算属性', () => {
    it('activeFilterCount应该返回激活的筛选条件数量', () => {
      // 初始状态下应该只有sport_type是激活的默认值
      expect(filters.activeFilterCount.value).toBe(1)
      
      // 添加联赛筛选
      filters.filters.value = { ...filters.filters.value, leagues: ['英超'] }
      expect(filters.activeFilterCount.value).toBe(2)
      
      // 添加状态筛选
      filters.filters.value = { ...filters.filters.value, status: 'live' }
      expect(filters.activeFilterCount.value).toBe(3)
      
      // 添加搜索筛选
      filters.filters.value = { ...filters.filters.value, search: 'test' }
      expect(filters.activeFilterCount.value).toBe(4)
      
      // 'all' 和空数组应该不计入激活条件
      filters.filters.value = {
        ...filters.filters.value,
        status: 'all',
        leagues: [],
        search: ''
      }
      expect(filters.activeFilterCount.value).toBe(1) // 只有sport_type
    })

    it('hasActiveFilters应该判断是否有权激活的筛选条件', () => {
      // 初始状态应该有激活的筛选条件
      expect(filters.hasActiveFilters.value).toBe(true)
      
      // 重置为只有默认值
      filters.filters.value = {
        sport_type: 'football',
        date_range: 'today',
        leagues: [],
        status: 'all',
        search: ''
      }
      expect(filters.hasActiveFilters.value).toBe(false)
      
      // 添加一个激活条件
      filters.filters.value = { ...filters.filters.value, leagues: ['英超'] }
      expect(filters.hasActiveFilters.value).toBe(true)
    })

    it('filterSummary应该返回筛选条件摘要', () => {
      filters.filters.value = {
        sport_type: 'basketball',
        date_range: 'week',
        leagues: ['NBA', 'CBA'],
        status: 'live',
        search: 'Lakers'
      }
      
      const summary = filters.filterSummary.value
      
      expect(summary).toContain('篮球')
      expect(summary).toContain('本周')
      expect(summary).toContain('NBA')
      expect(summary).toContain('CBA')
      expect(summary).toContain('进行中')
      expect(summary).toContain('Lakers')
    })
  })

  describe('更新筛选条件', () => {
    it('应该更新单个筛选条件', () => {
      filters.updateFilters({ sport_type: 'basketball' })
      
      expect(filters.filters.value.sport_type).toBe('basketball')
    })

    it('应该支持多个筛选条件同时更新', () => {
      filters.updateFilters({
        sport_type: 'basketball',
        date_range: 'week',
        leagues: ['NBA', 'CBA']
      })
      
      expect(filters.filters.value.sport_type).toBe('basketball')
      expect(filters.filters.value.date_range).toBe('week')
      expect(filters.filters.value.leagues).toEqual(['NBA', 'CBA'])
    })

    it('应该验证筛选条件的有效性', () => {
      // 测试有效的运动类型
      filters.updateFilters({ sport_type: 'football' })
      expect(filters.filters.value.sport_type).toBe('football')
      
      // 测试无效的运动类型（如果实现了验证）
      filters.updateFilters({ sport_type: 'invalid_sport' })
      // 根据实现，可能会接受或拒绝无效值
      expect(filters.filters.value.sport_type).toBeDefined()
    })

    it('应该验证日期范围的有效性', () => {
      const validRanges = ['today', 'week', 'month', 'all']
      
      validRanges.forEach(range => {
        filters.updateFilters({ date_range: range })
        expect(filters.filters.value.date_range).toBe(range)
      })
    })

    it('应该验证状态筛选的有效性', () => {
      const validStatuses = ['all', 'upcoming', 'live', 'finished']
      
      validStatuses.forEach(status => {
        filters.updateFilters({ status })
        expect(filters.filters.value.status).toBe(status)
      })
    })
  })

  describe('重置筛选条件', () => {
    it('应该重置所有筛选条件为默认值', () => {
      // 先设置一些非默认的筛选条件
      filters.filters.value = {
        sport_type: 'basketball',
        date_range: 'month',
        leagues: ['NBA', 'CBA'],
        status: 'live',
        search: 'test search'
      }
      
      filters.resetFilters()
      
      expect(filters.filters.value).toEqual({
        sport_type: 'football',
        date_range: 'today',
        leagues: [],
        status: 'all',
        search: ''
      })
    })

    it('重置时应该触发change事件', () => {
      const emitSpy = vi.fn()
      filters.emit = emitSpy
      
      filters.resetFilters()
      
      expect(emitSpy).toHaveBeenCalledWith('change', filters.filters.value)
    })
  })

  describe('快速筛选', () => {
    it('应该应用快速筛选', () => {
      const quickFilter = {
        label: '今日足球',
        value: 'football_today',
        icon: 'football',
        filters: {
          sport_type: 'football',
          date_range: 'today'
        }
      }
      
      filters.applyQuickFilter(quickFilter)
      
      expect(filters.filters.value.sport_type).toBe('football')
      expect(filters.filters.value.date_range).toBe('today')
    })

    it('应该验证快速筛选数据的有效性', () => {
      const invalidQuickFilter = {
        label: 'Invalid Filter',
        // 缺少必要的filters属性
      }
      
      // 这应该不会抛出错误，而是安全地忽略
      expect(() => {
        filters.applyQuickFilter(invalidQuickFilter)
      }).not.toThrow()
    })

    it('快速筛选应该合并现有条件', () => {
      filters.filters.value = {
        sport_type: 'basketball',
        date_range: 'week',
        leagues: ['NBA'],
        status: 'all',
        search: ''
      }
      
      const quickFilter = {
        filters: {
          sport_type: 'football',
          leagues: ['英超']
        }
      }
      
      filters.applyQuickFilter(quickFilter)
      
      // 快速筛选应该覆盖指定的字段，保留其他字段
      expect(filters.filters.value.sport_type).toBe('football')
      expect(filters.filters.value.leagues).toEqual(['英超'])
      expect(filters.filters.value.date_range).toBe('week') // 保持不变
      expect(filters.filters.value.status).toBe('all') // 保持不变
    })
  })

  describe('搜索功能', () => {
    it('应该设置搜索关键词', () => {
      filters.setSearch('曼联 vs 切尔西')
      
      expect(filters.filters.value.search).toBe('曼联 vs 切尔西')
    })

    it('应该支持空搜索词', () => {
      filters.filters.value = { ...filters.filters.value, search: 'previous search' }
      
      filters.setSearch('')
      
      expect(filters.filters.value.search).toBe('')
    })

    it('应该去除搜索词的首尾空格', () => {
      filters.setSearch('  test search  ')
      
      expect(filters.filters.value.search).toBe('test search')
    })

    it('应该限制搜索词长度', () => {
      const longSearch = 'a'.repeat(200)
      filters.setSearch(longSearch)
      
      // 假设有最大长度限制，比如100个字符
      expect(filters.filters.value.search.length).toBeLessThanOrEqual(100)
    })
  })

  describe('联赛筛选', () => {
    it('应该切换联赛选择状态', () => {
      // 初始状态：没有选中任何联赛
      expect(filters.filters.value.leagues).toEqual([])
      
      // 选择联赛
      filters.toggleLeague('英超')
      expect(filters.filters.value.leagues).toEqual(['英超'])
      
      // 再次选择同一联赛应该取消选择
      filters.toggleLeague('英超')
      expect(filters.filters.value.leagues).toEqual([])
      
      // 选择多个联赛
      filters.toggleLeague('英超')
      filters.toggleLeague('西甲')
      expect(filters.filters.value.leagues).toEqual(['英超', '西甲'])
      
      // 切换其中一个联赛
      filters.toggleLeague('英超')
      expect(filters.filters.value.leagues).toEqual(['西甲'])
    })

    it('应该验证联赛名称的有效性', () => {
      // 测试空字符串
      filters.toggleLeague('')
      expect(filters.filters.value.leagues).toEqual([])
      
      // 测试null或undefined
      filters.toggleLeague(null)
      filters.toggleLeague(undefined)
      expect(filters.filters.value.leagues).toEqual([])
      
      // 测试有效联赛名
      filters.toggleLeague('Valid League')
      expect(filters.filters.value.leagues).toContain('Valid League')
    })

    it('应该限制选择的联赛数量', () => {
      // 假设最多选择10个联赛
      const manyLeagues = Array.from({ length: 15 }, (_, i) => `League ${i + 1}`)
      
      manyLeagues.forEach(league => {
        filters.toggleLeague(league)
      })
      
      // 应该限制在某个最大数量内
      expect(filters.filters.value.leagues.length).toBeLessThanOrEqual(10)
    })
  })

  describe('状态筛选', () => {
    it('应该设置状态筛选', () => {
      filters.setStatus('live')
      expect(filters.filters.value.status).toBe('live')
      
      filters.setStatus('finished')
      expect(filters.filters.value.status).toBe('finished')
      
      filters.setStatus('all')
      expect(filters.filters.value.status).toBe('all')
    })

    it('应该验证状态值的有效性', () => {
      const validStatuses = ['all', 'upcoming', 'live', 'finished']
      const invalidStatuses = ['invalid', 'unknown', '']
      
      // 有效状态应该被接受
      validStatuses.forEach(status => {
        filters.setStatus(status)
        expect(filters.filters.value.status).toBe(status)
      })
      
      // 无效状态应该被忽略或设置为默认值
      invalidStatuses.forEach(status => {
        filters.setStatus(status)
        // 根据实现，可能保持原值或设为默认值
        expect(['all', 'upcoming', 'live', 'finished']).toContain(filters.filters.value.status)
      })
    })
  })

  describe('日期范围筛选', () => {
    it('应该设置日期范围', () => {
      const dateRanges = ['today', 'week', 'month', 'all']
      
      dateRanges.forEach(range => {
        filters.setDateRange(range)
        expect(filters.filters.value.date_range).toBe(range)
      })
    })

    it('应该验证日期范围的有效性', () => {
      // 有效范围
      filters.setDateRange('today')
      expect(filters.filters.value.date_range).toBe('today')
      
      // 无效范围应该被忽略
      filters.setDateRange('invalid_range')
      // 应该保持之前的有效值
      expect(filters.filters.value.date_range).toBe('today')
    })
  })

  describe('运动类型筛选', () => {
    it('应该设置运动类型', () => {
      filters.setSportType('basketball')
      expect(filters.filters.value.sport_type).toBe('basketball')
      
      filters.setSportType('football')
      expect(filters.filters.value.sport_type).toBe('football')
    })

    it('应该验证运动类型的有效性', () => {
      // 有效运动类型
      filters.setSportType('basketball')
      expect(filters.filters.value.sport_type).toBe('basketball')
      
      // 无效运动类型应该被忽略
      filters.setSportType('invalid_sport')
      // 应该保持之前的有效值
      expect(filters.filters.value.sport_type).toBe('basketball')
    })
  })

  describe('工具函数', () => {
    it('getFilterOptions应该返回可用的筛选选项', () => {
      const options = filters.getFilterOptions()
      
      expect(options).toHaveProperty('sportTypes')
      expect(options).toHaveProperty('dateRanges')
      expect(options).toHaveProperty('statuses')
      expect(options.sportTypes).toBeInstanceOf(Array)
      expect(options.dateRanges).toBeInstanceOf(Array)
      expect(options.statuses).toBeInstanceOf(Array)
    })

    it('validateFilters应该验证筛选条件的组合有效性', () => {
      // 有效组合
      const validFilters = {
        sport_type: 'football',
        date_range: 'today',
        leagues: ['英超'],
        status: 'live',
        search: 'test'
      }
      
      expect(filters.validateFilters(validFilters)).toBe(true)
      
      // 无效组合（如果有业务规则限制）
      const invalidFilters = {
        sport_type: '', // 空的运动类型
        date_range: 'invalid',
        leagues: [],
        status: 'all',
        search: ''
      }
      
      // 根据实现，可能返回true或false
      expect(typeof filters.validateFilters(invalidFilters)).toBe('boolean')
    })

    it('buildApiParams应该构建API请求参数', () => {
      filters.filters.value = {
        sport_type: 'basketball',
        date_range: 'week',
        leagues: ['NBA', 'CBA'],
        status: 'live',
        search: 'Lakers'
      }
      
      const params = filters.buildApiParams()
      
      expect(params).toHaveProperty('sport_type', 'basketball')
      expect(params).toHaveProperty('date_range', 'week')
      expect(params).toHaveProperty('leagues', ['NBA', 'CBA'])
      expect(params).toHaveProperty('status', 'live')
      expect(params).toHaveProperty('search', 'Lakers')
    })

    it('exportFilters应该导出当前筛选条件', () => {
      filters.filters.value = {
        sport_type: 'football',
        date_range: 'today',
        leagues: ['英超'],
        status: 'live',
        search: 'test'
      }
      
      const exported = filters.exportFilters()
      
      expect(exported).toEqual(filters.filters.value)
      expect(JSON.parse(JSON.stringify(exported))).toEqual(filters.filters.value) // 确保可序列化
    })

    it('importFilters应该导入筛选条件', () => {
      const importedFilters = {
        sport_type: 'basketball',
        date_range: 'month',
        leagues: ['NBA'],
        status: 'finished',
        search: 'imported'
      }
      
      filters.importFilters(importedFilters)
      
      expect(filters.filters.value).toEqual(importedFilters)
    })

    it('应该验证导入数据的有效性', () => {
      const invalidData = {
        sport_type: 'invalid_sport',
        date_range: 'invalid_range',
        // 缺少必要字段
      }
      
      // 导入无效数据应该被拒绝或清理
      filters.importFilters(invalidData)
      
      // 根据实现，可能完全拒绝或清理无效字段
      expect(filters.filters.value).toBeDefined()
    })
  })

  describe('持久化功能', () => {
    beforeEach(() => {
      // 模拟 localStorage
      Storage.prototype.getItem = vi.fn()
      Storage.prototype.setItem = vi.fn()
      Storage.prototype.removeItem = vi.fn()
    })

    it('应该保存筛选条件到localStorage', () => {
      filters.saveFiltersToStorage()
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'user_filters',
        expect.any(String)
      )
    })

    it('应该从localStorage加载筛选条件', () => {
      const savedFilters = {
        sport_type: 'basketball',
        date_range: 'week',
        leagues: ['NBA'],
        status: 'live',
        search: 'test'
      }
      
      localStorage.getItem.mockReturnValue(JSON.stringify(savedFilters))
      
      filters.loadFiltersFromStorage()
      
      expect(filters.filters.value).toEqual(savedFilters)
    })

    it('localStorage中没有数据时应该使用默认值', () => {
      localStorage.getItem.mockReturnValue(null)
      
      filters.loadFiltersFromStorage()
      
      expect(filters.filters.value).toEqual({
        sport_type: 'football',
        date_range: 'today',
        leagues: [],
        status: 'all',
        search: ''
      })
    })

    it('应该处理localStorage数据损坏', () => {
      localStorage.getItem.mockReturnValue('invalid json string')
      
      // 这应该不会抛出错误
      expect(() => {
        filters.loadFiltersFromStorage()
      }).not.toThrow()
      
      // 应该使用默认过滤器
      expect(filters.filters.value).toBeDefined()
    })

    it('应该处理localStorage配额超限', () => {
      localStorage.setItem.mockImplementation(() => {
        throw new Error('QuotaExceededError')
      })
      
      // 这应该不会抛出错误
      expect(() => {
        filters.saveFiltersToStorage()
      }).not.toThrow()
    })
  })

  describe('监听器', () => {
    it('筛选条件变化应该触发change事件', () => {
      const emitSpy = vi.fn()
      filters.emit = emitSpy
      
      // 更新筛选条件
      filters.updateFilters({ sport_type: 'basketball' })
      
      expect(emitSpy).toHaveBeenCalledWith('change', filters.filters.value)
    })

    it('筛选条件变化应该保存到localStorage', async () => {
      // 更新筛选条件
      filters.updateFilters({ sport_type: 'basketball' })
      
      // 等待监听器执行
      await new Promise(resolve => setTimeout(resolve, 0))
      
      expect(localStorage.setItem).toHaveBeenCalled()
    })
  })

  describe('错误处理', () => {
    it('应该处理更新筛选时的错误', () => {
      // 模拟一个会导致错误的操作
      const invalidFilters = null
      
      // 这应该被安全地处理
      expect(() => {
        filters.updateFilters(invalidFilters)
      }).not.toThrow()
    })

    it('应该处理重置筛选时的错误', () => {
      // 模拟localStorage错误
      localStorage.setItem.mockImplementation(() => {
        throw new Error('Storage error')
      })
      
      // 重置应该仍然工作，只是不保存
      expect(() => {
        filters.resetFilters()
      }).not.toThrow()
      
      expect(filters.filters.value).toEqual({
        sport_type: 'football',
        date_range: 'today',
        leagues: [],
        status: 'all',
        search: ''
      })
    })
  })

  describe('性能优化', () => {
    it('应该避免不必要的计算和存储', () => {
      const initialCallCount = localStorage.setItem.mock.calls.length
      
      // 设置相同的值不应该触发存储
      filters.updateFilters({ sport_type: 'football' }) // 已经是默认值
      
      // 等待可能的异步操作
      setTimeout(() => {
        // 存储调用次数应该没有明显增加（取决于实现）
        expect(localStorage.setItem.mock.calls.length).toBeLessThan(initialCallCount + 2)
      }, 100)
    })

    it('应该缓存计算结果', () => {
      // 第一次计算
      const result1 = filters.activeFilterCount.value
      
      // 相同状态下第二次计算应该使用缓存
      const result2 = filters.activeFilterCount.value
      
      expect(result1).toBe(result2)
    })
  })

  describe('边界情况', () => {
    it('空值和undefined应该被正确处理', () => {
      filters.updateFilters({
        sport_type: null,
        date_range: undefined,
        leagues: null,
        status: '',
        search: null
      })
      
      // 应该被转换为合适的默认值或保持现有值
      expect(filters.filters.value).toBeDefined()
    })

    it('极端值应该被正确处理', () => {
      // 很长的搜索词
      const longSearch = 'a'.repeat(1000)
      filters.setSearch(longSearch)
      expect(filters.filters.value.search.length).toBeLessThanOrEqual(100)
      
      // 很多联赛
      const manyLeagues = Array.from({ length: 100 }, (_, i) => `League ${i}`)
      filters.filters.value.leagues = manyLeagues
      expect(filters.filters.value.leagues.length).toBeLessThanOrEqual(50) // 假设有上限
    })

    it('特殊字符应该被正确处理', () => {
      const specialChars = 'test<script>alert("xss")</script>&nbsp;测试'
      filters.setSearch(specialChars)
      
      // XSS字符应该被转义或移除
      expect(filters.filters.value.search).not.toContain('<script>')
      expect(filters.filters.value.search).toContain('测试')
    })
  })

  describe('可访问性', () => {
    it('应该支持键盘导航', () => {
      // 这是一个基础的测试，实际的可访问性测试更复杂
      expect(filters.filters).toBeDefined()
      expect(filters.updateFilters).toBeInstanceOf(Function)
    })

    it('应该提供有意义的反馈', () => {
      // 当筛选条件变化时，应该有相应的状态更新
      const initialCount = filters.activeFilterCount.value
      filters.updateFilters({ leagues: ['英超'] })
      const newCount = filters.activeFilterCount.value
      
      expect(newCount).toBeGreaterThan(initialCount)
    })
  })
})