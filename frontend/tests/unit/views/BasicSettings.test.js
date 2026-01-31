import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { ElMessage } from 'element-plus'
import BasicSettings from '@/views/admin/settings/settings-components/BasicSettings.vue'

// Mock Element Plus Message
vi.mock('element-plus', () => ({
  ElMessage: {
    success: vi.fn(),
    error: vi.fn(),
    warning: vi.fn(),
    info: vi.fn()
  }
}))

// Mock auth store
vi.mock('@/stores/auth', () => ({
  useAuthStore: vi.fn(() => ({
    userInfo: {
      roles: ['admin']
    }
  }))
}))

describe('BasicSettings.vue', () => {
  let wrapper
  let pinia
  
  beforeEach(() => {
    // 重置所有mocks
    vi.clearAllMocks()
    
    // 创建新的pinia实例
    pinia = createTestingPinia({
      createSpy: vi.fn,
      initialState: {
        auth: {
          user: {
            roles: ['admin']
          }
        }
      }
    })
  })
  
  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })
  
  const createWrapper = (props = {}, options = {}) => {
    return mount(BasicSettings, {
      props,
      global: {
        plugins: [pinia],
        stubs: {
          'el-card': true,
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': true,
          'el-upload': true,
          'el-icon': true,
          'el-switch': true,
          'el-input-number': true,
          'el-tree': true,
          'el-dialog': true
        }
      },
      ...options
    })
  }
  
  describe('组件渲染', () => {
    it('应该正确渲染基础设置页面', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.find('.basic-settings').exists()).toBe(true)
      expect(wrapper.find('.settings-form').exists()).toBe(true)
    })
    
    it('应该显示系统基本信息卡片', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.text()).toContain('系统基本信息')
      expect(wrapper.text()).toContain('系统名称')
      expect(wrapper.text()).toContain('系统描述')
      expect(wrapper.text()).toContain('系统Logo')
    })
    
    it('应该显示系统配置卡片', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.text()).toContain('系统配置')
      expect(wrapper.text()).toContain('系统维护模式')
      expect(wrapper.text()).toContain('数据保留天数')
      expect(wrapper.text()).toContain('会话超时时间(分钟)')
    })
    
    it('应该显示保存和重置按钮', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.find('.form-actions').exists()).toBe(true)
      expect(wrapper.text()).toContain('保存设置')
      expect(wrapper.text()).toContain('重置')
    })

    it('应该显示菜单管理卡片', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.text()).toContain('菜单管理')
    })
  })
  
  describe('菜单管理功能', () => {
    it('应该初始化菜单数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(wrapper.vm.menuList).toBeDefined()
      expect(Array.isArray(wrapper.vm.menuList)).toBe(true)
      expect(wrapper.vm.menuList.length).toBeGreaterThan(0)
    })

    it('应该包含菜单管理方法', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      expect(typeof wrapper.vm.handleDragEnd).toBe('function')
      expect(typeof wrapper.vm.addMenu).toBe('function')
      expect(typeof wrapper.vm.editMenu).toBe('function')
      expect(typeof wrapper.vm.deleteMenu).toBe('function')
    })
  })

  describe('表单功能', () => {
    it('保存设置按钮应该显示成功消息', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      // 查找保存设置按钮
      const saveButton = wrapper.find('.form-actions').findAll('el-button-stub')[0]
      expect(saveButton.exists()).toBe(true)
      
      // 模拟点击
      await saveButton.trigger('click')
      
      // 验证消息显示
      expect(ElMessage.success).toHaveBeenCalledWith('基础设置保存成功')
    })
    
    it('重置按钮应该重置表单数据', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      // 修改表单数据
      wrapper.vm.form.systemName = '修改后的名称'
      wrapper.vm.form.systemDescription = '修改后的描述'
      
      // 查找重置按钮
      const resetButton = wrapper.find('.form-actions').findAll('el-button-stub')[1]
      expect(resetButton.exists()).toBe(true)
      
      // 模拟点击重置
      await resetButton.trigger('click')
      
      // 验证表单数据被重置为默认值
      expect(wrapper.vm.form.systemName).toBe('竞彩足球扫盘系统')
      expect(wrapper.vm.form.systemDescription).toContain('专业的足球数据采集')
    })
    
    it('表单验证规则应该有效', async () => {
      wrapper = createWrapper()
      await flushPromises()
      
      // 验证规则对象存在
      expect(wrapper.vm.rules.systemName).toBeDefined()
      expect(wrapper.vm.rules.systemDescription).toBeDefined()
      expect(wrapper.vm.rules.dataRetentionDays).toBeDefined()
      expect(wrapper.vm.rules.sessionTimeout).toBeDefined()
    })
  })
})