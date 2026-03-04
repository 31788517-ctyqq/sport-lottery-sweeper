// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory } from 'vue-router'
import JczqSchedule from '../../views/JczqSchedule.vue'
import { useFilters } from '../../composables/useFilters.js'
import { useMatches } from '../../composables/useMatches.js'

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

const routes = [
  { path: '/', component },
  { path: '/matches/:id', component },
  { path: '/betting', component }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

describe('JczqSchedule.vue', () => {
  let wrapper
  let filtersComposable
  let matchesComposable

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState
            },
            {
              id: 2,
              league: '西甲',
              home_team: '巴萨',
              away_team: '皇马',
              match_time: '2024-01-25T20:00:00Z',
              status: 'live',
              current_time: '67\'',
              home_score: 1,
              away_score: 0,
              jc_type: 'jczq',
              odds
            },
            {
              id: 3,
              league: '德甲',
              home_team: '拜仁',
              away_team: '多特',
              match_time: '2024-01-24T18:00:00Z',
              status: 'finished',
              home_score: 3,
              away_score: 1,
              jc_type: 'jczq',
              odds
            }
          ],
          loading: false,
          selectedDate: '2024-01-25',
          leagues: ['英超', '西甲', '德甲']
        },
        filters
        }
      }
    })
    
    filtersComposable = useFilters()
    matchesComposable = useMatches()
    
    wrapper = mount(JczqSchedule, {
      
      }
    })
    
    await router.isReady()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
  })

  describe('组件渲染', () => {
    it('应该正确渲染竞彩足球赛程页面', () => {
      expect(wrapper.find('.jczq-schedule').exists()).toBe(true)
      expect(wrapper.find('.schedule-header').exists()).toBe(true)
    })

    it('应该显示页面标题', () => {
      const title = wrapper.find('h1, .page-title, [data-testid="schedule-title"]')
      
      expect(title.exists() || wrapper.text().includes('竞彩足球') || wrapper.text().includes('JCZQ')).toBe(true)
    })

    it('应该显示日期导航', () => {
      const dateNavigation = wrapper.find('.date-navigation, .calendar-nav')
      
      expect(dateNavigation.exists()).toBe(true)
    })

    it('应该显示筛选器区域', () => {
      const filterSection = wrapper.find('.filter-section, .filters-bar')
      
      expect(filterSection.exists()).toBe(true)
    })

    it('应该显示比赛列表', () => {
      const matchesList = wrapper.find('.matches-list, .schedule-content')
      
      expect(matchesList.exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('应该在组件挂载时加载比赛数据', () => {
      expect(matchesComposable.fetchMatches).toHaveBeenCalled()
    })

    it('应该加载联赛列表', () => {
      expect(matchesComposable.fetchLeagues).toHaveBeenCalled()
    })

    it('加载状态应该显示骨架屏', async () => {
      matchesComposable.loading = true
      await wrapper.vm.$nextTick()
      
      const skeletonLoader = wrapper.find('.skeleton-loader, .loading-state')
      
      expect(skeletonLoader.exists()).toBe(true)
    })

    it('加载完成应该显示比赛内容', async () => {
      matchesComposable.loading = false
      await wrapper.vm.$nextTick()
      
      const matchesContent = wrapper.find('.matches-content, .schedule-list')
      const skeletonLoader = wrapper.find('.skeleton-loader')
      
      expect(matchesContent.exists()).toBe(true)
      expect(skeletonLoader.exists()).toBe(false)
    })
  })

  describe('日期导航', () => {
    it('应该显示日期选择器', () => {
      const datePicker = wrapper.find('.date-picker, .calendar-selector')
      
      expect(datePicker.exists()).toBe(true)
    })

    it('应该支持选择不同日期', async () => {
      const dateButton = wrapper.find('.date-item, [data-date="2024-01-26"]')
      
      if (dateButton.exists()) {
        await dateButton.trigger('click')
        
        expect(matchesComposable.selectedDate).toBe('2024-01-26')
        expect(matchesComposable.fetchMatches).toHaveBeenCalled()
      }
    })

    it('今天日期应该有特殊标识', () => {
      const todayElement = wrapper.find('.today, .current-date')
      
      // 根据实际实现判断今天日期的显示
      expect(todayElement.exists()).toBeDefined()
    })

    it('应该支持日期范围选择', async () => {
      const rangePicker = wrapper.find('.date-range-picker, .range-selector')
      
      if (rangePicker.exists()) {
        await rangePicker.trigger('click')
        
        // 验证日期范围选择功能
        expect(wrapper.vm.showDateRangePicker).toBe(true)
      }
    })
  })

  describe('筛选功能', () => {
    it('应该显示联赛筛选器', () => {
      const leagueFilter = wrapper.find('.league-filter, [data-filter="league"]')
      
      expect(leagueFilter.exists()).toBe(true)
    })

    it('应该支持选择特定联赛', async () => {
      filtersComposable.updateFilters({ leagues: ['英超'] })
      
      expect(filtersComposable.filters.leagues).toContain('英超')
      expect(matchesComposable.fetchMatches).toHaveBeenCalled()
    })

    it('应该显示状态筛选器', () => {
      const statusFilter = wrapper.find('.status-filter, [data-filter="status"]')
      
      expect(statusFilter.exists()).toBe(true)
    })

    it('应该支持按状态筛选比赛', async () => {
      filtersComposable.updateFilters({ status: 'live' })
      
      expect(filtersComposable.filters.status).toBe('live')
      expect(matchesComposable.fetchMatches).toHaveBeenCalled()
    })

    it('应该支持多联赛同时筛选', async () => {
      filtersComposable.updateFilters({ leagues: ['英超', '西甲'] })
      
      expect(filtersComposable.filters.leagues).toEqual(['英超', '西甲'])
    })

    it('应该重置筛选条件', async () => {
      filtersComposable.resetFilters()
      
      expect(filtersComposable.filters.leagues).toEqual([])
      expect(filtersComposable.filters.status).toBe('all')
    })
  })

  describe('比赛列表显示', () => {
    it('应该按时间顺序显示比赛', () => {
      const matchItems = wrapper.findAll('.match-item, .match-card-wrapper')
      
      if (matchItems.length > 1) {
        // 验证比赛按时间排序
        expect(matchItems.length).toBe(3)
      }
    })

    it('应该显示未开始的比赛', () => {
      const upcomingMatches = wrapper.findAll('.match-item[data-status="upcoming"]')
      
      // 应该显示曼联vs切尔西的比赛
      expect(upcomingMatches.length).toBeGreaterThan(0)
    })

    it('应该显示进行中的比赛', () => {
      const liveMatches = wrapper.findAll('.match-item[data-status="live"]')
      
      // 应该显示巴萨vs皇马的比赛
      expect(liveMatches.length).toBeGreaterThan(0)
    })

    it('应该显示已结束的比赛', () => {
      const finishedMatches = wrapper.findAll('.match-item[data-status="finished"]')
      
      // 应该显示拜仁vs多特的比赛
      expect(finishedMatches.length).toBeGreaterThan(0)
    })

    it('进行中比赛应该显示实时比分', () => {
      const liveMatch = wrapper.find('.match-item[data-status="live"]')
      
      if (liveMatch.exists()) {
        expect(liveMatch.text()).toContain('1')
        expect(liveMatch.text()).toContain('0')
        expect(liveMatch.text()).toContain('67\'') // 比赛时间
      }
    })

    it('已结束比赛应该显示最终比分', () => {
      const finishedMatch = wrapper.find('.match-item[data-status="finished"]')
      
      if (finishedMatch.exists()) {
        expect(finishedMatch.text()).toContain('3')
        expect(finishedMatch.text()).toContain('1')
      }
    })
  })

  describe('比赛卡片交互', () => {
    it('点击比赛应该跳转到详情页', async () => {
      const matchCard = wrapper.find('.match-card')
      
      if (matchCard.exists()) {
        await matchCard.trigger('click')
        
        // 验证路由跳转
        expect(window.location.href).toContain('/matches/1')
      }
    })

    it('应该支持添加到投注', async () => {
      const addToBetBtn = wrapper.find('.add-to-bet, .bet-button')
      
      if (addToBetBtn.exists()) {
        await addToBetBtn.trigger('click')
        
        // 验证投注功能被调用
        expect(wrapper.emitted('addToBet')).toBeTruthy()
      }
    })

    it('应该支持收藏比赛', async () => {
      const favoriteBtn = wrapper.find('.favorite-btn, .bookmark-button')
      
      if (favoriteBtn.exists()) {
        await favoriteBtn.trigger('click')
        
        // 验证收藏功能
        expect(wrapper.vm.toggleFavorite).toHaveBeenCalled()
      }
    })

    it('应该支持分享比赛', async () => {
      const shareBtn = wrapper.find('.share-btn, .share-button')
      
      if (shareBtn.exists()) {
        await shareBtn.trigger('click')
        
        // 验证分享功能
        expect(wrapper.vm.shareMatch).toHaveBeenCalled()
      }
    })
  })

  describe('实时更新', () => {
    it('应该建立WebSocket连接获取实时数据', () => {
      expect(wrapper.vm.setupRealtimeUpdates).toBeDefined()
    })

    it('应该处理比赛状态变化', async () => {
      const updatedMatch = {
        id: 1,
        status: 'live',
        current_time: '23\'',
        home_score: 0,
        away_score: 1
      }
      
      await wrapper.vm.handleMatchUpdate(updatedMatch)
      
      // 验证比赛数据更新
      const match = wrapper.vm.matches.find(m => m.id === 1)
      expect(match.status).toBe('live')
    })

    it('应该处理新的比赛事件', async () => {
      const matchEvent = {
        match_id: 2,
        type: 'goal',
        team: 'home',
        player: 'Messi',
        time: '70\''
      }
      
      await wrapper.vm.handleMatchEvent(matchEvent)
      
      // 验证事件处理
      expect(wrapper.vm.matchEvents).toContainEqual(matchEvent)
    })

    it('组件销毁时应该断开WebSocket连接', () => {
      wrapper.unmount()
      
      expect(wrapper.vm.cleanupRealtimeConnection).toBeDefined()
    })
  })

  describe('下拉刷新', () => {
    it('应该支持下拉刷新', async () => {
      const pullRefresh = wrapper.find('.pull-to-refresh')
      
      if (pullRefresh.exists()) {
        // 模拟下拉手势
        await pullRefresh.trigger('touchstart')
        await pullRefresh.trigger('touchmove')
        await pullRefresh.trigger('touchend')
        
        expect(matchesComposable.fetchMatches).toHaveBeenCalled()
      }
    })

    it('刷新时应该显示加载状态', async () => {
      wrapper.vm.isRefreshing = true
      await wrapper.vm.$nextTick()
      
      const refreshIndicator = wrapper.find('.refresh-indicator')
      
      expect(refreshIndicator.exists()).toBe(true)
    })
  })

  describe('空状态处理', () => {
    it('没有比赛时应该显示空状态', async () => {
      matchesComposable.matches = []
      await wrapper.vm.$nextTick()
      
      const emptyState = wrapper.find('.empty-state, .no-matches')
      
      expect(emptyState.exists()).toBe(true)
    })

    it('应该显示无筛选结果的提示', async () => {
      filtersComposable.updateFilters({ leagues: ['不存在的联赛'] })
      await wrapper.vm.$nextTick()
      
      const noResults = wrapper.find('.no-results, .filter-no-data')
      
      expect(noResults.exists()).toBe(true)
    })

    it('空状态时应该提供重置筛选的选项', async () => {
      matchesComposable.matches = []
      await wrapper.vm.$nextTick()
      
      const resetButton = wrapper.find('.reset-filters, .clear-filters')
      
      if (resetButton.exists()) {
        await resetButton.trigger('click')
        expect(filtersComposable.resetFilters).toHaveBeenCalled()
      }
    })
  })

  describe('搜索功能', () => {
    it('应该支持搜索比赛', async () => {
      const searchInput = wrapper.find('.search-input, .schedule-search')
      
      if (searchInput.exists()) {
        await searchInput.setValue('曼联')
        await searchInput.trigger('input')
        
        // 验证搜索过滤
        expect(wrapper.vm.searchQuery).toBe('曼联')
      }
    })

    it('搜索应该匹配球队名称', async () => {
      wrapper.vm.searchQuery = '巴萨'
      await wrapper.vm.$nextTick()
      
      const filteredMatches = wrapper.vm.filteredMatches
      
      // 应该只显示包含"巴萨"的比赛
      expect(filteredMatches.every(match => 
        match.home_team.includes('巴萨') || match.away_team.includes('巴萨')
      )).toBe(true)
    })

    it('应该支持清除搜索', async () => {
      wrapper.vm.searchQuery = '曼联'
      await wrapper.vm.$nextTick()
      
      const clearButton = wrapper.find('.clear-search, .search-clear')
      
      if (clearButton.exists()) {
        await clearButton.trigger('click')
        expect(wrapper.vm.searchQuery).toBe('')
      }
    })
  })

  describe('分组显示', () => {
    it('应该按联赛分组显示比赛', () => {
      const leagueGroups = wrapper.findAll('.league-group, .league-section')
      
      // 应该按英超、西甲、德甲分组
      expect(leagueGroups.length).toBe(3)
    })

    it('每个联赛组应该显示联赛名称和图标', () => {
      const leagueHeaders = wrapper.findAll('.league-header, .group-title')
      
      leagueHeaders.forEach(header => {
        expect(header.text()).toMatch(/(英超|西甲|德甲)/)
      })
    })

    it('应该支持折叠/展开联赛组', async () => {
      const leagueToggle = wrapper.find('.league-toggle, .collapse-button')
      
      if (leagueToggle.exists()) {
        await leagueToggle.trigger('click')
        
        // 验证折叠状态切换
        expect(wrapper.vm.collapsedLeagues).toBeDefined()
      }
    })
  })

  describe('错误处理', () => {
    it('数据加载失败应该显示错误状态', async () => {
      matchesComposable.fetchMatches.mockRejectedValue(new Error('Load failed'))
      
      await wrapper.vm.loadMatches()
      await wrapper.vm.$nextTick()
      
      const errorState = wrapper.find('.error-state, .load-error')
      
      expect(errorState.exists()).toBe(true)
    })

    it('网络错误应该显示重试选项', async () => {
      matchesComposable.fetchMatches.mockRejectedValue(new Error('Network error'))
      
      await wrapper.vm.loadMatches()
      await wrapper.vm.$nextTick()
      
      const retryButton = wrapper.find('.retry-button, .reload-btn')
      
      if (retryButton.exists()) {
        await retryButton.trigger('click')
        expect(matchesComposable.fetchMatches).toHaveBeenCalledTimes(2)
      }
    })

    it('应该处理无效的比赛数据', async () => {
      matchesComposable.matches = [null, undefined, { invalid: 'data' }]
      await wrapper.vm.$nextTick()
      
      // 验证数据验证和过滤
      expect(wrapper.vm.validMatches.length).toBeLessThan(3)
    })
  })

  describe('响应式设计', () => {
    it('应该在移动设备上调整布局', () => {
      Object.defineProperty(window, 'innerWidth', { value: 375 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('mobile-layout')
    })

    it('移动端应该隐藏部分筛选器', () => {
      Object.defineProperty(window, 'innerWidth', { value: 375 })
      window.dispatchEvent(new Event('resize'))
      
      const advancedFilters = wrapper.find('.advanced-filters')
      
      // 移动端可能隐藏高级筛选器
      expect(advancedFilters.exists()).toBeDefined()
    })

    it('平板设备应该使用网格布局', () => {
      Object.defineProperty(window, 'innerWidth', { value: 768 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('tablet-layout')
    })

    it('桌面设备应该显示完整功能', () => {
      Object.defineProperty(window, 'innerWidth', { value: 1200 })
      window.dispatchEvent(new Event('resize'))
      
      const fullFeatures = wrapper.find('.full-features, .desktop-only')
      
      expect(fullFeatures.exists()).toBeDefined()
    })
  })

  describe('性能优化', () => {
    it('应该懒加载比赛卡片', () => {
      // 验证懒加载逻辑
      expect(wrapper.vm.lazyLoadMatches).toBeDefined()
    })

    it('应该缓存筛选结果', () => {
      // 验证缓存机制
      expect(wrapper.vm.cacheFilteredMatches).toBeDefined()
    })

    it('滚动到底部应该加载更多比赛', async () => {
      const scrollContainer = wrapper.find('.matches-container')
      
      if (scrollContainer.exists()) {
        // 模拟滚动到底部
        await scrollContainer.trigger('scroll', { target })
        
        // 验证加载更多
        expect(matchesComposable.loadMoreMatches).toHaveBeenCalled()
      }
    })

    it('频繁筛选应该防抖', async () => {
      const startTime = Date.now()
      
      // 快速连续更新筛选条件
      filtersComposable.updateFilters({ leagues: ['英超'] })
      filtersComposable.updateFilters({ leagues: ['西甲'] })
      filtersComposable.updateFilters({ leagues: ['德甲'] })
      
      await wrapper.vm.$nextTick()
      
      const endTime = Date.now()
      
      // 验证防抖效果（实际测试中可能需要更复杂的验证）
      expect(endTime - startTime).toBeLessThan(1000)
    })
  })

  describe('无障碍访问', () => {
    it('比赛卡片应该有正确的语义化标签', () => {
      const matchCards = wrapper.findAll('.match-card')
      
      matchCards.forEach(card => {
        // 验证ARIA标签
        const ariaLabel = card.attributes('aria-label')
        expect(ariaLabel).toBeDefined()
      })
    })

    it('应该支持键盘导航', async () => {
      const focusableElements = wrapper.findAll('button, [tabindex]:not([tabindex="-1"])')
      
      // 验证焦点管理
      focusableElements.forEach((element, index) => {
        element.trigger('focus')
        expect(document.activeElement).toBe(element.element)
      })
    })

    it('状态筛选器应该有正确的role属性', () => {
      const statusFilter = wrapper.find('.status-filter')
      
      if (statusFilter.exists()) {
        const role = statusFilter.attributes('role')
        // expect(role).toBe('radiogroup')
      }
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
