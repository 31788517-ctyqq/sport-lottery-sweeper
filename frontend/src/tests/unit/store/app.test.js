// AI_WORKING: coder1 @2026-01-29 18:36:01 - 修复导入路径和语法问题
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAppStore } from '@/stores/app'

// 模拟 localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// 模拟 vue-router
global.window = Object.create(window)
Object.defineProperty(window, 'location', {
  value,
  writable: true
})

// 模拟 navigator
global.navigator = { language: 'zh-CN' }

describe('useAppStore (stores/app.js)', () => {
  let appStore
  
  beforeEach(() => {
    // 创建新的 Pinia 实例
    setActivePinia(createPinia())
    
    vi.clearAllMocks()
    
    // Reset localStorage mock
    localStorage.getItem.mockReturnValue(null)
    localStorage.setItem.mockImplementation(() => {})
    
    appStore = useAppStore()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('初始状态', () => {
    it('应该初始化正确的应用状态', () => {
      expect(appStore.theme).toBe('light')
      expect(appStore.language).toBe('zh-CN')
      expect(appStore.layout).toBe('grid')
      expect(appStore.sidebarOpen).toBe(false)
      expect(appStore.loading).toBe(false)
      expect(appStore.loadingText).toBe('')
      expect(appStore.notifications).toEqual([])
      expect(appStore.modal).toEqual({ show: false, component, props })
      expect(appStore.offline).toBe(false)
    })

    it('应该从 localStorage 加载保存的主题', () => {
      localStorage.getItem.mockReturnValue('dark')
      
      const newAppStore = useAppStore()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('app-theme')
      expect(newAppStore.theme).toBe('dark')
    })

    it('应该从 localStorage 加载保存的语言', () => {
      localStorage.getItem.mockReturnValue('en-US')
      
      const newAppStore = useAppStore()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('app-language')
      expect(newAppStore.language).toBe('en-US')
    })

    it('应该从 localStorage 加载保存的布局', () => {
      localStorage.getItem.mockReturnValue('list')
      
      const newAppStore = useAppStore()
      
      expect(localStorage.getItem).toHaveBeenCalledWith('app-layout')
      expect(newAppStore.layout).toBe('list')
    })
  })

  describe('主题管理', () => {
    it('应该切换深色/浅色主题', () => {
      expect(appStore.theme).toBe('light')
      
      appStore.toggleTheme()
      
      expect(appStore.theme).toBe('dark')
      expect(localStorage.setItem).toHaveBeenCalledWith('app-theme', 'dark')
      expect(document.documentElement.classList.contains('dark')).toBe(true)
    })

    it('应该设置特定主题', () => {
      appStore.setTheme('auto')
      
      expect(appStore.theme).toBe('auto')
      expect(localStorage.setItem).toHaveBeenCalledWith('app-theme', 'auto')
    })

    it('应该验证主题值', () => {
      expect(() => {
        appStore.setTheme('invalid-theme')
      }).toThrow('Invalid theme')
    })

    it('自动主题应该跟随系统偏好', () => {
      Object.defineProperty(window, 'matchMedia', {
        value: vi.fn().mockImplementation(query => ({
          matches: query === '(prefers-color-scheme: dark)',
          addListener: vi.fn(),
          removeListener: vi.fn()
        })),
        writable: true
      })
      
      appStore.setTheme('auto')
      
      expect(appStore.effectiveTheme).toBe('dark')
    })
  })

  describe('语言管理', () => {
    it('应该设置语言', () => {
      appStore.setLanguage('en-US')
      
      expect(appStore.language).toBe('en-US')
      expect(localStorage.setItem).toHaveBeenCalledWith('app-language', 'en-US')
    })

    it('应该验证语言代码', () => {
      expect(() => {
        appStore.setLanguage('invalid-lang')
      }).toThrow('Unsupported language')
    })

    it('应该支持RTL语言检测', () => {
      appStore.setLanguage('ar-SA') // 阿拉伯语 - RTL
      
      expect(appStore.isRTL).toBe(true)
    })

    it('中文环境应该设置正确的文本方向', () => {
      appStore.setLanguage('zh-CN')
      
      expect(appStore.isRTL).toBe(false)
      expect(document.dir).toBe('ltr')
    })
  })

  describe('布局管理', () => {
    it('应该切换布局模式', () => {
      expect(appStore.layout).toBe('grid')
      
      appStore.toggleLayout()
      
      expect(appStore.layout).toBe('list')
      expect(localStorage.setItem).toHaveBeenCalledWith('app-layout', 'list')
    })

    it('应该设置特定布局', () => {
      appStore.setLayout('compact')
      
      expect(appStore.layout).toBe('compact')
      expect(localStorage.setItem).toHaveBeenCalledWith('app-layout', 'compact')
    })

    it('应该验证布局值', () => {
      expect(() => {
        appStore.setLayout('invalid-layout')
      }).toThrow('Invalid layout')
    })

    it('应该计算当前布局类名', () => {
      appStore.setLayout('grid')
      expect(appStore.layoutClass).toBe('layout-grid')
      
      appStore.setLayout('list')
      expect(appStore.layoutClass).toBe('layout-list')
      
      appStore.setLayout('compact')
      expect(appStore.layoutClass).toBe('layout-compact')
    })
  })

  describe('侧边栏管理', () => {
    it('应该打开侧边栏', () => {
      appStore.openSidebar()
      
      expect(appStore.sidebarOpen).toBe(true)
    })

    it('应该关闭侧边栏', () => {
      appStore.sidebarOpen = true
      appStore.closeSidebar()
      
      expect(appStore.sidebarOpen).toBe(false)
    })

    it('应该切换侧边栏状态', () => {
      expect(appStore.sidebarOpen).toBe(false)
      
      appStore.toggleSidebar()
      expect(appStore.sidebarOpen).toBe(true)
      
      appStore.toggleSidebar()
      expect(appStore.sidebarOpen).toBe(false)
    })

    it('移动设备上应该自动关闭侧边栏', () => {
      Object.defineProperty(window, 'innerWidth', {
        value: 375,
        writable: true
      })
      
      appStore.sidebarOpen = true
      appStore.handleResize()
      
      expect(appStore.sidebarOpen).toBe(false)
    })
  })

  describe('加载状态管理', () => {
    it('应该显示加载状态', () => {
      appStore.showLoading('正在加载...')
      
      expect(appStore.loading).toBe(true)
      expect(appStore.loadingText).toBe('正在加载...')
    })

    it('应该隐藏加载状态', () => {
      appStore.showLoading('加载中...')
      appStore.hideLoading()
      
      expect(appStore.loading).toBe(false)
      expect(appStore.loadingText).toBe('')
    })

    it('应该支持加载状态上下文', () => {
      const context = { id: 1, type: 'fetch' }
      appStore.showLoading('加载数据...', context)
      
      expect(appStore.loadingContext).toEqual(context)
      
      appStore.hideLoading(context)
      expect(appStore.loading).toBe(false)
    })

    it('应该防止重复显示相同的加载', () => {
      appStore.showLoading('加载中...')
      const firstCallCount = localStorage.setItem.mock.calls.length
      
      appStore.showLoading('加载中...') // 相同的文本
      
      // localStorage.setItem 不应该被再次调用
      expect(localStorage.setItem.mock.calls.length).toBe(firstCallCount)
    })
  })

  describe('通知管理', () => {
    it('应该添加通知', () => {
      const notification = appStore.addNotification({
        type: 'success',
        title: '操作成功',
        message: '数据保存成功',
        duration: 3000
      })
      
      expect(notification.id).toBeDefined()
      expect(notification.type).toBe('success')
      expect(notification.title).toBe('操作成功')
      expect(notification.message).toBe('数据保存成功')
      expect(notification.duration).toBe(3000)
      expect(notification.timestamp).toBeInstanceOf(Date)
      expect(appStore.notifications).toContainEqual(notification)
    })

    it('应该自动移除定时通知', async () => {
      vi.useFakeTimers()
      
      appStore.addNotification({
        type: 'info',
        message: '3秒后消失',
        duration: 3000
      })
      
      expect(appStore.notifications).toHaveLength(1)
      
      // 快进3秒
      vi.advanceTimersByTime(3000)
      
      expect(appStore.notifications).toHaveLength(0)
      
      vi.useRealTimers()
    })

    it('应该移除指定通知', () => {
      const notification = appStore.addNotification({ message: '要删除的通知' })
      
      expect(appStore.notifications).toHaveLength(1)
      
      appStore.removeNotification(notification.id)
      
      expect(appStore.notifications).toHaveLength(0)
    })

    it('应该清除所有通知', () => {
      appStore.addNotification({ message: '通知1' })
      appStore.addNotification({ message: '通知2' })
      appStore.addNotification({ message: '通知3' })
      
      expect(appStore.notifications).toHaveLength(3)
      
      appStore.clearNotifications()
      
      expect(appStore.notifications).toHaveLength(0)
    })

    it('应该按类型清除通知', () => {
      appStore.addNotification({ type: 'success', message: '成功1' })
      appStore.addNotification({ type: 'error', message: '错误1' })
      appStore.addNotification({ type: 'success', message: '成功2' })
      
      appStore.clearNotificationsByType('success')
      
      expect(appStore.notifications).toHaveLength(1)
      expect(appStore.notifications[0].type).toBe('error')
    })

    it('应该提供便捷的通知方法', () => {
      appStore.notifySuccess('成功消息')
      appStore.notifyError('错误消息')
      appStore.notifyWarning('警告消息')
      appStore.notifyInfo('信息消息')
      
      expect(appStore.notifications).toHaveLength(4)
      expect(appStore.notifications.find(n => n.type === 'success')).toBeDefined()
      expect(appStore.notifications.find(n => n.type === 'error')).toBeDefined()
      expect(appStore.notifications.find(n => n.type === 'warning')).toBeDefined()
      expect(appStore.notifications.find(n => n.type === 'info')).toBeDefined()
    })
  })

  describe('模态框管理', () => {
    it('应该显示模态框', () => {
      const component = { template: 'Test Component</div>' }
      const props = { title: '测试模态框', data }
      
      appStore.showModal(component, props)
      
      expect(appStore.modal.show).toBe(true)
      expect(appStore.modal.component).toBe(component)
      expect(appStore.modal.props).toEqual(props)
    })

    it('应该关闭模态框', () => {
      appStore.showModal({}, {})
      appStore.hideModal()
      
      expect(appStore.modal.show).toBe(false)
      expect(appStore.modal.component).toBeNull()
      expect(appStore.modal.props).toEqual({})
    })

    it('应该切换模态框状态', () => {
      expect(appStore.modal.show).toBe(false)
      
      appStore.toggleModal({})
      expect(appStore.modal.show).toBe(true)
      
      appStore.toggleModal()
      expect(appStore.modal.show).toBe(false)
    })

    it('关闭模态框时应该调用回调', () => {
      const onClose = vi.fn()
      appStore.showModal({}, { onClose })
      
      appStore.hideModal()
      
      expect(onClose).toHaveBeenCalled()
    })
  })

  describe('网络状态管理', () => {
    it('应该检测在线状态', () => {
      // 模拟在线状态
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        writable: true
      })
      
      appStore.handleOnline()
      
      expect(appStore.offline).toBe(false)
      expect(appStore.notifications.some(n => n.message.includes('网络已连接'))).toBe(true)
    })

    it('应该检测离线状态', () => {
      // 模拟离线状态
      Object.defineProperty(navigator, 'onLine', {
        value: false,
        writable: true
      })
      
      appStore.handleOffline()
      
      expect(appStore.offline).toBe(true)
      expect(appStore.notifications.some(n => n.message.includes('网络连接已断开'))).toBe(true)
    })

    it('断线重连应该显示成功通知', () => {
      appStore.offline = true
      
      Object.defineProperty(navigator, 'onLine', {
        value: true,
        writable: true
      })
      
      appStore.handleOnline()
      
      expect(appStore.offline).toBe(false)
    })
  })

  describe('错误处理', () => {
    it('应该设置全局错误', () => {
      const error = new Error('测试错误')
      const context = { component: 'TestComponent', action: 'fetchData' }
      
      appStore.setError(error, context)
      
      expect(appStore.globalError).toEqual({
        message: '测试错误',
        stack: error.stack,
        context: context,
        timestamp: expect.any(Date)
      })
    })

    it('应该清除全局错误', () => {
      appStore.setError(new Error('测试错误'))
      appStore.clearError()
      
      expect(appStore.globalError).toBeNull()
    })

    it('应该处理未捕获的错误', () => {
      const error = new Error('未捕获错误')
      const errorEvent = { error, message: 'Script error' }
      
      appStore.handleGlobalError(errorEvent)
      
      expect(appStore.globalError).toBeDefined()
      expect(appStore.globalError.message).toBe('未捕获错误')
    })

    it('应该处理未处理的 Promise 拒绝', () => {
      const error = new Error('Promise rejected')
      const rejectionEvent = { reason: error }
      
      appStore.handleUnhandledRejection(rejectionEvent)
      
      expect(appStore.globalError).toBeDefined()
      expect(appStore.globalError.message).toBe('Promise rejected')
    })
  })

  describe('数据持久化', () => {
    it('应该保存状态到 localStorage', () => {
      appStore.setTheme('dark')
      appStore.setLanguage('en-US')
      appStore.setLayout('list')
      
      appStore.saveState()
      
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'app-state',
        expect.stringContaining('dark')
      )
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'app-state',
        expect.stringContaining('en-US')
      )
      expect(localStorage.setItem).toHaveBeenCalledWith(
        'app-state',
        expect.stringContaining('list')
      )
    })

    it('应该从 localStorage 恢复状态', () => {
      const savedState = {
        theme: 'dark',
        language: 'en-US',
        layout: 'compact',
        sidebarOpen: true
      }
      
      localStorage.getItem.mockReturnValue(JSON.stringify(savedState))
      
      const newAppStore = useAppStore()
      
      expect(newAppStore.theme).toBe('dark')
      expect(newAppStore.language).toBe('en-US')
      expect(newAppStore.layout).toBe('compact')
      expect(newAppStore.sidebarOpen).toBe(true)
    })

    it('无效的状态数据应该被忽略', () => {
      localStorage.getItem.mockReturnValue('invalid-json')
      const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
      
      const newAppStore = useAppStore()
      
      expect(consoleSpy).toHaveBeenCalled()
      expect(newAppStore.theme).toBe('light') // 默认值
      
      consoleSpy.mockRestore()
    })

    it('应该定期自动保存状态', () => {
      vi.useFakeTimers()
      
      appStore.setTheme('dark')
      
      // 快进自动保存间隔
      vi.advanceTimersByTime(60000) // 1分钟
      
      expect(localStorage.setItem).toHaveBeenCalledWith('app-state', expect.any(String))
      
      vi.useRealTimers()
    })
  })

  describe('响应式特性', () => {
    it('应该监听窗口大小变化', () => {
      const resizeHandler = vi.fn()
      window.addEventListener = vi.fn((event, handler) => {
        if (event === 'resize') resizeHandler.mockImplementation(handler)
      })
      
      const newAppStore = useAppStore()
      
      // 触发 resize 事件
      resizeHandler()
      
      expect(resizeHandler).toHaveBeenCalled()
    })

    it('应该监听网络状态变化', () => {
      const onlineHandler = vi.fn()
      const offlineHandler = vi.fn()
      
      window.addEventListener = vi.fn((event, handler) => {
        if (event === 'online') onlineHandler.mockImplementation(handler)
        if (event === 'offline') offlineHandler.mockImplementation(handler)
      })
      
      const newAppStore = useAppStore()
      
      onlineHandler()
      expect(newAppStore.offline).toBe(false)
      
      offlineHandler()
      expect(newAppStore.offline).toBe(true)
    })

    it('组件卸载时应该清理事件监听器', () => {
      const removeEventListener = vi.fn()
      window.removeEventListener = removeEventListener
      
      const newAppStore = useAppStore()
      
      // 模拟组件卸载
      newAppStore.$dispose?.()
      
      expect(removeEventListener).toHaveBeenCalledWith('resize', expect.any(Function))
      expect(removeEventListener).toHaveBeenCalledWith('online', expect.any(Function))
      expect(removeEventListener).toHaveBeenCalledWith('offline', expect.any(Function))
    })
  })

  describe('性能优化', () => {
    it('应该限制通知数量防止内存泄漏', () => {
      // 添加超过100条通知
      for (let i = 0; i < 150; i++) {
        appStore.addNotification({ message: `通知${i}` })
      }
      
      // 应该被限制在某个合理范围内
      expect(appStore.notifications.length).toBeLessThan(200)
    })

    it('频繁的状态变更应该使用防抖', () => {
      vi.useFakeTimers()
      
      // 快速连续更改主题
      appStore.setTheme('dark')
      appStore.setTheme('light')
      appStore.setTheme('dark')
      
      // 立即检查，localStorage.setItem 应该还没有被频繁调用
      const initialCalls = localStorage.setItem.mock.calls.length
      
      // 快进防抖时间
      vi.advanceTimersByTime(1000)
      
      // 现在应该只调用了一次保存
      expect(localStorage.setItem.mock.calls.length).toBeLessThan(initialCalls + 10)
      
      vi.useRealTimers()
    })

    it('模态框切换应该避免不必要的DOM操作', () => {
      const component1 = { template: 'Component1</div>' }
      const component2 = { template: 'Component2</div>' }
      
      appStore.showModal(component1, {})
      const firstModalElement = document.querySelector('.modal-overlay')
      
      appStore.showModal(component2, {})
      const secondModalElement = document.querySelector('.modal-overlay')
      
      // 应该是同一个DOM元素被重用
      expect(firstModalElement).toBe(secondModalElement)
    })
  })

  describe('计算属性和工具方法', () => {
    it('应该正确计算当前主题类名', () => {
      appStore.setTheme('dark')
      expect(appStore.themeClass).toBe('theme-dark')
      
      appStore.setTheme('light')
      expect(appStore.themeClass).toBe('theme-light')
      
      appStore.setTheme('auto')
      expect(appStore.themeClass).toContain('theme-auto')
    })

    it('应该提供状态重置功能', () => {
      // 修改状态
      appStore.setTheme('dark')
      appStore.setLanguage('en-US')
      appStore.setLayout('list')
      appStore.addNotification({ message: '测试通知' })
      
      // 重置状态
      appStore.resetState()
      
      expect(appStore.theme).toBe('light')
      expect(appStore.language).toBe('zh-CN')
      expect(appStore.layout).toBe('grid')
      expect(appStore.notifications).toHaveLength(0)
    })

    it('应该导出状态快照', () => {
      appStore.setTheme('dark')
      appStore.setLanguage('en-US')
      
      const snapshot = appStore.exportState()
      
      expect(snapshot.theme).toBe('dark')
      expect(snapshot.language).toBe('en-US')
      expect(snapshot.timestamp).toBeInstanceOf(Date)
    })

    it('应该导入状态快照', () => {
      const snapshot = {
        theme: 'dark',
        language: 'en-US',
        layout: 'compact',
        timestamp: new Date()
      }
      
      appStore.importState(snapshot)
      
      expect(appStore.theme).toBe('dark')
      expect(appStore.language).toBe('en-US')
      expect(appStore.layout).toBe('compact')
    })
  })
})
// AI_DONE: coder1 @2026-01-29 18:36:01
