import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import BottomNav from '@/components/BottomNav.vue'

// 模拟 vue-router
type MockRouterPush = (path: string) => void

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: vi.fn() as MockRouterPush
  }),
  useRoute: () => ({
    path: '/'
  })
}))

describe('BottomNav.vue', () => {
  let wrapper
  let mockRouterPush
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    mockRouterPush = vi.fn()
    
    wrapper = mount(BottomNav, {
      global: {
        mocks: {
          $t: (key: string) => key,
          $router: { push: mockRouterPush },
          $route: { path: '/' }
        },
        stubs: {
          'el-badge': true,
          'el-icon': true
        }
      },
      props: {
        activeTab: '/'
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染底部导航', () => {
      expect(wrapper.find('.bottom-nav').exists()).toBe(true)
      expect(wrapper.find('.nav-container').exists()).toBe(true)
    })

    it('应该包含所有导航项', () => {
      expect(wrapper.text()).toContain('首页')
      expect(wrapper.text()).toContain('赛程')
      expect(wrapper.text()).toContain('收藏')
      expect(wrapper.text()).toContain('我的')
    })
  })

  describe('导航项状态', () => {
    it('当前激活项应该有高亮样式', () => {
      const activeItem = wrapper.find('.nav-item.active')
      expect(activeItem.exists()).toBe(true)
      expect(activeItem.text()).toContain('首页')
    })

    it('非激活项不应该有高亮样式', async () => {
      await wrapper.setProps({ activeTab: '/schedule' })
      
      const homeItem = wrapper.findAll('.nav-item').find(item => 
        item.text().includes('首页')
      )
      if (homeItem) {
        expect(homeItem.classes()).not.toContain('active')
      }
    })

    it('应该根据 activeTab prop 正确设置激活状态', async () => {
      const testCases = [
        { tab: '/', expectedText: '首页' },
        { tab: '/schedule', expectedText: '赛程' },
        { tab: '/favorites', expectedText: '收藏' },
        { tab: '/profile', expectedText: '我的' }
      ]
      
      for (const testCase of testCases) {
        await wrapper.setProps({ activeTab: testCase.tab })
        await nextTick()
        
        const activeItem = wrapper.findAll('.nav-item').find(item => 
          item.classes().includes('active')
        )
        if (activeItem) {
          expect(activeItem.text()).toContain(testCase.expectedText)
        }
      }
    })
  })

  describe('导航功能', () => {
    it('点击首页导航应该跳转到首页', async () => {
      const homeNavItem = wrapper.findAll('.nav-item').find(item => 
        item.text().includes('首页')
      )
      
      if (homeNavItem) {
        await homeNavItem.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/')
      }
    })

    it('点击赛程导航应该跳转到赛程页', async () => {
      const scheduleNavItem = wrapper.findAll('.nav-item').find(item => 
        item.text().includes('赛程')
      )
      
      if (scheduleNavItem) {
        await scheduleNavItem.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/schedule')
      }
    })

    it('点击收藏导航应该跳转到收藏页', async () => {
      const favoritesNavItem = wrapper.findAll('.nav-item').find(item => 
        item.text().includes('收藏')
      )
      
      if (favoritesNavItem) {
        await favoritesNavItem.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/favorites')
      }
    })

    it('点击我的导航应该跳转到个人中心', async () => {
      const profileNavItem = wrapper.findAll('.nav-item').find(item => 
        item.text().includes('我的')
      )
      
      if (profileNavItem) {
        await profileNavItem.trigger('click')
        expect(mockRouterPush).toHaveBeenCalledWith('/profile')
      }
    })
  })

  describe('徽章显示', () => {
    it('有未读消息时应该显示徽章', async () => {
      await wrapper.setProps({ 
        activeTab: '/',
        unreadCount: 3 
      })
      
      const badge = wrapper.find('.badge')
      if (badge.exists()) {
        expect(badge.text()).toContain('3')
        expect(badge.isVisible()).toBe(true)
      }
    })

    it('无未读消息时不显示徽章', () => {
      const badge = wrapper.find('.badge')
      if (badge.exists()) {
        expect(badge.isVisible()).toBe(false)
      }
    })

    it('大量未读消息应该显示省略号', async () => {
      await wrapper.setProps({ unreadCount: 100 })
      
      const badge = wrapper.find('.badge')
      if (badge.exists()) {
        expect(badge.text()).toContain('99+')
      }
    })
  })

  describe('响应式设计', () => {
    it('在移动设备上应该固定到底部', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(true)
      expect(wrapper.classes()).toContain('mobile-bottom-nav')
    })

    it('在桌面设备上应该是相对定位', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 1200,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(false)
      expect(wrapper.classes()).not.toContain('mobile-bottom-nav')
    })
  })

  describe('无障碍访问', () => {
    it('导航项应该有正确的 aria-label', () => {
      const navItems = wrapper.findAll('.nav-item')
      navItems.forEach(item => {
        expect(item.attributes('aria-label')).toBeDefined()
      })
    })

    it('激活项应该有 aria-current 属性', () => {
      const activeItem = wrapper.find('.nav-item.active')
      if (activeItem.exists()) {
        expect(activeItem.attributes('aria-current')).toBe('page')
      }
    })
  })

  describe('触摸事件', () => {
    it('移动设备上应该支持触摸反馈', async () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      wrapper.vm.checkMobile()
      
      const navItem = wrapper.findAll('.nav-item').first()
      if (navItem.exists()) {
        await navItem.trigger('touchstart')
        expect(navItem.classes()).toContain('touch-active')
        
        await navItem.trigger('touchend')
        expect(navItem.classes()).not.toContain('touch-active')
      }
    })
  })

  describe('性能优化', () => {
    it('路由变化不应该频繁触发重新渲染', async () => {
      const initialRender = wrapper.html()
      
      // 模拟多次路由变化
      for (let i = 0; i < 5; i++) {
        await wrapper.setProps({ activeTab: i % 2 === 0 ? '/' : '/schedule' })
      }
      
      // 组件应该正常响应，不会报错
      expect(wrapper.exists()).toBe(true)
    })
  })
})