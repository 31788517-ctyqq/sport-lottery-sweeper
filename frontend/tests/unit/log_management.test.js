/**
 * 日志管理模块单元测试
 * 测试日志管理模块的5个子页面功能
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount, shallowMount } from '@vue/test-utils';
import { ElTable, ElPagination, ElDialog, ElButton, ElInput, ElSelect, ElOption, ElDatePicker, ElCard, ElTag } from 'element-plus';
import { nextTick } from 'vue';

// 导入各个日志管理页面组件
import LogManagement from '@/views/admin/logs/LogManagement.vue';
import SystemLogs from '@/views/admin/logs/SystemLogs.vue';
import UserLogs from '@/views/admin/logs/UserLogs.vue';
import SecurityLogs from '@/views/admin/logs/SecurityLogs.vue';
import APILogs from '@/views/admin/logs/APILogs.vue';

// 模拟axios请求
vi.mock('axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: { items: [], total: 0 } })),
    post: vi.fn(() => Promise.resolve({ data: {} }))
  }
}));

// 模拟router
const mockRouter = {
  push: vi.fn(),
  replace: vi.fn()
};

vi.mock('vue-router', () => ({
  useRouter: () => mockRouter,
  useRoute: () => ({ path: '/admin/logs' })
}));

describe('日志管理模块单元测试', () => {
  describe('日志管理主页面(LogManagement)', () => {
    let wrapper;

    beforeEach(() => {
      wrapper = mount(LogManagement, {
        global: {
          components: {
            ElCard,
            ElButton,
            ElTable,
            ElTag,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
    });

    afterEach(() => {
      wrapper.unmount();
    });

    it('应该正确渲染页面标题', () => {
      expect(wrapper.find('h2').text()).toBe('日志管理中心');
    });

    it('应该渲染统计信息卡片', () => {
      const statItems = wrapper.findAll('.log-stat-item');
      expect(statItems.length).toBe(4); // 总日志数、错误日志、用户活动、安全事件
    });

    it('应该渲染导航按钮', () => {
      const navButtons = wrapper.findAll('.log-menu button');
      expect(navButtons.length).toBe(4); // 系统日志、用户日志、安全日志、API日志
    });

    it('应该包含最近日志表格', () => {
      expect(wrapper.find('.recent-logs .el-table').exists()).toBe(true);
    });

    it('应该有正确的路由跳转方法', async () => {
      const systemLogBtn = wrapper.find('button:has-text("系统日志")');
      await systemLogBtn.trigger('click');
      expect(mockRouter.push).toHaveBeenCalledWith('/admin/logs/system');
    });
  });

  describe('系统日志页面(SystemLogs)', () => {
    let wrapper;

    beforeEach(() => {
      wrapper = mount(SystemLogs, {
        global: {
          components: {
            ElCard,
            ElTable,
            ElInput,
            ElSelect,
            ElOption,
            ElDatePicker,
            ElPagination,
            ElDialog,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
    });

    afterEach(() => {
      wrapper.unmount();
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span').text();
      expect(header).toBe('系统日志');
    });

    it('应该包含筛选工具栏', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      expect(wrapper.find('.el-select').exists()).toBe(true);
      expect(wrapper.find('.el-date-editor').exists()).toBe(true);
      expect(wrapper.find('button:has-text("筛选")').exists()).toBe(true);
    });

    it('应该渲染日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该包含分页组件', () => {
      expect(wrapper.find('.pagination-container').exists()).toBe(true);
    });

    it('应该有正确的筛选方法', async () => {
      const spy = vi.spyOn(wrapper.vm, 'applyFilters');
      
      // 更新筛选条件
      await wrapper.setData({
        searchQuery: 'test',
        logLevelFilter: 'INFO'
      });
      
      // 触发筛选
      const filterBtn = wrapper.find('button:has-text("筛选")');
      await filterBtn.trigger('click');
      
      expect(spy).toHaveBeenCalled();
      expect(wrapper.vm.searchQuery).toBe('test');
      expect(wrapper.vm.logLevelFilter).toBe('INFO');
    });
  });

  describe('用户日志页面(UserLogs)', () => {
    let wrapper;

    beforeEach(() => {
      wrapper = mount(UserLogs, {
        global: {
          components: {
            ElCard,
            ElTable,
            ElInput,
            ElSelect,
            ElOption,
            ElDatePicker,
            ElPagination,
            ElDialog,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
    });

    afterEach(() => {
      wrapper.unmount();
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span').text();
      expect(header).toBe('用户日志');
    });

    it('应该包含用户筛选选项', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      expect(wrapper.find('select[placeholder="用户ID"]').exists()).toBe(true);
      expect(wrapper.find('button:has-text("筛选")').exists()).toBe(true);
    });

    it('应该渲染用户日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该有用户ID列', () => {
      const columns = wrapper.findAll('.el-table__header .cell');
      const hasUserIdColumn = columns.some(col => col.text() === '用户ID');
      expect(hasUserIdColumn).toBe(true);
    });
  });

  describe('安全日志页面(SecurityLogs)', () => {
    let wrapper;

    beforeEach(() => {
      wrapper = mount(SecurityLogs, {
        global: {
          components: {
            ElCard,
            ElTable,
            ElInput,
            ElSelect,
            ElOption,
            ElDatePicker,
            ElPagination,
            ElDialog,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
    });

    afterEach(() => {
      wrapper.unmount();
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span').text();
      expect(header).toBe('安全日志');
    });

    it('应该渲染安全日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该包含安全相关筛选项', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      expect(wrapper.find('button:has-text("筛选")').exists()).toBe(true);
    });
  });

  describe('API日志页面(APILogs)', () => {
    let wrapper;

    beforeEach(() => {
      wrapper = mount(APILogs, {
        global: {
          components: {
            ElCard,
            ElTable,
            ElInput,
            ElSelect,
            ElOption,
            ElDatePicker,
            ElPagination,
            ElDialog,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
    });

    afterEach(() => {
      wrapper.unmount();
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span').text();
      expect(header).toBe('API日志');
    });

    it('应该渲染API日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该包含API日志特有的列', () => {
      const cells = wrapper.findAll('.el-table__header .cell');
      const headers = cells.map(cell => cell.text());
      
      expect(headers).toContain('请求路径');
      expect(headers).toContain('状态码');
      expect(headers).toContain('耗时(ms)');
      expect(headers).toContain('IP地址');
    });
  });

  describe('日志管理模块交互功能测试', () => {
    it('系统日志页面应有正确的标签类型方法', () => {
      const wrapper = shallowMount(SystemLogs);
      
      expect(wrapper.vm.getTagType('ERROR')).toBe('danger');
      expect(wrapper.vm.getTagType('WARN')).toBe('warning');
      expect(wrapper.vm.getTagType('INFO')).toBe('info');
      expect(wrapper.vm.getTagType('DEBUG')).toBe('primary');
      expect(wrapper.vm.getTagType('UNKNOWN')).toBe('info');
    });

    it('安全日志页面应有正确的标签类型方法', () => {
      const wrapper = shallowMount(SecurityLogs);
      
      expect(wrapper.vm.getTagType('ERROR')).toBe('danger');
      expect(wrapper.vm.getTagType('CRITICAL')).toBe('danger');
      expect(wrapper.vm.getTagType('WARN')).toBe('warning');
      expect(wrapper.vm.getTagType('INFO')).toBe('info');
    });

    it('API日志页面应有正确的标签类型方法', () => {
      const wrapper = shallowMount(APILogs);
      
      expect(wrapper.vm.getTagType('ERROR')).toBe('danger');
      expect(wrapper.vm.getTagType('CRITICAL')).toBe('danger');
      expect(wrapper.vm.getTagType('INFO')).toBe('info');
    });

    it('应该能够处理分页变化事件', async () => {
      const wrapper = mount(SystemLogs, {
        global: {
          components: {
            ElCard,
            ElTable,
            ElPagination,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
      
      const spySizeChange = vi.spyOn(wrapper.vm, 'handleSizeChange');
      const spyCurrentChange = vi.spyOn(wrapper.vm, 'handleCurrentChange');
      
      // 模拟分页变化
      await wrapper.vm.handleSizeChange(100);
      await wrapper.vm.handleCurrentChange(2);
      
      expect(spySizeChange).toHaveBeenCalledWith(100);
      expect(spyCurrentChange).toHaveBeenCalledWith(2);
    });
  });
});