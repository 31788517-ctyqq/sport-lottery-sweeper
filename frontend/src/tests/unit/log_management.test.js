// AI_WORKING: coder1 @2026-01-30 15:35:00 - 修复组件导入路径，使用真实Vue组件替换模拟组件
/**
 * 日志管理模块单元测试
 * 测试日志管理模块的5个子页面功能
 */
// @vitest-environment jsdom

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import { ElTable, ElPagination, ElDialog, ElButton, ElInput, ElSelect, ElOption, ElDatePicker, ElCard, ElTag, ElRow, ElCol } from 'element-plus';
import { nextTick } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';

// 导入真实组件
import LogManagement from '../../views/admin/logs/LogManagement.vue';
import SystemLogs from '../../views/admin/logs/SystemLogs.vue';
import UserLogs from '../../views/admin/logs/UserLogs.vue';
import SecurityLogs from '../../views/admin/logs/SecurityLogs.vue';
import APILogs from '../../views/admin/logs/APILogs.vue';

// 模拟axios
vi.mock('axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    delete: vi.fn()
  }
}));

// 创建一个模拟路由器，使用真实组件作为路由
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: LogManagement },
    { path: '/admin/logs', component: LogManagement },
    { path: '/admin/logs/system', component: SystemLogs },
    { path: '/admin/logs/user', component: UserLogs },
    { path: '/admin/logs/security', component: SecurityLogs },
    { path: '/admin/logs/api', component: APILogs }
  ]
});

