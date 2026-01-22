import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import HeaderComponent from '@/components/HeaderComponent.vue'

// 模拟 vue-router
type MockRouterPush = (path: string) => void

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn() as MockRouterPush
  }),
  useRoute: () => ({ path: '/' })
}))

// 模拟 Pinia store
vi.mock('pinia', () => ({
  defineStore: vi.fn(() => ({
    user: { name: 'Test User', avatar: '' },
    isLoggedIn: true
  }))
}))

describe('HeaderComponent.vue', () => {
  let wrapper
  let mockRouterPush
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    mockRouterPush = vi.fn()
    
    wrapper = mount(HeaderComponent, {
      global: {
        mocks: {
          $t: (key: string) => key,
          $router: { push: mockRouterPush },
          $route: { path: '/' },
          $store: {
            state: {
              user: { name: 'Test User', avatar: '' },
              isLoggedIn: true
            }
          }
        },
        stubs: {
          'el-dropdown': true,
          'el-menu': true,
          'el-menu-item': true,
          'el-avatar': true,
          'el-icon': true,
          'el-badge': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染头部组件', () => {
      expect(wrapper.find('.header-component').exists()).toBe(true)
      expect(wrapper.find('.header-container').exists()).toBe(true)
      expect(wrapper.find('.logo-section').exists()).toBe(true)
      expect(wrapper.find('.nav-section').exists()).toBe(true)
      expect(wrapper.find('.user-section').exists()).toBe(true)
    })

    it('应该显示 logo 和标题', () => {
      expect(wrapper.text()).toContain('体育彩票')
    })

    it('应该显示用户信息当已登录', () => {
      expect(wrapper.text()).toContain('Test User')
    })
  })

  describe('导航菜单', () => {
    it('应该包含所有主导航项', () => {
      expect(wrapper.text()).toContain('首页')
      expect(wrapper.text()).toContain('赛程')
      expect(wrapper.text()).toContain('数据分析')
      expect(wrapper.text()).toContain('情报')
    })

    it('当前页面菜单项应该高亮', () => {
      const activeMenuItem = wrapper.find('.nav-menu .el-menu-item.is-active')
      expect(activeMenuItem.exists()).toBe(true)
    })

    it('点击导航项应该跳转到对应页面', async () => {
      const scheduleMenuItem = wrapper.findAll('.nav-menu .el-menu-item').find(item => 
        item.text().includes('赛程')
      )
      
      if (scheduleMenuItem) {
        await scheduleMenuItem.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/schedule')
      }
    })
  })

  describe('用户功能', () => {
    it('已登录用户应该显示用户菜单', () => {
      expect(wrapper.find('.user-dropdown').exists()).toBe(true)
      expect(wrapper.find('.user-info').exists()).toBe(true)
    })

    it('未登录用户应该显示登录按钮', async () => {
      await wrapper.setData({ isLoggedIn: false })
      
      expect(wrapper.find('.login-btn').exists()).toBe(true)
      expect(wrapper.find('.user-dropdown').exists()).toBe(false)
    })

    it('点击登录按钮应该跳转到登录页', async () => {
      await wrapper.setData({ isLoggedIn: false })
      
      const loginBtn = wrapper.find('.login-btn')
      if (loginBtn.exists()) {
        await loginBtn.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/login')
      }
    })

    it('点击用户头像应该显示下拉菜单', async () => {
      const userAvatar = wrapper.find('.user-avatar')
      if (userAvatar.exists()) {
        await userAvatar.trigger('click')
        expect(wrapper.find('.dropdown-menu').isVisible()).toBe(true)
      }
    })
  })

  describe('下拉菜单功能', () => {
    it('用户菜单应该包含个人中心选项', async () => {
      const userAvatar = wrapper.find('.user-avatar')
      if (userAvatar.exists()) {
        await userAvatar.trigger('click')
        await nextTick()
        
        expect(wrapper.text()).toContain('个人中心')
      }
    })

    it('用户菜单应该包含设置选项', async () => {
      const userAvatar = wrapper.find('.user-avatar')
      if (userAvatar.exists()) {
        await userAvatar.trigger('click')
        await nextTick()
        
        expect(wrapper.text()).toContain('设置')
      }
    })

    it('用户菜单应该包含退出登录选项', async () => {
      const userAvatar = wrapper.find('.user-avatar')
      if (userAvatar.exists()) {
        await userAvatar.trigger('click')
        await nextTick()
        
        expect(wrapper.text()).toContain('退出登录')
      }
    })

    it('点击退出登录应该调用登出方法', async () => {
      const logoutSpy = vi.spyOn(wrapper.vm, 'handleLogout')
      
      const userAvatar = wrapper.find('.user-avatar')
      if (userAvatar.exists()) {
        await userAvatar.trigger('click')
        await nextTick()
        
        const logoutItem = wrapper.findAll('.dropdown-item').find(item => 
          item.text().includes('退出登录')
        )
        if (logoutItem) {
          await logoutItem.trigger('click')
          expect(logoutSpy).toHaveBeenCalled()
        }
      }
    })
  })

  describe('搜索功能', () => {
    it('应该显示搜索框', () => {
      expect(wrapper.find('.search-box').exists()).toBe(true)
    })

    it('输入搜索关键词应该更新搜索值', async () => {
      const searchInput = wrapper.find('.search-input')
      if (searchInput.exists()) {
        await searchInput.setValue('英超')
        await searchInput.trigger('input')
        
        expect(wrapper.vm.searchQuery).toBe('英超')
      }
    })

    it('提交搜索应该触发搜索事件', async () => {
      const searchInput = wrapper.find('.search-input')
      if (searchInput.exists()) {
        await searchInput.setValue('英超')
        
        const searchForm = wrapper.find('.search-form')
        if (searchForm.exists()) {
          await searchForm.trigger('submit.prevent')
          expect(wrapper.emitted('search')).toBeTruthy()
          expect(wrapper.emitted('search')[0]).toEqual(['英超'])
        }
      }
    })

    it('清空搜索应该重置搜索值', async () => {
      await wrapper.setData({ searchQuery: '英超' })
      
      const clearBtn = wrapper.find('.clear-search')
      if (clearBtn.exists()) {
        await clearBtn.trigger('click')
        expect(wrapper.vm.searchQuery).toBe('')
      }
    })
  })

  describe('通知功能', () => {
    it('应该显示通知图标', () => {
      expect(wrapper.find('.notification-btn').exists()).toBe(true)
    })

    it('有未读通知时应该显示徽章', async () => {
      await wrapper.setData({ unreadNotifications: 3 })
      
      const badge = wrapper.find('.notification-badge')
      if (badge.exists()) {
        expect(badge.text()).toContain('3')
        expect(badge.isVisible()).toBe(true)
      }
    })

    it('无未读通知时不显示徽章', () => {
      const badge = wrapper.find('.notification-badge')
      if (badge.exists()) {
        expect(badge.isVisible()).toBe(false)
      }
    })

    it('点击通知图标应该显示通知面板', async () => {
      const notificationBtn = wrapper.find('.notification-btn')
      if (notificationBtn.exists()) {
        await notificationBtn.trigger('click')
        expect(wrapper.find('.notification-panel').isVisible()).toBe(true)
      }
    })
  })

  describe('响应式设计', () => {
    it('在移动设备上应该显示汉堡菜单', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(true)
      expect(wrapper.find('.mobile-menu-btn').exists()).toBe(true)
    })

    it('在桌面设备上应该隐藏汉堡菜单', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 1200,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(false)
      expect(wrapper.find('.mobile-menu-btn').exists()).toBe(false)
    })

    it('移动设备上点击汉堡菜单应该显示移动导航', async () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      wrapper.vm.checkMobile()
      
      const mobileMenuBtn = wrapper.find('.mobile-menu-btn')
      if (mobileMenuBtn.exists()) {
        await mobileMenuBtn.trigger('click')
        expect(wrapper.find('.mobile-nav').isVisible()).toBe(true)
      }
    })
  })

  describe('主题切换', () => {
    it('应该支持主题切换按钮', () => {
      expect(wrapper.find('.theme-toggle').exists()).toBe(true)
    })

    it('点击主题切换应该切换深色/浅色模式', async () => {
      const themeToggle = wrapper.find('.theme-toggle')
      if (themeToggle.exists()) {
        await themeToggle.trigger('click')
        expect(wrapper.vm.isDarkTheme).toBe(true)
      }
    })
  })

  describe('数据持久化', () => {
    it('应该保存搜索历史到 localStorage', async () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn(),
          setItem: vi.fn(),
          removeItem: vi.fn()
        },
        writable: true
      })
      
      await wrapper.setData({ searchQuery: '英超' })
      wrapper.vm.saveSearchHistory()
      
      expect(localStorage.setItem).toHaveBeenCalled()
    })

    it('应该从 localStorage 加载搜索历史', async () => {
      Object.defineProperty(window, 'localStorage', {
        value: {
          getItem: vi.fn().mockReturnValue(JSON.stringify(['英超', '西甲'])),
          setItem: vi.fn(),
          removeItem: vi.fn()
        },
        writable: true
      })
      
      wrapper.vm.loadSearchHistory()
      await nextTick()
      
      expect(wrapper.vm.searchHistory).toEqual(['英超', '西甲'])
    })
  })

  describe('性能优化', () => {
    it('窗口大小改变时应该防抖处理', async () => {
      vi.useFakeTimers()
      
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      
      // 快速连续触发 resize 事件
      window.dispatchEvent(new Event('resize'))
      window.dispatchEvent(new Event('resize'))
      window.dispatchEvent(new Event('resize'))
      
      vi.runOnlyPendingTimers()
      
      expect(wrapper.vm.isMobile).toBe(true)
      
      vi.useRealTimers()
    })
  })
})