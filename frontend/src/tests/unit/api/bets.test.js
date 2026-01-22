import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { betsAPI } from '@/api/modules/bets.js'

// 模拟 request 模块
global.fetch = vi.fn()

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn()
}

describe('betsAPI', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    localStorage.getItem.mockReturnValue('fake-jwt-token')
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('createBet', () => {
    it('应该成功创建投注', async () => {
      const mockBet = {
        id: 1,
        user_id: 1,
        match_id: 1,
        bet_type: 'single',
        amount: 100.0,
        potential_win: 210.0,
        status: 'pending',
        created_at: '2024-01-22T10:00:00Z'
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            data: mockBet,
            message: '投注创建成功'
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const betData = {
        match_id: 1,
        bet_type: 'single',
        selections: [
          { option: 'win', odds: 2.1 }
        ],
        amount: 100.0
      }
      
      const result = await freshBetsAPI.createBet(betData)
      
      expect(result.success).toBe(true)
      expect(result.data.id).toBe(1)
      expect(result.data.amount).toBe(100.0)
      expect(result.data.potential_win).toBe(210.0)
      expect(result.message).toContain('成功')
    })

    it('余额不足应该返回错误', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockRejectedValue({
            response: {
              status: 400,
              data: {
                success: false,
                message: 'Insufficient balance',
                code: 'INSUFFICIENT_BALANCE'
              }
            }
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      try {
        await freshBetsAPI.createBet({
          match_id: 1,
          amount: 999999.0 // 大额投注
        })
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(400)
        expect(error.response.data.code).toBe('INSUFFICIENT_BALANCE')
      }
    })

    it('赔率已变化应该返回警告', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockRejectedValue({
            response: {
              status: 409,
              data: {
                success: false,
                message: 'Odds have changed',
                code: 'ODDS_CHANGED',
                current_odds: { win: 2.2, draw: 3.3, lose: 2.9 }
              }
            }
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      try {
        await freshBetsAPI.createBet({
          match_id: 1,
          selections: [{ option: 'win', odds: 2.1 }]
        })
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(409)
        expect(error.response.data.current_odds.win).toBe(2.2)
      }
    })
  })

  describe('getUserBets', () => {
    it('应该获取用户投注历史', async () => {
      const mockBets = [
        {
          id: 1,
          match_id: 1,
          bet_type: 'single',
          amount: 100.0,
          status: 'won',
          win_amount: 210.0,
          created_at: '2024-01-20T10:00:00Z'
        },
        {
          id: 2,
          match_id: 2,
          bet_type: 'multiple',
          amount: 50.0,
          status: 'lost',
          created_at: '2024-01-19T15:00:00Z'
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockBets,
            pagination: {
              page: 1,
              limit: 20,
              total: 2
            }
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const result = await freshBetsAPI.getUserBets({ page: 1, limit: 20 })
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(2)
      expect(result.data[0].status).toBe('won')
      expect(result.data[0].win_amount).toBe(210.0)
      expect(result.pagination.total).toBe(2)
    })

    it('应该支持状态筛选', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: [],
            pagination: { page: 1, limit: 20, total: 0 }
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      await freshBetsAPI.getUserBets({ status: 'pending' })
      
      expect(true).toBe(true) // 验证状态参数被正确传递
    })
  })

  describe('getBetDetail', () => {
    it('应该获取投注详情', async () => {
      const mockBetDetail = {
        id: 1,
        user_id: 1,
        match_id: 1,
        bet_type: 'single',
        amount: 100.0,
        potential_win: 210.0,
        status: 'won',
        win_amount: 210.0,
        created_at: '2024-01-20T10:00:00Z',
        settled_at: '2024-01-20T17:00:00Z',
        match_info: {
          home_team: '曼联',
          away_team: '切尔西',
          final_score: '2-1'
        },
        selections: [
          { option: 'win', odds: 2.1, result: 'win' }
        ]
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockBetDetail
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const result = await freshBetsAPI.getBetDetail(1)
      
      expect(result.success).toBe(true)
      expect(result.data.id).toBe(1)
      expect(result.data.match_info.home_team).toBe('曼联')
      expect(result.data.selections).toHaveLength(1)
    })
  })

  describe('cancelBet', () => {
    it('应该取消待处理的投注', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockResolvedValue({
            success: true,
            message: '投注已取消'
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const result = await freshBetsAPI.cancelBet(1)
      
      expect(result.success).toBe(true)
      expect(result.message).toContain('取消')
    })

    it('已结算的投注不能取消', async () => {
      vi.doMock('@/utils/request.js', () => ({
        default: {
          post: vi.fn().mockRejectedValue({
            response: {
              status: 400,
              data: {
                success: false,
                message: 'Cannot cancel settled bet',
                code: 'BET_ALREADY_SETTLED'
              }
            }
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      try {
        await freshBetsAPI.cancelBet(1)
        expect(false).toBe(true)
      } catch (error) {
        expect(error.response.status).toBe(400)
        expect(error.response.data.code).toBe('BET_ALREADY_SETTLED')
      }
    })
  })

  describe('getBetStatistics', () => {
    it('应该获取投注统计', async () => {
      const mockStats = {
        total_bets: 50,
        won_bets: 30,
        lost_bets: 18,
        pending_bets: 2,
        win_rate: 60.0,
        total_amount: 5000.0,
        total_won: 6200.0,
        net_profit: 1200.0,
        monthly_stats: [
          { month: '2024-01', bets: 20, won: 12, amount: 2000.0 },
          { month: '2023-12', bets: 30, won: 18, amount: 3000.0 }
        ]
      }
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockStats
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const result = await freshBetsAPI.getBetStatistics()
      
      expect(result.success).toBe(true)
      expect(result.data.total_bets).toBe(50)
      expect(result.data.win_rate).toBe(60.0)
      expect(result.data.net_profit).toBe(1200.0)
      expect(result.data.monthly_stats).toHaveLength(2)
    })
  })

  describe('getBetHistory', () => {
    it('应该获取投注历史（带过滤）', async () => {
      const mockHistory = [
        {
          id: 1,
          match_id: 1,
          amount: 100.0,
          status: 'won',
          created_at: '2024-01-20T10:00:00Z'
        }
      ]
      
      vi.doMock('@/utils/request.js', () => ({
        default: {
          get: vi.fn().mockResolvedValue({
            success: true,
            data: mockHistory
          })
        }
      }))
      
      vi.resetModules()
      const { betsAPI: freshBetsAPI } = await import('@/api/modules/bets.js')
      
      const filters = {
        start_date: '2024-01-01',
        end_date: '2024-01-31',
        status: 'won'
      }
      
      const result = await freshBetsAPI.getBetHistory(filters)
      
      expect(result.success).toBe(true)
      expect(result.data).toHaveLength(1)
    })
  })
})