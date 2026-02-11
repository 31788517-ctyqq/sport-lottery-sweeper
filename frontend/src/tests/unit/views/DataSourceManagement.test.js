import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import DataSourceManagement from '../../../../views/admin/crawler/DataSourceManagement.vue'

// 模拟全局 fetch
global.fetch = vi.fn()

// 模拟 Element Plus 消息组件
global.ElMessage = {
  success: vi.fn(),
  error: vi.fn(),
  warning: vi.fn()
}

global.ElMessageBox = {
  confirm: vi.fn().mockImplementation(() => Promise.resolve()),
  alert: vi.fn().mockImplementation(() => Promise.resolve())
}

describe('DataSourceManagement.vue', () => {
  let wrapper

  const mockDataSourceList = {
    success: true,
    data: {
      items: [
        {
          id: 1,
          source_id: 'DS001',
          name: '测试数据源1',
          type: 'api',
          config: { category: 'match_data' },
          url: 'https://api.example.com/data',
          status: 'online',
          error_rate: 0.05,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T01:00:00Z'
        }
      ],
      total: 1
    }
  }

  beforeEach(async () => {
    vi.clearAllMocks()
    // 模拟 fetch 返回数据源列表
    global.fetch.mockResolvedValue({
      json: vi.fn().mockResolvedValue(mockDataSourceList)
    })

    wrapper = mount(DataSourceManagement, {
      global: {
        mocks: {},
        stubs: {
          'el-row': true,
          'el-col': true,
          'el-card': true,
          'el-button': true,
          'el-select': true,
          'el-option': true,
          'el-input': true,
          'el-table': true,
          'el-table-column': true,
          'el-tag': true,
          'el-pagination': true,
          'el-dialog': true,
          'el-form': true,
          'el-form-item': true,
          'el-switch': true,
          'el-tabs': true,
          'el-tab-pane': true,
          'el-input-number': true
        }
      }
    })

    // 等待组件挂载和初始数据加载
    await wrapper.vm.$nextTick()
  })

  afterEach(() => {
    wrapper.unmount()
    vi.restoreAllMocks()
  })

  describe('组件渲染', () => {
    it('应该正确渲染数据源管理页面', () => {
      expect(wrapper.text()).toContain('数据源管理')
    })

    it('应该显示统计卡片', () => {
      expect(wrapper.text()).toContain('总数据源')
      expect(wrapper.text()).toContain('在线源')
      expect(wrapper.text()).toContain('离线源')
      expect(wrapper.text()).toContain('错误率')
    })
  })

  describe('数据加载', () => {
    it('应该在挂载时加载数据源列表', () => {
      expect(global.fetch).toHaveBeenCalled()
    })
  })

  describe('分类映射函数', () => {
    it('应该正确映射比赛数据分类', () => {
      const row = { type: '100qiu', config: { source_type: '100qiu' } }
      const category = wrapper.vm.getCategory(row)
      expect(category).toBe('比赛数据')
    })
  })
})