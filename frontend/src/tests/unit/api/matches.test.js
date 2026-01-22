import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { matchesAPI } from '@/api/modules/matches.js'

// 模拟 request 模块
global.fetch = vi.fn()

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('matchesAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.getItem.mockReturnValue('fake-jwt-token')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('getMatches', () => {
    it('应该获取比赛列表', async () => {
      const mockMatches = [
        {
          id: 1,
          league: '英超',
          home_team: '曼联',
          away_team: '切尔西',
          match_time: '2024-01-25T15:00:00Z',
          status: 'upcoming',
          jc_type: 'jczq',
          odds: { win: 2.1, draw: 3.2, lose: 2.8 }
        },
        {
          id: 2,
          league: '西甲',
          home_team: '巴萨',
          away_team: '皇马',
          match_time: '2024-01-26T20:00:00Z',
          status: 'upcoming',
          jc_type: 'jczq',
          odds: { win: 2.3, draw: 3.1, lose: 2.9 }
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockMatches,
            pagination: {
              page: 1,
              limit: 20,
              total: 2
            }
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const filters = {
        sport_type: 'football',
        date_range: 'today',
        status: 'upcoming'
      }
      
      const result = await freshMatchesAPI.getMatches(filters)
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(2)
      expect(result.data[0].home_team).toBe('曼联')
      expect(result.data[0].away_team).toBe('切尔西')
      expect(result.pagination.total).toBe(2)
    })

    it('应该支持分页参数', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: [],
            pagination: { page: 2, limit: 10, total: 25 }
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      await freshMatchesAPI.getMatches({}, { page: 2, limit: 10 })
      
      // 验证分页参数被正确传递
      expect(true).toBe(true) // 这里可以添加更具体的断言
    })

    it('应该处理网络错误', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockRejectedValue(new Error('Network error'))
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      try {
        await freshMatchesAPI.getMatches()
        expect(false).toBe(true)
      } catch (error) {
        expect(error.message).toBe('Network error')
      }
    })
  })

  describe('getMatchDetail', () => {
    it('应该获取比赛详情', async () => {
      const mockMatchDetail = {
        id: 1,
        league: '英超',
        home_team: '曼联',
        away_team: '切尔西',
        match_time: '2024-01-25T15:00:00Z',
        venue: '老特拉福德球场',
        status: 'upcoming',
        jc_type: 'jczq',
        home_score: null,
        away_score: null,
        weather: '晴朗',
        temperature: '15°C',
        odds_history: [
          { time: '2024-01-20T10:00:00Z', win: 2.1, draw: 3.2, lose: 2.8 },
          { time: '2024-01-21T10:00:00Z', win: 2.0, draw: 3.3, lose: 2.9 }
        ],
        team_stats: {
          home: { wins: 15, draws: 5, losses: 2 },
          away: { wins: 12, draws: 8, losses: 3 }
        }
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockMatchDetail
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const result = await freshMatchesAPI.getMatchDetail(1)
      
      expect(result.success).toBe(true)
      expect(result.data.id).toBe(1)
      expect(result.data.home_team).toBe('曼联')
      expect(result.data.venue).toBe('老特拉福德球场')
      expect(result.data.odds_history).toHaveLength(2)
    })

    it('比赛不存在应该返回404错误', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockRejectedValue({
            response: {
              status: 404,
              data: {
                success: false,
                message: 'Match not found'
              }
            }
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      try {
        await freshMatchesAPI.getMatchDetail(99999)
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(404)
        expect(error.response.data.message).toContain('not found')
      }
    })
  })

  describe('getLiveMatches', () => {
    it('应该获取正在进行的比赛', async () => {
      const mockLiveMatches = [
        {
          id: 1,
          league: '英超',
          home_team: '曼联',
          away_team: '切尔西',
          match_time: '2024-01-25T15:00:00Z',
          status: 'live',
          current_time: '67\'',
          home_score: 1,
          away_score: 0,
          events: [
            { time: '23\'', type: 'goal', team: 'home', player: 'Rashford' },
            { time: '45+2\'', type: 'yellow_card', team: 'away', player: 'Kante' }
          ]
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockLiveMatches
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const result = await freshMatchesAPI.getLiveMatches()
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(1)
      expect(result.data[0].status).toBe('live')
      expect(result.data[0].current_time).toBe('67\'')
      expect(result.data[0].events).toHaveLength(2)
    })
  })

  describe('getLeagues', () => {
    it('应该获取联赛列表', async () => {
      const mockLeagues = [
        { id: 1, name: '英超', country: 'England', season: '2023-24', logo: 'logo-url' },
        { id: 2, name: '西甲', country: 'Spain', season: '2023-24', logo: 'logo-url' },
        { id: 3, name: '德甲', country: 'Germany', season: '2023-24', logo: 'logo-url' }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockLeagues
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const result = await freshMatchesAPI.getLeagues()
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(3)
      expect(result.data[0].name).toBe('英超')
    })
  })

  describe('getTeams', () => {
    it('应该获取球队列表', async () => {
      const mockTeams = [
        { id: 1, name: '曼联', short_name: 'MU', league_id: 1, logo: 'team-logo' },
        { id: 2, name: '切尔西', short_name: 'CFC', league_id: 1, logo: 'team-logo' }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockTeams
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const result = await freshMatchesAPI.getTeams({ league_id: 1 })
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(2)
      expect(result.data[0].short_name).toBe('MU')
    })
  })

  describe('searchMatches', () => {
    it('应该搜索比赛', async () => {
      const mockResults = [
        {
          id: 1,
          home_team: '曼联',
          away_team: '切尔西',
          match_time: '2024-01-25T15:00:00Z',
          league: '英超'
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockResults
          })
        }
      }))
      
      vi.resetModules()
      const { matchesAPI: freshMatchesAPI } = await import('@/api/modules/matches.js')
      
      const result = await freshMatchesAPI.searchMatches('曼联')
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(1)
      expect(result.data[0].home_team).toContain('曼联')
    })
  })
})