// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useMatches } from '../../composables/useMatches.js'
import { ref } from 'vue'

// 模拟 vue-router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn()
}

// 模拟 dayjs
global.dayjs = vi.fn(date => ({
  format: vi.fn(format => {
    if (format === 'YYYY-MM-DD') return '2024-01-25'
    if (format === 'MM-DD') return '01-25'
    if (format === 'dddd') return 'Thursday'
    return date
  }),
  isSame: vi.fn(() => false),
  isToday: vi.fn(() => false),
  add: vi.fn(() => ({}))
}))

// 模拟 matchUtils
global.matchUtils = {
  getMatchStatusText: vi.fn(status => {
    const statusMap = {
      upcoming: '未开始',
      live: '进行中',
      finished: '已结束',
      cancelled: '已取消'
    }
    return statusMap[status] || status
  }),
  getMatchStatusClass: vi.fn(status => `status-${status}`),
  formatMatchTime: vi.fn(time => '15:00'),
  calculateProgress: vi.fn(() => 65)
}

describe('useMatches', () => {
  let matches

  beforeEach(() => {
    vi.clearAllMocks()
    matches = useMatches()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('状态管理', () => {
    it('应该初始化matches为空数组', () => {
      expect(matches.matches.value).toEqual([])
    })

    it('应该初始化loading状态为false', () => {
      expect(matches.loading.value).toBe(false)
    })

    it('应该初始化error状态为null', () => {
      expect(matches.error.value).toBeNull()
    })

    it('应该初始化selectedDate为今天', () => {
      expect(matches.selectedDate.value).toBeDefined()
    })

    it('应该初始化leagues为空数组', () => {
      expect(matches.leagues.value).toEqual([])
    })

    it('应该初始化filters为默认对象', () => {
      expect(matches.filters.value).toEqual({
        leagues: [],
        status: 'all',
        search: ''
      })
    })
  })

  describe('计算属性', () => {
    it('filteredMatches应该根据筛选条件过滤比赛', () => {
      matches.matches.value = [
        { id: 1, league: '英超', status: 'upcoming', home_team: '曼联', away_team: '切尔西' },
        { id: 2, league: '西甲', status: 'live', home_team: '巴萨', away_team: '皇马' },
        { id: 3, league: '英超', status: 'finished', home_team: '阿森纳', away_team: '热刺' }
      ]
      
      // 测试联赛筛选
      matches.filters.value = { ...matches.filters.value, leagues: ['英超'] }
      expect(matches.filteredMatches.value).toHaveLength(2)
      expect(matches.filteredMatches.value.every(match => match.league === '英超')).toBe(true)
      
      // 测试状态筛选
      matches.filters.value = { ...matches.filters.value, status: 'live' }
      expect(matches.filteredMatches.value).toHaveLength(1)
      expect(matches.filteredMatches.value[0].status).toBe('live')
      
      // 测试搜索筛选
      matches.filters.value = { ...matches.filters.value, search: '曼联' }
      expect(matches.filteredMatches.value).toHaveLength(1)
      expect(matches.filteredMatches.value[0].home_team).toBe('曼联')
    })

    it('groupedMatches应该按日期分组比赛', () => {
      const today = new Date().toISOString().split('T')[0]
      const tomorrow = new Date(Date.now() + 86400000).toISOString().split('T')[0]
      
      matches.matches.value = [
        { id: 1, match_time: `${today}T15:00:00Z`, status: 'upcoming' },
        { id: 2, match_time: `${today}T20:00:00Z`, status: 'upcoming' },
        { id: 3, match_time: `${tomorrow}T15:00:00Z`, status: 'upcoming' }
      ]
      
      const grouped = matches.groupedMatches.
      expect(grouped).toHaveProperty(today)
      expect(grouped).toHaveProperty(tomorrow)
      expect(grouped[today]).toHaveLength(2)
      expect(grouped[tomorrow]).toHaveLength(1)
    })

    it('sortedMatches应该按时间排序比赛', () => {
      matches.matches.value = [
        { id: 1, match_time: '2024-01-25T20:00:00Z' },
        { id: 2, match_time: '2024-01-25T15:00:00Z' },
        { id: 3, match_time: '2024-01-24T18:00:00Z' }
      ]
      
      const sorted = matches.sortedMatches.
      expect(sorted[0].match_time).toBe('2024-01-24T18:00:00Z')
      expect(sorted[1].match_time).toBe('2024-01-25T15:00:00Z')
      expect(sorted[2].match_time).toBe('2024-01-25T20:00:00Z')
    })

    it('liveMatches应该只包含进行中的比赛', () => {
      matches.matches.value = [
        { id: 1, status: 'upcoming' },
        { id: 2, status: 'live' },
        { id: 3, status: 'live' },
        { id: 4, status: 'finished' }
      ]
      
      const live = matches.liveMatches.
      expect(live).toHaveLength(2)
      expect(live.every(match => match.status === 'live')).toBe(true)
    })

    it('upcomingMatches应该只包含未开始的比赛', () => {
      matches.matches.value = [
        { id: 1, status: 'upcoming' },
        { id: 2, status: 'live' },
        { id: 3, status: 'upcoming' },
        { id: 4, status: 'finished' }
      ]
      
      const upcoming = matches.upcomingMatches.
      expect(upcoming).toHaveLength(2)
      expect(upcoming.every(match => match.status === 'upcoming')).toBe(true)
    })

    it('finishedMatches应该只包含已结束的比赛', () => {
      matches.matches.value = [
        { id: 1, status: 'upcoming' },
        { id: 2, status: 'live' },
        { id: 3, status: 'finished' },
        { id: 4, status: 'finished' }
      ]
      
      const finished = matches.finishedMatches.
      expect(finished).toHaveLength(2)
      expect(finished.every(match => match.status === 'finished')).toBe(true)
    })

    it('availableDates应该返回有比赛的日期', () => {
      matches.matches.value = [
        { id: 1, match_time: '2024-01-25T15:00:00Z' },
        { id: 2, match_time: '2024-01-25T20:00:00Z' },
        { id: 3, match_time: '2024-01-26T15:00:00Z' }
      ]
      
      const dates = matches.availableDates.
      expect(dates).toHaveLength(2)
      expect(dates).toContain('2024-01-25')
      expect(dates).toContain('2024-01-26')
    })
  })

  describe('获取比赛数据', () => {
    it('应该成功获取比赛列表', async () => {
      const mockMatches = [
        { id: 1, league: '英超', home_team: '曼联', away_team: '切尔西', match_time: '2024-01-25T15:00:00Z' },
        { id: 2, league: '西甲', home_team: '巴萨', away_team: '皇马', match_time: '2024-01-25T20:00:00Z' }
      ]
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      await matches.fetchMatches()
      
      expect(matches.loading.value).toBe(false)
      expect(matches.error.value).toBeNull()
      expect(matches.matches.value).toEqual(mockMatches)
      expect(toast.success).not.toHaveBeenCalled() // 成功时不显示toast
    })

    it('应该处理获取比赛失败', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
      }))
      
      await matches.fetchMatches()
      
      expect(matches.loading.value).toBe(false)
      expect(matches.error.value).toBe('Network error')
      expect(matches.matches.value).toEqual([])
      expect(toast.error).toHaveBeenCalledWith('获取比赛数据失败')
    })

    it('应该支持日期筛选参数', async () => {
      const mockMatches = [{ id: 1, match_time: '2024-01-25T15:00:00Z' }]
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      await matches.fetchMatches({ date: '2024-01-25' })
      
      expect(matchesAPI.getMatches).toHaveBeenCalledWith({ date: '2024-01-25' })
    })

    it('应该支持联赛筛选参数', async () => {
      const mockMatches = [{ id: 1, league: '英超' }]
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      await matches.fetchMatches({ leagues: ['英超'] })
      
      expect(matchesAPI.getMatches).toHaveBeenCalledWith({ leagues: ['英超'] })
    })

    it('加载状态应该正确设置', async () => {
      let resolvePromise
      const promise = new Promise(resolve => resolvePromise = resolve)
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
      }))
      
      const fetchPromise = matches.fetchMatches()
      
      // 立即检查loading状态
      expect(matches.loading.value).toBe(true)
      
      resolvePromise({ success: true, data: [] })
      await fetchPromise
      
      expect(matches.loading.value).toBe(false)
    })
  })

  describe('获取联赛列表', () => {
    it('应该成功获取联赛列表', async () => {
      const mockLeagues = ['英超', '西甲', '德甲', '意甲']
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      await matches.fetchLeagues()
      
      expect(matches.leagues.value).toEqual(mockLeagues)
      expect(matches.loading.value).toBe(false)
    })

    it('应该处理获取联赛失败', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
      }))
      
      await matches.fetchLeagues()
      
      expect(matches.leagues.value).toEqual([])
      expect(matches.error.value).toBe('API error')
    })
  })

  describe('获取比赛详情', () => {
    it('应该成功获取比赛详情', async () => {
      const mockMatchDetail = {
        id: 1,
        league: '英超',
        home_team: '曼联',
        away_team: '切尔西',
        match_time: '2024-01-25T15:00:00Z',
        odds
      }
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      const result = await matches.fetchMatchDetail(1)
      
      expect(result).toEqual(mockMatchDetail)
      expect(matches.loading.value).toBe(false)
    })

    it('应该处理比赛详情不存在的情况', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
          })
        }
      }))
      
      try {
        await matches.fetchMatchDetail(999)
      } catch (error) {
        expect(error.response.status).toBe(404)
        expect(toast.error).toHaveBeenCalledWith('比赛不存在')
      }
    })
  })

  describe('搜索功能', () => {
    it('应该更新搜索筛选条件', () => {
      matches.updateFilters({ search: '曼联' })
      
      expect(matches.filters.value.search).toBe('曼联')
    })

    it('应该支持多个筛选条件同时更新', () => {
      matches.updateFilters({
        leagues: ['英超', '西甲'],
        status: 'live',
        search: '巴萨'
      })
      
      expect(matches.filters.value.leagues).toEqual(['英超', '西甲'])
      expect(matches.filters.value.status).toBe('live')
      expect(matches.filters.value.search).toBe('巴萨')
    })

    it('应该重置筛选条件', () => {
      // 先设置一些筛选条件
      matches.filters.value = {
        leagues: ['英超'],
        status: 'live',
        search: 'test'
      }
      
      matches.resetFilters()
      
      expect(matches.filters.value).toEqual({
        leagues: [],
        status: 'all',
        search: ''
      })
    })
  })

  describe('日期选择', () => {
    it('应该更新选中的日期', () => {
      matches.setSelectedDate('2024-01-26')
      
      expect(matches.selectedDate.value).toBe('2024-01-26')
    })

    it('应该获取指定日期的比赛', () => {
      const mockMatches = [{ id: 1, match_time: '2024-01-26T15:00:00Z' }]
      
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI)
        }
      }))
      
      matches.selectDate('2024-01-26')
      
      expect(matches.selectedDate.value).toBe('2024-01-26')
      expect(matchesAPI.getMatches).toHaveBeenCalledWith({ date: '2024-01-26' })
    })
  })

  describe('实时更新', () => {
    it('应该设置实时更新连接', () => {
      matches.setupRealtimeUpdates()
      
      expect(matches.realtimeConnected.value).toBe(true)
    })

    it('应该处理比赛状态更新', async () => {
      const originalMatch = { id: 1, status: 'upcoming', home_score: 0, away_score: 0 }
      matches.matches.value = [originalMatch]
      
      const updatedMatch = { id: 1, status: 'live', current_time: '23\'', home_score: 1, away_score: 0 }
      
      await matches.handleMatchUpdate(updatedMatch)
      
      const match = matches.matches.value.find(m => m.id === 1)
      expect(match.status).toBe('live')
      expect(match.home_score).toBe(1)
      expect(match.away_score).toBe(0)
      expect(match.current_time).toBe('23\'')
    })

    it('应该处理比赛事件', async () => {
      const matchEvent = {
        match_id: 1,
        type: 'goal',
        team: 'home',
        player: 'Messi',
        time: '67\''
      }
      
      await matches.handleMatchEvent(matchEvent)
      
      expect(matches.matchEvents.value).toContainEqual(matchEvent)
      expect(toast.info).toHaveBeenCalledWith('进球: Messi (67\')')
    })

    it('应该限制比赛事件数量', async () => {
      // 添加超过最大数量的事件
      for (let i = 0; i < 15; i++) {
        await matches.handleMatchEvent({
          match_id: 1,
          type: 'event',
          description: `Event ${i}`,
          time: `${i}'`
        })
      }
      
      expect(matches.matchEvents.value).toHaveLength(10) // MAX_EVENTS = 10
    })

    it('组件销毁时应该清理实时连接', () => {
      matches.setupRealtimeUpdates()
      expect(matches.realtimeConnected.value).toBe(true)
      
      matches.cleanup()
      
      expect(matches.realtimeConnected.value).toBe(false)
    })
  })

  describe('工具函数', () => {
    it('getMatchById应该返回指定ID的比赛', () => {
      matches.matches.value = [
        { id: 1, home_team: 'Team A' },
        { id: 2, home_team: 'Team B' }
      ]
      
      const match = matches.getMatchById(1)
      expect(match.home_team).toBe('Team A')
      
      const notFound = matches.getMatchById(999)
      expect(notFound).toBeUndefined()
    })

    it('isMatchLive应该判断比赛是否为进行中', () => {
      expect(matches.isMatchLive({ status: 'live' })).toBe(true)
      expect(matches.isMatchLive({ status: 'upcoming' })).toBe(false)
      expect(matches.isMatchLive({ status: 'finished' })).toBe(false)
      expect(matches.isMatchLive(null)).toBe(false)
    })

    it('isMatchFinished应该判断比赛是否已结束', () => {
      expect(matches.isMatchFinished({ status: 'finished' })).toBe(true)
      expect(matches.isMatchFinished({ status: 'live' })).toBe(false)
      expect(matches.isMatchFinished({ status: 'upcoming' })).toBe(false)
    })

    it('formatMatchTime应该格式化比赛时间', () => {
      const match = { match_time: '2024-01-25T15:00:00Z' }
      
      const formatted = matches.formatMatchTime(match)
      expect(formatted).toBe('15:00')
      expect(matchUtils.formatMatchTime).toHaveBeenCalledWith(match.match_time)
    })

    it('getMatchStatusText应该返回状态文本', () => {
      const match = { status: 'live' }
      
      const statusText = matches.getMatchStatusText(match)
      expect(statusText).toBe('进行中')
      expect(matchUtils.getMatchStatusText).toHaveBeenCalledWith('live')
    })

    it('getMatchStatusClass应该返回状态类名', () => {
      const match = { status: 'upcoming' }
      
      const statusClass = matches.getMatchStatusClass(match)
      expect(statusClass).toBe('status-upcoming')
      expect(matchUtils.getMatchStatusClass).toHaveBeenCalledWith('upcoming')
    })
  })

  describe('数据验证', () => {
    it('应该验证比赛数据的完整性', () => {
      const validMatch = {
        id: 1,
        league: '英超',
        home_team: '曼联',
        away_team: '切尔西',
        match_time: '2024-01-25T15:00:00Z',
        status: 'upcoming'
      }
      
      const invalidMatch = {
        id: 1,
        // 缺少必要字段
      }
      
      expect(matches.isValidMatch(validMatch)).toBe(true)
      expect(matches.isValidMatch(invalidMatch)).toBe(false)
      expect(matches.isValidMatch(null)).toBe(false)
      expect(matches.isValidMatch({})).toBe(false)
    })

    it('应该过滤无效的比赛数据', () => {
      const mixedMatches = [
        { id: 1, league: '英超', home_team: 'Team A', away_team: 'Team B', match_time: '2024-01-25T15:00:00Z' },
        null,
        { id: 2 }, // 无效数据
        { id: 3, league: '西甲', home_team: 'Team C', away_team: 'Team D', match_time: '2024-01-25T20:00:00Z' }
      ]
      
      const validMatches = matches.filterValidMatches(mixedMatches)
      
      expect(validMatches).toHaveLength(2)
      expect(validMatches[0].id).toBe(1)
      expect(validMatches[1].id).toBe(3)
    })
  })

  describe('性能优化', () => {
    it('应该缓存过滤结果', () => {
      matches.matches.value = [
        { id: 1, league: '英超', status: 'upcoming' },
        { id: 2, league: '西甲', status: 'live' }
      ]
      
      // 第一次计算
      const result1 = matches.filteredMatches.
      // 相同条件下第二次计算应该使用缓存
      const result2 = matches.filteredMatches.
      expect(result1).toBe(result2) // 引用相同说明使用了缓存
    })

    it('筛选条件变化时应该重新计算', () => {
      matches.matches.value = [
        { id: 1, league: '英超', status: 'upcoming' },
        { id: 2, league: '西甲', status: 'live' }
      ]
      
      // 第一次计算
      const result1 = matches.filteredMatches.
      // 改变筛选条件
      matches.filters.value = { ...matches.filters.value, leagues: ['英超'] }
      
      // 第二次计算应该不同
      const result2 = matches.filteredMatches.
      expect(result1).not.toBe(result2)
      expect(result1).toHaveLength(2)
      expect(result2).toHaveLength(1)
    })
  })

  describe('错误处理', () => {
    it('应该处理网络超时', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI))
        }
      }))
      
      await matches.fetchMatches()
      
      expect(matches.error.value).toBe('timeout')
      expect(toast.error).toHaveBeenCalledWith('获取比赛数据失败')
    })

    it('应该处理服务器错误', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
            }
          })
        }
      }))
      
      await matches.fetchMatches()
      
      expect(matches.error.value).toBeDefined()
      expect(toast.error).toHaveBeenCalled()
    })

    it('应该处理认证失败', async () => {
      vi.doMock('../../api/modules/matches.js', () => ({
        matchesAPI
            }
          })
        }
      }))
      
      await matches.fetchMatches()
      
      // 认证失败时应该重定向到登录页
      expect(window.location.href).toContain('/login')
    })
  })

  describe('边界情况', () => {
    it('空数据应该正确处理', () => {
      matches.matches.value = []
      
      expect(matches.filteredMatches.value).toEqual([])
      expect(matches.groupedMatches.value).toEqual({})
      expect(matches.liveMatches.value).toEqual([])
      expect(matches.upcomingMatches.value).toEqual([])
      expect(matches.finishedMatches.value).toEqual([])
      expect(matches.availableDates.value).toEqual([])
    })

    it('大量数据应该正常处理', () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        league: `League ${(i % 10) + 1}`,
        home_team: `Team A${i}`,
        away_team: `Team B${i}`,
        match_time: `2024-01-25T${15 + (i % 9)}:00:00Z`,
        status: i % 3 === 0 ? 'upcoming' : i % 3 === 1 ? 'live' : 'finished'
      }))
      
      matches.matches.value = largeDataset
      
      expect(matches.filteredMatches.value).toHaveLength(1000)
      expect(matches.liveMatches.value.length).toBeGreaterThan(0)
      expect(matches.upcomingMatches.value.length).toBeGreaterThan(0)
      expect(matches.finishedMatches.value.length).toBeGreaterThan(0)
    })

    it('特殊字符应该正确处理', () => {
      const specialCharMatch = {
        id: 1,
        league: 'Premier-League',
        home_team: 'Manchester United FC',
        away_team: 'Real Madrid CF',
        match_time: '2024-01-25T15:00:00Z',
        status: 'upcoming'
      }
      
      matches.matches.value = [specialCharMatch]
      matches.filters.value = { ...matches.filters.value, search: 'United' }
      
      const filtered = matches.filteredMatches.
      expect(filtered).toHaveLength(1)
      expect(filtered[0].home_team).toContain('United')
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