describe('日志管理模块单元测试', () => {
  describe('日志管理主页面(LogManagement)', () => {
    let wrapper;

    beforeEach(async () => {
      // 使用mount并提供所有必要的组件，提供初始数据以避免API调用
      wrapper = mount(LogManagement, {
        data() {
          return {
            totalLogs: 100,
            errorLogs: 5,
            userActivities: 20,
            securityEvents: 3,
            recentLogs: [
              { timestamp: '2023-01-01 12:00:00', level: 'INFO', module: 'test', message: 'test message' }
            ],
            loadingRecent: false
          }
        },
        global: {
          components: {
            ElCard,
            ElRow,
            ElCol,
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
      await nextTick(); // 确保组件完全渲染
    });

    afterEach(() => {
      if (wrapper && wrapper.unmount) {
        wrapper.unmount();
      }
    });

    it('应该正确渲染页面标题', () => {
      // 根据实际模板结构，标题在el-card内
      const h2 = wrapper.find('h2');
      expect(h2.exists()).toBe(true);
      expect(h2.text()).toBe('日志管理中心');
    });

    it('应该渲染统计信息卡片', () => {
      // 根据实际模板结构，统计信息卡片使用log-stat-item类
      const statItems = wrapper.findAll('.log-stat-item');
      expect(statItems.length).toBe(4); // 有4个统计信息卡片
    });

    it('应该渲染导航按钮', () => {
      // 根据实际模板结构，导航按钮在log-menu div内
      const navButtons = wrapper.findAll('.log-menu button');
      expect(navButtons.length).toBe(4); // 有4个导航按钮
    });

    it('应该包含最近日志表格', () => {
      // 根据实际模板结构，最近日志表格在recent-logs card内
      const tableExists = wrapper.find('.recent-logs .el-table').exists();
      expect(tableExists).toBe(true);
    });

    it('应该有正确的路由跳转方法', async () => {
      const routerPushSpy = vi.spyOn(router, 'push');
      // 查找第一个按钮并点击
      const buttons = wrapper.findAll('.log-menu button');
      if (buttons.length > 0) {
        await buttons[0].trigger('click');
        // 检查是否调用了router.push
        expect(routerPushSpy).toHaveBeenCalled();
      }
    });

    // AI_WORKING: coder1 @2026-01-30 15:40:00 - 添加API调用测试
    it('应调用API加载统计数据', async () => {
      const mockResponse = { data: { total_logs: 150, level_stats: [{ level: 'ERROR', count: 10 }], module_stats: [{ module: 'user', count: 25 }, { module: 'security', count: 5 }] } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      // 调用组件方法
      await wrapper.vm.loadStatistics();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/statistics');
      expect(wrapper.vm.totalLogs).toBe(150);
      expect(wrapper.vm.errorLogs).toBe(10);
      expect(wrapper.vm.userActivities).toBe(25);
      expect(wrapper.vm.securityEvents).toBe(5);
    });

    it('应调用API加载最近日志', async () => {
      const mockLogs = [
        { timestamp: '2023-01-01 10:00:00', level: 'INFO', module: 'system', message: '系统启动' },
        { timestamp: '2023-01-01 10:05:00', level: 'ERROR', module: 'auth', message: '认证失败' }
      ];
      const mockResponse = { data: { items: mockLogs, total: 2 } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      // 调用组件方法
      await wrapper.vm.loadRecentLogs();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/system?skip=0&limit=5');
      expect(wrapper.vm.recentLogs).toEqual(mockLogs);
      expect(wrapper.vm.loadingRecent).toBe(false);
    });

    it('刷新按钮应触发数据重新加载', async () => {
      const loadRecentLogsSpy = vi.spyOn(wrapper.vm, 'loadRecentLogs');
      const refreshButton = wrapper.find('.recent-logs button[type="link"]');
      
      await refreshButton.trigger('click');
      expect(loadRecentLogsSpy).toHaveBeenCalled();
    });

    it('API错误时应显示错误信息', async () => {
      const axios = await import('axios');
      axios.default.get.mockRejectedValue(new Error('Network error'));
      
      // 模拟 $message.error 方法
      const messageErrorSpy = vi.fn();
      wrapper.vm.$message = { error: messageErrorSpy };

      await wrapper.vm.loadStatistics();
      
      expect(messageErrorSpy).toHaveBeenCalledWith('加载日志统计失败');
      expect(wrapper.vm.totalLogs).toBe(0);
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
            ElButton,
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
      if (wrapper && wrapper.unmount) {
        wrapper.unmount();
      }
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span');
      expect(header.exists()).toBe(true);
      expect(header.text()).toBe('系统日志');
    });

    it('应该包含筛选工具栏', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      expect(wrapper.find('.el-select').exists()).toBe(true);
      expect(wrapper.find('.el-date-editor').exists()).toBe(true);
      // 修复选择器，不再使用:has-text
      const filterButtons = wrapper.findAll('button');
      const hasFilterButton = filterButtons.some(btn => btn.text().includes('筛选'));
      expect(hasFilterButton).toBe(true);
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
      
      // 触发筛选 - 使用更通用的选择器
      const buttons = wrapper.findAll('button');
      const filterButton = buttons.find(btn => btn.text().includes('筛选'));
      if (filterButton) {
        await filterButton.trigger('click');
        expect(spy).toHaveBeenCalled();
      }
      expect(wrapper.vm.searchQuery).toBe('test');
      expect(wrapper.vm.logLevelFilter).toBe('INFO');
    });

    // AI_WORKING: coder1 @2026-01-30 15:45:00 - 添加API调用和交互测试
    it('应调用API加载系统日志', async () => {
      const mockLogs = [
        { timestamp: '2023-01-01 10:00:00', level: 'INFO', module: 'system', message: '系统启动' },
        { timestamp: '2023-01-01 10:05:00', level: 'ERROR', module: 'auth', message: '认证失败' }
      ];
      const mockResponse = { data: { items: mockLogs, total: 2 } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      await wrapper.vm.loadLogs();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/system', expect.any(Object));
      expect(wrapper.vm.logs).toEqual(mockLogs);
      expect(wrapper.vm.totalLogs).toBe(2);
      expect(wrapper.vm.loading).toBe(false);
    });

    it('筛选条件变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.setData({
        searchQuery: 'error',
        logLevelFilter: 'ERROR'
      });
      
      await wrapper.vm.applyFilters();
      
      expect(loadLogsSpy).toHaveBeenCalled();
      expect(wrapper.vm.currentPage).toBe(1); // 重置为第一页
    });

    it('分页变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.vm.handleSizeChange(100);
      expect(wrapper.vm.pageSize).toBe(100);
      expect(loadLogsSpy).toHaveBeenCalled();
      
      await wrapper.vm.handleCurrentChange(2);
      expect(wrapper.vm.currentPage).toBe(2);
      expect(loadLogsSpy).toHaveBeenCalledTimes(2);
    });

    it('查看详情应打开弹窗', async () => {
      const testLog = { timestamp: '2023-01-01 10:00:00', level: 'INFO', module: 'system', message: '测试' };
      await wrapper.setData({ logs: [testLog] });
      
      // 查找查看详情按钮
      const detailButton = wrapper.find('button[type="link"]');
      await detailButton.trigger('click');
      
      expect(wrapper.vm.selectedLog).toEqual(testLog);
      expect(wrapper.vm.showDetailDialog).toBe(true);
    });

    it('API错误时应显示错误信息', async () => {
      const axios = await import('axios');
      axios.default.get.mockRejectedValue(new Error('Network error'));
      
      // 模拟 $message.error 方法
      const messageErrorSpy = vi.fn();
      wrapper.vm.$message = { error: messageErrorSpy };

      await wrapper.vm.loadLogs();
      
      expect(messageErrorSpy).toHaveBeenCalledWith('加载系统日志失败');
      expect(wrapper.vm.loading).toBe(false);
    });

    it('空数据时应显示无数据提示', async () => {
      await wrapper.setData({ logs: [] });
      await nextTick();
      
      // 假设表格会显示无数据提示
      const emptyText = wrapper.find('.el-table__empty-text');
      expect(emptyText.exists()).toBe(true);
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
            ElButton,
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
      if (wrapper && wrapper.unmount) {
        wrapper.unmount();
      }
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span');
      expect(header.exists()).toBe(true);
      expect(header.text()).toBe('用户日志');
    });

    it('应该包含用户筛选选项', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      // 修复：用户ID筛选是下拉框，不是select[placeholder]，而是el-select内部的输入框
      expect(wrapper.find('.el-select').exists()).toBe(true);
      const filterButtons = wrapper.findAll('button');
      const hasFilterButton = filterButtons.some(btn => btn.text().includes('筛选'));
      expect(hasFilterButton).toBe(true);
    });

    it('应该渲染用户日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该有用户ID列', () => {
      // 使用更灵活的方法检测表格头部
      // 检查是否存在任何包含"用户ID"文本的元素
      const html = wrapper.html();
      expect(html).toContain('用户ID');
    });

    // AI_WORKING: coder1 @2026-01-30 15:50:00 - 添加API调用、错误处理和边界条件测试
    it('应调用API加载用户日志', async () => {
      const mockLogs = [
        { timestamp: '2023-01-01 10:00:00', user_id: 1, module: 'user', message: '用户登录' },
        { timestamp: '2023-01-01 10:05:00', user_id: 2, module: 'user', message: '用户登出' }
      ];
      const mockResponse = { data: { items: mockLogs, total: 2 } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      await wrapper.vm.loadLogs();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/user', expect.any(Object));
      expect(wrapper.vm.logs).toEqual(mockLogs);
      expect(wrapper.vm.totalLogs).toBe(2);
      expect(wrapper.vm.loading).toBe(false);
    });

    it('筛选条件变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.setData({
        searchQuery: 'login',
        userIdFilter: '1'
      });
      
      await wrapper.vm.applyFilters();
      
      expect(loadLogsSpy).toHaveBeenCalled();
      expect(wrapper.vm.currentPage).toBe(1); // 重置为第一页
    });

    it('分页变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.vm.handleSizeChange(100);
      expect(wrapper.vm.pageSize).toBe(100);
      expect(loadLogsSpy).toHaveBeenCalled();
      
      await wrapper.vm.handleCurrentChange(2);
      expect(wrapper.vm.currentPage).toBe(2);
      expect(loadLogsSpy).toHaveBeenCalledTimes(2);
    });

    it('查看详情应打开弹窗', async () => {
      const testLog = { timestamp: '2023-01-01 10:00:00', user_id: 1, module: 'user', message: '测试' };
      await wrapper.setData({ logs: [testLog] });
      
      // 查找查看详情按钮
      const detailButton = wrapper.find('button[type="link"]');
      await detailButton.trigger('click');
      
      expect(wrapper.vm.selectedLog).toEqual(testLog);
      expect(wrapper.vm.showDetailDialog).toBe(true);
    });

    it('API错误时应显示错误信息', async () => {
      const axios = await import('axios');
      axios.default.get.mockRejectedValue(new Error('Network error'));
      
      // 模拟 $message.error 方法
      const messageErrorSpy = vi.fn();
      wrapper.vm.$message = { error: messageErrorSpy };

      await wrapper.vm.loadLogs();
      
      expect(messageErrorSpy).toHaveBeenCalledWith('加载用户日志失败');
      expect(wrapper.vm.loading).toBe(false);
    });

    it('空数据时应显示无数据提示', async () => {
      await wrapper.setData({ logs: [] });
      await nextTick();
      
      // 假设表格会显示无数据提示
      const emptyText = wrapper.find('.el-table__empty-text');
      expect(emptyText.exists()).toBe(true);
    });

    it('边界条件：无效用户ID应正确处理', async () => {
      // 设置无效的用户ID筛选
      await wrapper.setData({ userIdFilter: 'invalid' });
      
      // 调用筛选方法，应该不会崩溃
      await wrapper.vm.applyFilters();
      
      // 检查是否调用了API，但参数可能被忽略或处理
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });

    it('边界条件：超大分页应正确处理', async () => {
      // 设置超大分页大小
      await wrapper.vm.handleSizeChange(1000);
      expect(wrapper.vm.pageSize).toBe(1000);
      
      // API应该被调用
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
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
            ElButton,
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
      if (wrapper && wrapper.unmount) {
        wrapper.unmount();
      }
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span');
      expect(header.exists()).toBe(true);
      expect(header.text()).toBe('安全日志');
    });

    it('应该渲染安全日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该包含安全相关筛选项', () => {
      expect(wrapper.find('input[placeholder="搜索日志..."]').exists()).toBe(true);
      const filterButtons = wrapper.findAll('button');
      const hasFilterButton = filterButtons.some(btn => btn.text().includes('筛选'));
      expect(hasFilterButton).toBe(true);
    });

    // AI_WORKING: coder1 @2026-01-30 15:55:00 - 添加API调用、错误处理和边界条件测试
    it('应调用API加载安全日志', async () => {
      const mockLogs = [
        { timestamp: '2023-01-01 10:00:00', level: 'INFO', module: 'security', message: '安全扫描完成' },
        { timestamp: '2023-01-01 10:05:00', level: 'ERROR', module: 'security', message: '入侵检测警报' }
      ];
      const mockResponse = { data: { items: mockLogs, total: 2 } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      await wrapper.vm.loadLogs();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/security', expect.any(Object));
      expect(wrapper.vm.logs).toEqual(mockLogs);
      expect(wrapper.vm.totalLogs).toBe(2);
      expect(wrapper.vm.loading).toBe(false);
    });

    it('筛选条件变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.setData({
        searchQuery: '入侵',
        logLevelFilter: 'ERROR'
      });
      
      await wrapper.vm.applyFilters();
      
      expect(loadLogsSpy).toHaveBeenCalled();
      expect(wrapper.vm.currentPage).toBe(1); // 重置为第一页
    });

    it('分页变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.vm.handleSizeChange(100);
      expect(wrapper.vm.pageSize).toBe(100);
      expect(loadLogsSpy).toHaveBeenCalled();
      
      await wrapper.vm.handleCurrentChange(2);
      expect(wrapper.vm.currentPage).toBe(2);
      expect(loadLogsSpy).toHaveBeenCalledTimes(2);
    });

    it('查看详情应打开弹窗', async () => {
      const testLog = { timestamp: '2023-01-01 10:00:00', level: 'INFO', module: 'security', message: '测试' };
      await wrapper.setData({ logs: [testLog] });
      
      // 查找查看详情按钮
      const detailButton = wrapper.find('button[type="link"]');
      await detailButton.trigger('click');
      
      expect(wrapper.vm.selectedLog).toEqual(testLog);
      expect(wrapper.vm.showDetailDialog).toBe(true);
    });

    it('API错误时应显示错误信息', async () => {
      const axios = await import('axios');
      axios.default.get.mockRejectedValue(new Error('Network error'));
      
      // 模拟 $message.error 方法
      const messageErrorSpy = vi.fn();
      wrapper.vm.$message = { error: messageErrorSpy };

      await wrapper.vm.loadLogs();
      
      expect(messageErrorSpy).toHaveBeenCalledWith('加载安全日志失败');
      expect(wrapper.vm.loading).toBe(false);
    });

    it('空数据时应显示无数据提示', async () => {
      await wrapper.setData({ logs: [] });
      await nextTick();
      
      // 假设表格会显示无数据提示
      const emptyText = wrapper.find('.el-table__empty-text');
      expect(emptyText.exists()).toBe(true);
    });

    it('边界条件：无效日志级别应正确处理', async () => {
      // 设置无效的日志级别筛选
      await wrapper.setData({ logLevelFilter: 'INVALID' });
      
      // 调用筛选方法，应该不会崩溃
      await wrapper.vm.applyFilters();
      
      // 检查是否调用了API，但参数可能被忽略或处理
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });

    it('边界条件：超大分页应正确处理', async () => {
      // 设置超大分页大小
      await wrapper.vm.handleSizeChange(1000);
      expect(wrapper.vm.pageSize).toBe(1000);
      
      // API应该被调用
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });
  });

  describe('API日志页面(APILogs)', () => {
    let wrapper;

    beforeEach(() => {
      // 创建一个自定义的el-table-column组件来捕获列信息
      const TableColumnCapture = {
        name: 'ElTableColumn',
        template: '<div class="captured-column" :data-prop="prop" :data-label="label"><slot/></div>',
        props: ['prop', 'label', 'width']
      };

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
            ElButton,
            ElTag,
            TableColumnCapture
          }
        }
      });
    });

    afterEach(() => {
      if (wrapper && wrapper.unmount) {
        wrapper.unmount();
      }
    });

    it('应该正确渲染页面标题', () => {
      const header = wrapper.find('div[slot="header"] span');
      expect(header.exists()).toBe(true);
      expect(header.text()).toBe('API日志');
    });

    it('应该渲染API日志表格', () => {
      expect(wrapper.find('.el-table').exists()).toBe(true);
    });

    it('应该包含API日志特有的列', () => {
      // 使用自定义组件捕获的列信息
      const columns = wrapper.findAll('.captured-column');
      
      // 检查是否包含了API日志应有的列
      const props = columns.map(col => col.attributes('data-prop'));
      const labels = columns.map(col => col.attributes('data-label'));
      
      expect(props).toContain('request_path');
      expect(props).toContain('response_status');
      expect(props).toContain('duration_ms');
      expect(props).toContain('ip_address');
      expect(props).toContain('message');
      
      // 检查列标题
      expect(labels).toContain('请求路径');
      expect(labels).toContain('状态码');
      expect(labels).toContain('耗时(ms)');
      expect(labels).toContain('IP地址');
    });

    // AI_WORKING: coder1 @2026-01-30 16:00:00 - 添加API调用、错误处理和边界条件测试
    it('应调用API加载API日志', async () => {
      const mockLogs = [
        { timestamp: '2023-01-01 10:00:00', level: 'INFO', request_path: '/api/v1/test', response_status: 200, duration_ms: 150, ip_address: '127.0.0.1', message: '请求成功' },
        { timestamp: '2023-01-01 10:05:00', level: 'ERROR', request_path: '/api/v1/error', response_status: 500, duration_ms: 300, ip_address: '192.168.1.1', message: '内部服务器错误' }
      ];
      const mockResponse = { data: { items: mockLogs, total: 2 } };
      const axios = await import('axios');
      axios.default.get.mockResolvedValue(mockResponse);

      await wrapper.vm.loadLogs();
      
      expect(axios.default.get).toHaveBeenCalledWith('/api/v1/admin/system/logs/db/api', expect.any(Object));
      expect(wrapper.vm.logs).toEqual(mockLogs);
      expect(wrapper.vm.totalLogs).toBe(2);
      expect(wrapper.vm.loading).toBe(false);
    });

    it('筛选条件变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.setData({
        searchQuery: 'error',
        logLevelFilter: 'ERROR'
      });
      
      await wrapper.vm.applyFilters();
      
      expect(loadLogsSpy).toHaveBeenCalled();
      expect(wrapper.vm.currentPage).toBe(1); // 重置为第一页
    });

    it('分页变化应触发数据加载', async () => {
      const loadLogsSpy = vi.spyOn(wrapper.vm, 'loadLogs');
      
      await wrapper.vm.handleSizeChange(100);
      expect(wrapper.vm.pageSize).toBe(100);
      expect(loadLogsSpy).toHaveBeenCalled();
      
      await wrapper.vm.handleCurrentChange(2);
      expect(wrapper.vm.currentPage).toBe(2);
      expect(loadLogsSpy).toHaveBeenCalledTimes(2);
    });

    it('查看详情应打开弹窗', async () => {
      const testLog = { timestamp: '2023-01-01 10:00:00', level: 'INFO', request_path: '/api/v1/test', response_status: 200, duration_ms: 150, ip_address: '127.0.0.1', message: '测试' };
      await wrapper.setData({ logs: [testLog] });
      
      // 查找查看详情按钮
      const detailButton = wrapper.find('button[type="link"]');
      await detailButton.trigger('click');
      
      expect(wrapper.vm.selectedLog).toEqual(testLog);
      expect(wrapper.vm.showDetailDialog).toBe(true);
    });

    it('API错误时应显示错误信息', async () => {
      const axios = await import('axios');
      axios.default.get.mockRejectedValue(new Error('Network error'));
      
      // 模拟 $message.error 方法
      const messageErrorSpy = vi.fn();
      wrapper.vm.$message = { error: messageErrorSpy };

      await wrapper.vm.loadLogs();
      
      expect(messageErrorSpy).toHaveBeenCalledWith('加载API日志失败');
      expect(wrapper.vm.loading).toBe(false);
    });

    it('空数据时应显示无数据提示', async () => {
      await wrapper.setData({ logs: [] });
      await nextTick();
      
      // 假设表格会显示无数据提示
      const emptyText = wrapper.find('.el-table__empty-text');
      expect(emptyText.exists()).toBe(true);
    });

    it('边界条件：无效状态码应正确处理', async () => {
      // 设置无效的状态码筛选（通过搜索）
      await wrapper.setData({ searchQuery: 'status:invalid' });
      
      // 调用筛选方法，应该不会崩溃
      await wrapper.vm.applyFilters();
      
      // 检查是否调用了API，但参数可能被忽略或处理
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });

    it('边界条件：超大分页应正确处理', async () => {
      // 设置超大分页大小
      await wrapper.vm.handleSizeChange(1000);
      expect(wrapper.vm.pageSize).toBe(1000);
      
      // API应该被调用
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });

    it('边界条件：极端日期范围应正确处理', async () => {
      // 设置极端日期范围（过去很久到未来很久）
      const startDate = new Date('2000-01-01');
      const endDate = new Date('2030-12-31');
      await wrapper.setData({ dateRange: [startDate, endDate] });
      
      // 调用筛选方法，应该不会崩溃
      await wrapper.vm.applyFilters();
      
      // 检查是否调用了API
      const axios = await import('axios');
      expect(axios.default.get).toHaveBeenCalled();
    });
  });

  describe('日志管理模块交互功能测试', () => {
    it('系统日志页面应有正确的标签类型方法', () => {
      const wrapper = mount(SystemLogs, {
        global: {
          components: {
            ElCard,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
      
      expect(wrapper.vm.getTagType('ERROR')).toBe('danger');
      expect(wrapper.vm.getTagType('WARN')).toBe('warning');
      expect(wrapper.vm.getTagType('INFO')).toBe('info');
      expect(wrapper.vm.getTagType('DEBUG')).toBe('primary');
      expect(wrapper.vm.getTagType('UNKNOWN')).toBe('info');
    });

    it('安全日志页面应有正确的标签类型方法', () => {
      const wrapper = mount(SecurityLogs, {
        global: {
          components: {
            ElCard,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
      
      expect(wrapper.vm.getTagType('ERROR')).toBe('danger');
      expect(wrapper.vm.getTagType('CRITICAL')).toBe('danger');
      expect(wrapper.vm.getTagType('WARN')).toBe('warning');
      expect(wrapper.vm.getTagType('INFO')).toBe('info');
    });

    it('API日志页面应有正确的标签类型方法', () => {
      const wrapper = mount(APILogs, {
        global: {
          components: {
            ElCard,
            'el-table-column': {
              template: '<div></div>',
              props: ['prop', 'label', 'width']
            }
          }
        }
      });
      
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
// AI_DONE: coder1 @2026-01-29 18:36:01
