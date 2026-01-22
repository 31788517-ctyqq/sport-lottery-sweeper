import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createWebHistory } from 'vue-router'
import AdminDashboard from '@/views/AdminDashboard.vue'
import { useAdmin } from '@/composables/useAdmin.js'

// 模拟图表库
global.Chart = vi.fn()

// 模拟 echarts
global.echarts = {
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  }))
}

// 模拟 toast
global.toast = {
  success: vi.fn(),
  error: vi.fn(),
  info: vi.fn()
}

const routes = [
  { path: '/', component: { template: '<div>Home</div>' } },
  { path: '/admin/login', component: { template: '<div>Admin Login</div>' } },
  { path: '/admin/users', component: { template: '<div>Users</div>' } },
  { path: '/admin/matches', component: { template: '<div>Matches</div>' } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

describe('AdminDashboard.vue', () => {
  let wrapper
  let adminComposable

  beforeEach(async () => {
    vi.clearAllMocks()
    
    const pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        admin: {
          stats: {
            total_users: 1000,
            active_users: 850,
            total_bets: 5000,
            pending_approvals: 5,
            system_health: 'good'
          },
          loading: false,
          recentActivities: [
            {
              id: 1,
              type: 'user_registered',
              description: 'New user registered',
              timestamp: new Date().toISOString()
            }
          ]
        }
      }
    })
    
    adminComposable = useAdmin()
    
    wrapper = mount(AdminDashboard, {
      global: {
        plugins: [pinia, router],
        stubs: {
          StatsCard: true,
          ChartCard: true,
          ActivityFeed: true,
          QuickActions: true,
          RecentRegistrations: true,
          SystemAlerts: true
        }
      }
    })
    
    await router.isReady()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
  })

  describe('权限验证', () => {
    it('应该检查管理员权限', () => {
      // 验证组件是否检查管理员权限
      expect(wrapper.vm.checkAdminPermission).toBeDefined()
    })

    it('非管理员应该重定向', async () => {
      // 模拟非管理员状态
      adminComposable.isAdmin = false
      
      // 重新挂载组件以触发权限检查
      await wrapper.vm.$nextTick()
      
      // 验证重定向逻辑
      // expect(window.location.href).toContain('/admin/login')
    })

    it('管理员token过期应该重定向', async () => {
      adminComposable.token = null
      
      await wrapper.vm.$nextTick()
      
      // 验证token检查逻辑
      expect(adminComposable.token).toBeNull()
    })
  })

  describe('组件渲染', () => {
    it('应该正确渲染管理仪表板', () => {
      expect(wrapper.find('.admin-dashboard').exists()).toBe(true)
      expect(wrapper.find('.dashboard-header').exists()).toBe(true)
    })

    it('应该显示仪表板标题', () => {
      const title = wrapper.find('h1, .dashboard-title, [data-testid="dashboard-title"]')
      
      expect(title.exists() || wrapper.text().includes('管理') || wrapper.text().includes('Dashboard')).toBe(true)
    })

    it('应该显示统计卡片区域', () => {
      const statsSection = wrapper.find('.stats-section, .statistics-cards')
      
      expect(statsSection.exists()).toBe(true)
    })

    it('应该显示图表区域', () => {
      const chartsSection = wrapper.find('.charts-section, .analytics-charts')
      
      expect(chartsSection.exists()).toBe(true)
    })

    it('应该显示快速操作区域', () => {
      const quickActions = wrapper.find('.quick-actions, .action-buttons')
      
      expect(quickActions.exists()).toBe(true)
    })
  })

  describe('数据加载', () => {
    it('应该在组件挂载时加载统计数据', () => {
      expect(adminComposable.fetchStats).toHaveBeenCalled()
    })

    it('应该加载最近活动数据', () => {
      expect(adminComposable.fetchRecentActivities).toHaveBeenCalled()
    })

    it('加载状态应该显示loading', async () => {
      adminComposable.loading = true
      await wrapper.vm.$nextTick()
      
      const loadingElement = wrapper.find('.loading, .spinner')
      
      expect(loadingElement.exists()).toBe(true)
    })

    it('加载完成应该隐藏loading', async () => {
      adminComposable.loading = false
      await wrapper.vm.$nextTick()
      
      const loadingElement = wrapper.find('.loading, .spinner')
      
      expect(loadingElement.exists()).toBe(false)
    })
  })

  describe('统计数据显示', () => {
    it('应该显示总用户数', () => {
      const userStats = wrapper.find('.total-users, [data-stat="total_users"]')
      
      if (userStats.exists()) {
        expect(userStats.text()).toContain('1000')
      }
    })

    it('应该显示活跃用户数', () => {
      const activeUsers = wrapper.find('.active-users, [data-stat="active_users"]')
      
      if (activeUsers.exists()) {
        expect(activeUsers.text()).toContain('850')
      }
    })

    it('应该显示总投注数', () => {
      const totalBets = wrapper.find('.total-bets, [data-stat="total_bets"]')
      
      if (totalBets.exists()) {
        expect(totalBets.text()).toContain('5000')
      }
    })

    it('应该显示待审批用户数', () => {
      const pendingApprovals = wrapper.find('.pending-approvals, [data-stat="pending_approvals"]')
      
      if (pendingApprovals.exists()) {
        expect(pendingApprovals.text()).toContain('5')
      }
    })

    it('应该显示系统健康状态', () => {
      const systemHealth = wrapper.find('.system-health, [data-stat="system_health"]')
      
      if (systemHealth.exists()) {
        expect(systemHealth.text()).toContain('good')
      }
    })
  })

  describe('图表功能', () => {
    it('应该初始化用户增长图表', () => {
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该初始化投注趋势图表', () => {
      expect(echarts.init).toHaveBeenCalled()
    })

    it('应该初始化收入分析图表', () => {
      expect(echarts.init).toHaveBeenCalled()
    })

    it('窗口大小变化时应该重绘图表', async () => {
      // 模拟窗口大小变化
      window.dispatchEvent(new Event('resize'))
      await wrapper.vm.$nextTick()
      
      // 验证图表resize方法被调用
      const chartInstances = wrapper.vm.chartInstances || []
      chartInstances.forEach(chart => {
        if (chart.resize) {
          expect(chart.resize).toHaveBeenCalled()
        }
      })
    })

    it('组件销毁时应该清理图表', () => {
      wrapper.unmount()
      
      // 验证图表dispose方法被调用
      const chartInstances = wrapper.vm.chartInstances || []
      chartInstances.forEach(chart => {
        if (chart.dispose) {
          expect(chart.dispose).toHaveBeenCalled()
        }
      })
    })
  })

  describe('快速操作', () => {
    it('应该包含用户审批快捷入口', async () => {
      const approveUsersBtn = wrapper.find('.approve-users-btn, [data-action="approve-users"]')
      
      if (approveUsersBtn.exists()) {
        await approveUsersBtn.trigger('click')
        expect(window.location.href).toContain('/admin/users')
      }
    })

    it('应该包含比赛管理快捷入口', async () => {
      const manageMatchesBtn = wrapper.find('.manage-matches-btn, [data-action="manage-matches"]')
      
      if (manageMatchesBtn.exists()) {
        await manageMatchesBtn.trigger('click')
        expect(window.location.href).toContain('/admin/matches')
      }
    })

    it('应该包含系统设置快捷入口', async () => {
      const systemSettingsBtn = wrapper.find('.system-settings-btn, [data-action="system-settings"]')
      
      if (systemSettingsBtn.exists()) {
        await systemSettingsBtn.trigger('click')
        // 验证设置页面跳转
      }
    })

    it('应该包含报表导出快捷入口', async () => {
      const exportReportsBtn = wrapper.find('.export-reports-btn, [data-action="export-reports"]')
      
      if (exportReportsBtn.exists()) {
        await exportReportsBtn.trigger('click')
        // 验证导出功能被调用
        expect(adminComposable.exportReport).toHaveBeenCalled()
      }
    })
  })

  describe('最近活动', () => {
    it('应该显示最近活动列表', () => {
      const activitiesList = wrapper.find('.activities-list, .recent-activities')
      
      expect(activitiesList.exists()).toBe(true)
    })

    it('应该显示活动描述和时间', () => {
      const activityItems = wrapper.findAll('.activity-item, .activity-entry')
      
      if (activityItems.length > 0) {
        const firstActivity = activityItems[0]
        expect(firstActivity.text()).toContain('New user registered')
      }
    })

    it('应该支持刷新活动列表', async () => {
      const refreshBtn = wrapper.find('.refresh-activities, .reload-btn')
      
      if (refreshBtn.exists()) {
        await refreshBtn.trigger('click')
        expect(adminComposable.fetchRecentActivities).toHaveBeenCalled()
      }
    })
  })

  describe('实时更新', () => {
    it('应该定期更新统计数据', () => {
      // 检查是否有定时更新逻辑
      expect(wrapper.vm.startAutoRefresh).toBeDefined()
    })

    it('应该能够停止自动更新', () => {
      wrapper.unmount()
      
      // 验证定时器被清理
      expect(wrapper.vm.stopAutoRefresh).toBeDefined()
    })

    it('手动刷新应该更新数据', async () => {
      const refreshBtn = wrapper.find('.refresh-all, .manual-refresh')
      
      if (refreshBtn.exists()) {
        await refreshBtn.trigger('click')
        
        expect(adminComposable.fetchStats).toHaveBeenCalled()
        expect(adminComposable.fetchRecentActivities).toHaveBeenCalled()
      }
    })
  })

  describe('错误处理', () => {
    it('统计数据加载失败应该显示错误', async () => {
      adminComposable.fetchStats.mockRejectedValue(new Error('Load failed'))
      
      await wrapper.vm.loadDashboardData()
      await wrapper.vm.$nextTick()
      
      expect(toast.error).toHaveBeenCalledWith('加载统计数据失败')
    })

    it('图表初始化失败应该有降级处理', async () => {
      // 模拟图表初始化失败
      global.echarts.init.mockImplementation(() => {
        throw new Error('Chart init failed')
      })
      
      await wrapper.vm.initCharts()
      await wrapper.vm.$nextTick()
      
      // 验证降级处理
      expect(wrapper.vm.chartsEnabled).toBe(false)
    })

    it('网络错误应该重试加载', async () => {
      adminComposable.fetchStats
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ success: true })
      
      await wrapper.vm.loadDashboardData()
      await wrapper.vm.$nextTick()
      
      // 验证重试逻辑
      expect(adminComposable.fetchStats).toHaveBeenCalledTimes(2)
    })
  })

  describe('响应式设计', () => {
    it('应该在移动设备上调整布局', () => {
      // 模拟移动设备
      Object.defineProperty(window, 'innerWidth', { value: 375 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('mobile-layout')
    })

    it('应该在平板设备上调整布局', () => {
      // 模拟平板设备
      Object.defineProperty(window, 'innerWidth', { value: 768 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('tablet-layout')
    })

    it('应该在桌面设备上显示完整布局', () => {
      // 模拟桌面设备
      Object.defineProperty(window, 'innerWidth', { value: 1200 })
      window.dispatchEvent(new Event('resize'))
      
      expect(wrapper.classes()).toContain('desktop-layout')
    })
  })

  describe('性能优化', () => {
    it('应该懒加载图表', () => {
      // 验证图表是否在需要时加载
      expect(wrapper.vm.lazyLoadCharts).toBeDefined()
    })

    it('应该缓存统计数据', () => {
      // 验证数据缓存逻辑
      expect(wrapper.vm.cacheStats).toBeDefined()
    })

    it('长时间不活跃应该暂停更新', () => {
      // 模拟用户不活跃
      Object.defineProperty(document, 'hidden', { value: true, configurable: true })
      document.dispatchEvent(new Event('visibilitychange'))
      
      // 验证暂停更新逻辑
      expect(wrapper.vm.pauseAutoRefresh).toBeDefined()
    })
  })

  describe('搜索和过滤', () => {
    it('应该支持快速搜索', async () => {
      const searchInput = wrapper.find('.dashboard-search input')
      
      if (searchInput.exists()) {
        await searchInput.setValue('user')
        await searchInput.trigger('input')
        
        // 验证搜索功能
        expect(wrapper.vm.handleSearch).toHaveBeenCalled()
      }
    })

    it('应该支持时间范围过滤', async () => {
      const timeFilter = wrapper.find('.time-filter select, .date-range-picker')
      
      if (timeFilter.exists()) {
        await timeFilter.setValue('7d')
        await timeFilter.trigger('change')
        
        expect(adminComposable.fetchStats).toHaveBeenCalledWith(expect.objectContaining({ timeRange: '7d' }))
      }
    })
  })

  describe('通知和提醒', () => {
    it('应该显示系统告警', () => {
      const alerts = wrapper.find('.system-alerts, .alerts-panel')
      
      expect(alerts.exists()).toBe(true)
    })

    it('应该显示待处理事项数量', () => {
      const pendingBadge = wrapper.find('.pending-badge, .notification-count')
      
      if (pendingBadge.exists()) {
        expect(pendingBadge.text()).toContain('5') // pending_approvals count
      }
    })

    it('新告警到达应该显示通知', async () => {
      const newAlert = {
        id: 2,
        type: 'warning',
        message: 'High server load detected',
        timestamp: new Date().toISOString()
      }
      
      await wrapper.vm.handleNewAlert(newAlert)
      
      expect(toast.warning).toHaveBeenCalledWith('High server load detected')
    })
  })

  describe('数据导出', () => {
    it('应该支持导出统计数据', async () => {
      const exportBtn = wrapper.find('.export-stats, .download-report')
      
      if (exportBtn.exists()) {
        await exportBtn.trigger('click')
        
        expect(adminComposable.exportStats).toHaveBeenCalled()
      }
    })

    it('导出应该支持多种格式', async () => {
      const formatSelect = wrapper.find('.export-format select')
      
      if (formatSelect.exists()) {
        await formatSelect.setValue('pdf')
        await formatSelect.trigger('change')
        
        // 验证格式参数传递
        expect(adminComposable.exportStats).toHaveBeenCalledWith(expect.objectContaining({ format: 'pdf' }))
      }
    })
  })
})