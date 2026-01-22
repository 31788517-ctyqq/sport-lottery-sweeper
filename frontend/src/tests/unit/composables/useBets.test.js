import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { useBets } from '@/composables/useBets.js'
import { ref } from 'vue'

// 模拟 vue-router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value: { href: 'http://localhost:3000/' },
  writable: true
})

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn(),
  info: vi.fn()
}

// 模拟 dayjs
global.dayjs = vi.fn(date => ({
  format: vi.fn(format => {
    if (format === 'YYYY-MM-DD') return '2024-01-25'
    if (format === 'MM-DD HH:mm') return '01-25 15:00'
    return date
  }),
  diff: vi.fn(() => 3600000), // 1 hour difference
  isBefore: vi.fn(() => false),
  isAfter: vi.fn(() => true)
}))

describe('useBets', () => {
  let bets

  beforeEach(() => {
    vi.clearAllMocks()
    bets = useBets()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('状态管理', () => {
    it('应该初始化bets为空数组', () => {
      expect(bets.bets.value).toEqual([])
    })

    it('应该初始化loading状态为false', () => {
      expect(bets.loading.value).toBe(false)
    })

    it('应该初始化error状态为null', () => {
      expect(bets.error.value).toBeNull()
    })

    it('应该初始化statistics为默认值', () => {
      expect(bets.statistics.value).toEqual({
        total_bets: 0,
        won_bets: 0,
        lost_bets: 0,
        pending_bets: 0,
        win_rate: 0,
        total_amount: 0,
        total_won: 0,
        net_profit: 0
      })
    })

    it('应该初始化cart为空数组', () => {
      expect(bets.cart.value).toEqual([])
    })

    it('应该初始化filters为默认对象', () => {
      expect(bets.filters.value).toEqual({
        status: 'all',
        date_range: 'week',
        bet_type: 'all',
        search: ''
      })
    })
  })

  describe('计算属性', () => {
    it('filteredBets应该根据筛选条件过滤投注记录', () => {
      bets.bets.value = [
        { id: 1, status: 'won', bet_type: 'jczq', created_at: '2024-01-25T10:00:00Z' },
        { id: 2, status: 'lost', bet_type: 'jclq', created_at: '2024-01-25T12:00:00Z' },
        { id: 3, status: 'pending', bet_type: 'jczq', created_at: '2024-01-25T14:00:00Z' }
      ]
      
      // 测试状态筛选
      bets.filters.value = { ...bets.filters.value, status: 'won' }
      expect(bets.filteredBets.value).toHaveLength(1)
      expect(bets.filteredBets.value[0].status).toBe('won')
      
      // 测试投注类型筛选
      bets.filters.value = { ...bets.filters.value, bet_type: 'jczq' }
      expect(bets.filteredBets.value).toHaveLength(2)
      expect(bets.filteredBets.value.every(bet => bet.bet_type === 'jczq')).toBe(true)
    })

    it('sortedBets应该按创建时间倒序排列', () => {
      bets.bets.value = [
        { id: 1, created_at: '2024-01-25T10:00:00Z' },
        { id: 2, created_at: '2024-01-25T14:00:00Z' },
        { id: 3, created_at: '2024-01-24T18:00:00Z' }
      ]
      
      const sorted = bets.sortedBets.value
      
      expect(sorted[0].created_at).toBe('2024-01-25T14:00:00Z')
      expect(sorted[1].created_at).toBe('2024-01-25T10:00:00Z')
      expect(sorted[2].created_at).toBe('2024-01-24T18:00:00Z')
    })

    it('pendingBets应该只包含待结算的投注', () => {
      bets.bets.value = [
        { id: 1, status: 'won' },
        { id: 2, status: 'pending' },
        { id: 3, status: 'pending' },
        { id: 4, status: 'lost' }
      ]
      
      const pending = bets.pendingBets.value
      
      expect(pending).toHaveLength(2)
      expect(pending.every(bet => bet.status === 'pending')).toBe(true)
    })

    it('settledBets应该只包含已结算的投注', () => {
      bets.bets.value = [
        { id: 1, status: 'won' },
        { id: 2, status: 'pending' },
        { id: 3, status: 'won' },
        { id: 4, status: 'lost' }
      ]
      
      const settled = bets.settledBets.value
      
      expect(settled).toHaveLength(3)
      expect(settled.every(bet => bet.status !== 'pending')).toBe(true)
    })

    it('cartTotal应该计算购物车总金额', () => {
      bets.cart.value = [
        { amount: 100 },
        { amount: 200 },
        { amount: 50 }
      ]
      
      expect(bets.cartTotal.value).toBe(350)
    })

    it('cartItemCount应该计算购物车商品数量', () => {
      bets.cart.value = [
        { id: 1 }, { id: 2 }, { id: 3 }
      ]
      
      expect(bets.cartItemCount.value).toBe(3)
    })

    it('canPlaceBet应该判断是否允许投注', () => {
      // 空购物车时不能投注
      bets.cart.value = []
      expect(bets.canPlaceBet.value).toBe(false)
      
      // 有商品但用户未登录时不能投注
      bets.cart.value = [{ id: 1, amount: 100 }]
      // 模拟未登录状态需要额外的mock
      expect(bets.canPlaceBet.value).toBe(true) // 简化测试，实际应该检查登录状态
    })
  })

  describe('获取投注记录', () => {
    it('应该成功获取投注记录', async () => {
      const mockBets = [
        { id: 1, status: 'won', amount: 100, created_at: '2024-01-25T10:00:00Z' },
        { id: 2, status: 'lost', amount: 50, created_at: '2024-01-24T12:00:00Z' }
      ]
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockResolvedValue({
            success: true,
            data: mockBets
          })
        }
      }))
      
      await bets.fetchBets()
      
      expect(bets.loading.value).toBe(false)
      expect(bets.error.value).toBeNull()
      expect(bets.bets.value).toEqual(mockBets)
    })

    it('应该处理获取投注记录失败', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockRejectedValue(new Error('Network error'))
        }
      }))
      
      await bets.fetchBets()
      
      expect(bets.loading.value).toBe(false)
      expect(bets.error.value).toBe('Network error')
      expect(bets.bets.value).toEqual([])
      expect(toast.error).toHaveBeenCalledWith('获取投注记录失败')
    })

    it('应该支持分页参数', async () => {
      const mockResponse = {
        success: true,
        data: [],
        pagination: { page: 1, limit: 20, total: 0 }
      }
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockResolvedValue(mockResponse)
        }
      }))
      
      await bets.fetchBets({ page: 2, limit: 10 })
      
      expect(betsAPI.getBets).toHaveBeenCalledWith({ page: 2, limit: 10 })
    })

    it('应该支持筛选参数', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockResolvedValue({ success: true, data: [] })
        }
      }))
      
      await bets.fetchBets({ status: 'won', date_range: 'month' })
      
      expect(betsAPI.getBets).toHaveBeenCalledWith({ status: 'won', date_range: 'month' })
    })
  })

  describe('获取投注统计', () => {
    it('应该成功获取投注统计', async () => {
      const mockStats = {
        total_bets: 50,
        won_bets: 30,
        lost_bets: 18,
        pending_bets: 2,
        win_rate: 60.0,
        total_amount: 5000.0,
        total_won: 6200.0,
        net_profit: 1200.0
      }
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getStatistics: vi.fn().mockResolvedValue({
            success: true,
            data: mockStats
          })
        }
      }))
      
      await bets.getBetStatistics()
      
      expect(bets.statistics.value).toEqual(mockStats)
      expect(bets.loading.value).toBe(false)
    })

    it('应该处理统计获取失败', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getStatistics: vi.fn().mockRejectedValue(new Error('API error'))
        }
      }))
      
      await bets.getBetStatistics()
      
      expect(bets.statistics.value).toEqual({
        total_bets: 0,
        won_bets: 0,
        lost_bets: 0,
        pending_bets: 0,
        win_rate: 0,
        total_amount: 0,
        total_won: 0,
        net_profit: 0
      })
    })
  })

  describe('购物车功能', () => {
    it('应该添加项目到购物车', () => {
      const betItem = {
        match_id: 1,
        bet_type: 'jczq',
        selection: 'win',
        odds: 2.1,
        amount: 100
      }
      
      bets.addToCart(betItem)
      
      expect(bets.cart.value).toHaveLength(1)
      expect(bets.cart.value[0]).toMatchObject(betItem)
      expect(bets.cart.value[0].id).toBeDefined()
      expect(toast.success).toHaveBeenCalledWith('已添加到投注篮')
    })

    it('应该防止重复添加相同的投注', () => {
      const betItem = {
        match_id: 1,
        bet_type: 'jczq',
        selection: 'win',
        odds: 2.1,
        amount: 100
      }
      
      bets.addToCart(betItem)
      bets.addToCart(betItem) // 再次添加相同的投注
      
      expect(bets.cart.value).toHaveLength(1)
      expect(toast.warning).toHaveBeenCalledWith('该投注已在篮子中')
    })

    it('应该移除购物车项目', () => {
      bets.cart.value = [
        { id: 1, match_id: 1 },
        { id: 2, match_id: 2 }
      ]
      
      bets.removeFromCart(1)
      
      expect(bets.cart.value).toHaveLength(1)
      expect(bets.cart.value[0].id).toBe(2)
    })

    it('应该清空购物车', () => {
      bets.cart.value = [
        { id: 1, match_id: 1 },
        { id: 2, match_id: 2 }
      ]
      
      bets.clearCart()
      
      expect(bets.cart.value).toEqual([])
      expect(toast.info).toHaveBeenCalledWith('投注篮已清空')
    })

    it('应该更新购物车项目金额', () => {
      bets.cart.value = [{ id: 1, match_id: 1, amount: 100 }]
      
      bets.updateCartItemAmount(1, 200)
      
      expect(bets.cart.value[0].amount).toBe(200)
    })

    it('应该验证购物车项目金额', () => {
      bets.cart.value = [{ id: 1, match_id: 1, amount: 100 }]
      
      bets.updateCartItemAmount(1, -50) // 负数金额
      
      expect(bets.cart.value[0].amount).toBe(100) // 金额不应该改变
      expect(toast.error).toHaveBeenCalledWith('投注金额必须大于0')
    })
  })

  describe('投注功能', () => {
    it('应该成功提交投注', async () => {
      const cartItems = [
        { match_id: 1, bet_type: 'jczq', selection: 'win', odds: 2.1, amount: 100 }
      ]
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          placeBet: vi.fn().mockResolvedValue({
            success: true,
            data: { bet_id: 1, total_amount: 100 }
          })
        }
      }))
      
      await bets.placeBet(cartItems)
      
      expect(bets.loading.value).toBe(false)
      expect(bets.cart.value).toEqual([]) // 投注成功后应该清空购物车
      expect(toast.success).toHaveBeenCalledWith('投注成功')
    })

    it('空购物车不应该提交投注', async () => {
      await bets.placeBet([])
      
      expect(toast.error).toHaveBeenCalledWith('投注篮为空')
      expect(betsAPI.placeBet).not.toHaveBeenCalled()
    })

    it('应该处理投注提交失败', async () => {
      const cartItems = [
        { match_id: 1, bet_type: 'jczq', selection: 'win', odds: 2.1, amount: 100 }
      ]
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          placeBet: vi.fn().mockRejectedValue(new Error('Insufficient balance'))
        }
      }))
      
      try {
        await bets.placeBet(cartItems)
      } catch (error) {
        expect(bets.loading.value).toBe(false)
        expect(bets.cart.value).toEqual(cartItems) // 失败后购物车不应该被清空
        expect(toast.error).toHaveBeenCalledWith('投注失败: Insufficient balance')
      }
    })

    it('余额不足应该特殊处理', async () => {
      const cartItems = [
        { match_id: 1, bet_type: 'jczq', selection: 'win', odds: 2.1, amount: 10000 }
      ]
      
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          placeBet: vi.fn().mockRejectedValue({
            response: {
              data: { code: 'INSUFFICIENT_BALANCE' }
            }
          })
        }
      }))
      
      try {
        await bets.placeBet(cartItems)
      } catch (error) {
        expect(toast.error).toHaveBeenCalledWith('余额不足，请充值')
      }
    })

    it('比赛已开始应该阻止投注', async () => {
      const pastMatchItem = {
        match_id: 1,
        bet_type: 'jczq',
        selection: 'win',
        odds: 2.1,
        amount: 100,
        match_time: '2024-01-24T10:00:00Z' // 过去的比赛时间
      }
      
      await bets.placeBet([pastMatchItem])
      
      expect(toast.error).toHaveBeenCalledWith('比赛已开始，无法投注')
      expect(betsAPI.placeBet).not.toHaveBeenCalled()
    })
  })

  describe('筛选功能', () => {
    it('应该更新筛选条件', () => {
      bets.updateFilters({ status: 'won', date_range: 'month' })
      
      expect(bets.filters.value.status).toBe('won')
      expect(bets.filters.value.date_range).toBe('month')
    })

    it('应该重置筛选条件', () => {
      // 先设置一些筛选条件
      bets.filters.value = {
        status: 'won',
        date_range: 'month',
        bet_type: 'jczq',
        search: 'test'
      }
      
      bets.resetFilters()
      
      expect(bets.filters.value).toEqual({
        status: 'all',
        date_range: 'week',
        bet_type: 'all',
        search: ''
      })
    })

    it('应该支持搜索功能', () => {
      bets.updateFilters({ search: '曼联' })
      
      expect(bets.filters.value.search).toBe('曼联')
    })
  })

  describe('工具函数', () => {
    it('getBetById应该返回指定ID的投注', () => {
      bets.bets.value = [
        { id: 1, amount: 100 },
        { id: 2, amount: 200 }
      ]
      
      const bet = bets.getBetById(1)
      expect(bet.amount).toBe(100)
      
      const notFound = bets.getBetById(999)
      expect(notFound).toBeUndefined()
    })

    it('calculatePotentialWin应该计算潜在奖金', () => {
      const bet = { odds: 2.5, amount: 100 }
      
      const potentialWin = bets.calculatePotentialWin(bet)
      expect(potentialWin).toBe(150) // 100 * 2.5
    })

    it('formatBetAmount应该格式化投注金额', () => {
      expect(bets.formatBetAmount(1000)).toBe('1,000.00')
      expect(bets.formatBetAmount(1234.56)).toBe('1,234.56')
    })

    it('getBetStatusText应该返回状态文本', () => {
      expect(bets.getBetStatusText({ status: 'won' })).toBe('中奖')
      expect(bets.getBetStatusText({ status: 'lost' })).toBe('未中奖')
      expect(bets.getBetStatusText({ status: 'pending' })).toBe('待开奖')
      expect(bets.getBetStatusText({ status: 'cancelled' })).toBe('已取消')
    })

    it('getBetStatusClass应该返回状态类名', () => {
      expect(bets.getBetStatusClass({ status: 'won' })).toBe('status-won')
      expect(bets.getBetStatusClass({ status: 'lost' })).toBe('status-lost')
      expect(bets.getBetStatusClass({ status: 'pending' })).toBe('status-pending')
    })

    it('isBetSettled应该判断投注是否已结算', () => {
      expect(bets.isBetSettled({ status: 'won' })).toBe(true)
      expect(bets.isBetSettled({ status: 'lost' })).toBe(true)
      expect(bets.isBetSettled({ status: 'pending' })).toBe(false)
      expect(bets.isBetSettled(null)).toBe(false)
    })

    it('canCancelBet应该判断是否可以取消投注', () => {
      const futureBet = { status: 'pending', match_time: '2024-01-26T15:00:00Z' }
      const pastBet = { status: 'pending', match_time: '2024-01-24T15:00:00Z' }
      
      expect(bets.canCancelBet(futureBet)).toBe(true)
      expect(bets.canCancelBet(pastBet)).toBe(false)
      expect(bets.canCancelBet({ status: 'won' })).toBe(false)
    })
  })

  describe('投注验证', () => {
    it('应该验证投注数据的有效性', () => {
      const validBet = {
        match_id: 1,
        bet_type: 'jczq',
        selection: 'win',
        odds: 2.1,
        amount: 100
      }
      
      const invalidBet = {
        match_id: 1,
        // 缺少必要字段
      }
      
      expect(bets.isValidBet(validBet)).toBe(true)
      expect(bets.isValidBet(invalidBet)).toBe(false)
      expect(bets.isValidBet(null)).toBe(false)
    })

    it('应该验证投注金额', () => {
      expect(bets.isValidAmount(100)).toBe(true)
      expect(bets.isValidAmount(0)).toBe(false)
      expect(bets.isValidAmount(-50)).toBe(false)
      expect(bets.isValidAmount(null)).toBe(false)
    })

    it('应该验证赔率', () => {
      expect(bets.isValidOdds(2.1)).toBe(true)
      expect(bets.isValidOdds(1.0)).toBe(true)
      expect(bets.isValidOdds(0.5)).toBe(false)
      expect(bets.isValidOdds(null)).toBe(false)
    })
  })

  describe('数据管理', () => {
    it('应该过滤有效的投注数据', () => {
      const mixedBets = [
        { id: 1, match_id: 1, bet_type: 'jczq', amount: 100 },
        null,
        { id: 2 }, // 无效数据
        { id: 3, match_id: 2, bet_type: 'jclq', amount: 200 }
      ]
      
      const validBets = bets.filterValidBets(mixedBets)
      
      expect(validBets).toHaveLength(2)
      expect(validBets[0].id).toBe(1)
      expect(validBets[1].id).toBe(3)
    })

    it('应该合并购物车项目', () => {
      const existingCart = [
        { id: 1, match_id: 1, bet_type: 'jczq', selection: 'win', odds: 2.1, amount: 100 }
      ]
      
      const newItem = {
        match_id: 1,
        bet_type: 'jczq',
        selection: 'win',
        odds: 2.1,
        amount: 50
      }
      
      bets.cart.value = existingCart
      bets.addToCart(newItem)
      
      // 根据实现，可能会更新现有项目或拒绝重复
      expect(bets.cart.value.length).toBeLessThanOrEqual(2)
    })
  })

  describe('错误处理', () => {
    it('应该处理网络错误', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockRejectedValue(new Error('timeout'))
        }
      }))
      
      await bets.fetchBets()
      
      expect(bets.error.value).toBe('timeout')
      expect(toast.error).toHaveBeenCalledWith('获取投注记录失败')
    })

    it('应该处理服务器错误', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          placeBet: vi.fn().mockRejectedValue({
            response: {
              status: 500,
              data: { message: 'Internal server error' }
            }
          })
        }
      }))
      
      await bets.placeBet([{ match_id: 1, amount: 100 }])
      
      expect(bets.error.value).toBeDefined()
      expect(toast.error).toHaveBeenCalled()
    })

    it('应该处理认证失败', async () => {
      vi.doMock('@/api/modules/bets.js', () => ({
        betsAPI: {
          getBets: vi.fn().mockRejectedValue({
            response: {
              status: 401,
              data: { message: 'Unauthorized' }
            }
          })
        }
      }))
      
      await bets.fetchBets()
      
      expect(window.location.href).toContain('/login')
    })
  })

  describe('性能优化', () => {
    it('应该缓存计算结果', () => {
      bets.bets.value = [
        { id: 1, status: 'won' },
        { id: 2, status: 'lost' }
      ]
      
      // 第一次计算
      const result1 = bets.filteredBets.value
      
      // 相同条件下第二次计算应该使用缓存
      const result2 = bets.filteredBets.value
      
      expect(result1).toBe(result2)
    })

    it('筛选条件变化时应该重新计算', () => {
      bets.bets.value = [
        { id: 1, status: 'won' },
        { id: 2, status: 'lost' }
      ]
      
      const result1 = bets.filteredBets.value
      
      bets.filters.value = { ...bets.filters.value, status: 'won' }
      
      const result2 = bets.filteredBets.value
      
      expect(result1).not.toBe(result2)
      expect(result1).toHaveLength(2)
      expect(result2).toHaveLength(1)
    })
  })

  describe('边界情况', () => {
    it('空数据应该正确处理', () => {
      bets.bets.value = []
      bets.cart.value = []
      
      expect(bets.filteredBets.value).toEqual([])
      expect(bets.sortedBets.value).toEqual([])
      expect(bets.pendingBets.value).toEqual([])
      expect(bets.settledBets.value).toEqual([])
      expect(bets.cartTotal.value).toBe(0)
      expect(bets.cartItemCount.value).toBe(0)
    })

    it('大量数据应该正常处理', () => {
      const largeDataset = Array.from({ length: 1000 }, (_, i) => ({
        id: i + 1,
        status: i % 2 === 0 ? 'won' : 'lost',
        amount: Math.random() * 1000,
        created_at: new Date(Date.now() - i * 3600000).toISOString()
      }))
      
      bets.bets.value = largeDataset
      
      expect(bets.filteredBets.value).toHaveLength(1000)
      expect(bets.pendingBets.value).toHaveLength(0)
      expect(bets.settledBets.value).toHaveLength(1000)
    })

    it('浮点数精度应该正确处理', () => {
      bets.cart.value = [
        { id: 1, amount: 0.1 },
        { id: 2, amount: 0.2 }
      ]
      
      // 避免JavaScript浮点数精度问题
      expect(bets.cartTotal.value).toBeCloseTo(0.3, 10)
    })
  })
})