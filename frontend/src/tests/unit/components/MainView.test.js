import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MainView from '@/components/MainView.vue'

// 模拟子组件
vi.mock('@/components/HeaderComponent.vue', () => ({
  default: { template: '<div class="header-component"><slot /></div>' }
}))

vi.mock('@/components/BottomNav.vue', () => ({
  default: { template: '<div class="bottom-nav"><slot /></div>' }
}))

vi.mock('@/components/MainContent.jsx', () => ({
  default: { template: '<div class="main-content">Main Content</div>' }
}))

describe('MainView.vue', () => {
  let wrapper
  
  beforeEach(() => {
    vi.clearAllMocks()
    
    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn()
      },
      writable: true
    })
    
    wrapper = mount(MainView, {
      global: {
        mocks: {
          $t: (key) => key,
          $route: { path: '/' },
          $router: { push: vi.fn() }
        },
        stubs: {
          'router-view': true,
          'keep-alive': true
        }
      }
    })
  })

  afterEach(() => {
    wrapper.unmount()
  })

  describe('组件渲染', () => {
    it('应该正确渲染主视图结构', () => {
      expect(wrapper.find('.main-view').exists()).toBe(true)
      expect(wrapper.find('.header-container').exists()).toBe(true)
      expect(wrapper.find('.content-container').exists()).toBe(true)
      expect(wrapper.find('.bottom-nav-container').exists()).toBe(true)
    })

    it('应该包含 HeaderComponent', () => {
      expect(wrapper.find('.header-component').exists()).toBe(true)
    })

    it('应该包含 BottomNav', () => {
      expect(wrapper.find('.bottom-nav').exists()).toBe(true)
    })

    it('应该包含 MainContent', () => {
      expect(wrapper.find('.main-content').exists()).toBe(true)
    })
  })

  describe('布局切换', () => {
    it('应该支持网格布局', async () => {
      wrapper.vm.layoutMode = 'grid'
      await nextTick()
      
      expect(wrapper.vm.currentLayoutClass).toContain('grid')
      expect(wrapper.find('.main-content').classes()).toContain('grid-layout')
    })

    it('应该支持列表布局', async () => {
      wrapper.vm.layoutMode = 'list'
      await nextTick()
      
      expect(wrapper.vm.currentLayoutClass).toContain('list')
      expect(wrapper.find('.main-content').classes()).toContain('list-layout')
    })

    it('应该支持紧凑布局', async () => {
      wrapper.vm.layoutMode = 'compact'
      await nextTick()
      
      expect(wrapper.vm.currentLayoutClass).toContain('compact')
      expect(wrapper.find('.main-content').classes()).toContain('compact-layout')
    })
  })

  describe('主题切换', () => {
    it('应该支持浅色主题', async () => {
      wrapper.vm.theme = 'light'
      await nextTick()
      
      expect(wrapper.vm.isDarkTheme).toBe(false)
      expect(document.body.classList.contains('dark-theme')).toBe(false)
    })

    it('应该支持深色主题', async () => {
      wrapper.vm.theme = 'dark'
      await nextTick()
      
      expect(wrapper.vm.isDarkTheme).toBe(true)
      expect(document.body.classList.contains('dark-theme')).toBe(true)
    })
  })

  describe('侧边栏功能', () => {
    it('应该能够打开侧边栏', async () => {
      wrapper.vm.toggleSidebar(true)
      await nextTick()
      
      expect(wrapper.vm.showSidebar).toBe(true)
      expect(wrapper.find('.sidebar-overlay').exists()).toBe(true)
    })

    it('应该能够关闭侧边栏', async () => {
      wrapper.vm.showSidebar = true
      wrapper.vm.closeSidebar()
      await nextTick()
      
      expect(wrapper.vm.showSidebar).toBe(false)
    })

    it('点击遮罩层应该关闭侧边栏', async () => {
      wrapper.vm.showSidebar = true
      
      const overlay = wrapper.find('.sidebar-overlay')
      if (overlay.exists()) {
        await overlay.trigger('click')
        expect(wrapper.vm.showSidebar).toBe(false)
      }
    })
  })

  describe('响应式设计', () => {
    it('应该检测移动设备', () => {
      // Mock window.innerWidth
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(true)
    })

    it('应该检测桌面设备', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 1200,
        writable: true
      })
      
      wrapper.vm.checkMobile()
      expect(wrapper.vm.isMobile).toBe(false)
    })
  })

  describe('数据持久化', () => {
    it('应该保存布局偏好到 localStorage', async () => {
      wrapper.vm.layoutMode = 'grid'
      wrapper.vm.saveLayoutPreference()
      
      expect(localStorage.setItem).toHaveBeenCalledWith('layout-mode', 'grid')
    })

    it('应该从 localStorage 加载布局偏好', async () => {
      localStorage.getItem.mockReturnValue('list')
      
      wrapper.vm.loadLayoutPreference()
      await nextTick()
      
      expect(wrapper.vm.layoutMode).toBe('list')
    })

    it('布局偏好不存在时使用默认值', async () => {
      localStorage.getItem.mockReturnValue(null)
      
      wrapper.vm.loadLayoutPreference()
      await nextTick()
      
      expect(wrapper.vm.layoutMode).toBe('grid') // 默认值
    })
  })

  describe('生命周期', () => {
    it('应该在挂载时加载用户偏好', () => {
      expect(localStorage.getItem).toHaveBeenCalledWith('layout-mode')
      expect(localStorage.getItem).toHaveBeenCalledWith('theme')
    })

    it('应该在窗口大小改变时更新移动检测', async () => {
      const resizeHandler = vi.fn()
      window.addEventListener = vi.fn((event, handler) => {
        if (event === 'resize') resizeHandler.mockImplementation(handler)
      })
      
      wrapper = mount(MainView)
      
      // 触发 resize 事件
      resizeHandler()
      
      expect(resizeHandler).toHaveBeenCalled()
    })
  })

  describe('事件处理', () => {
    it('应该处理布局切换事件', async () => {
      wrapper.vm.changeLayout('compact')
      await nextTick()
      
      expect(wrapper.vm.layoutMode).toBe('compact')
      expect(localStorage.setItem).toHaveBeenCalledWith('layout-mode', 'compact')
    })

    it('应该处理主题切换事件', async () => {
      wrapper.vm.toggleTheme()
      await nextTick()
      
      expect(wrapper.vm.theme).toBe('dark')
      expect(localStorage.setItem).toHaveBeenCalledWith('theme', 'dark')
    })
  })
})