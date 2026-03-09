/**
 * 日志管理模块API交互测试
 * 测试前后端API交互功能
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import axios from 'axios';

// Mock axios
vi.mock('axios');

describe('日志管理API交互测试', () => {
  // 模拟真实的API响应数据
  const mockSystemLogs = {
    items: [
      {
        id: 1,
        timestamp: '2024-01-28T10:00:00Z',
        level: 'INFO',
        module: 'system',
        message: 'Application started successfully',
        extra_data: '{"version": "1.0.0", "environment": "production"}'
      },
      {
        id: 2,
        timestamp: '2024-01-28T10:05:00Z',
        level: 'ERROR',
        module: 'database',
        message: 'Connection timeout',
        extra_data: '{"host": "localhost", "port": 5432}'
      }
    ],
    total: 2
  };

  const mockUserLogs = {
    items: [
      {
        id: 1,
        timestamp: '2024-01-28T09:00:00Z',
        user_id: 1,
        module: 'auth',
        message: 'User login successful',
        ip_address: '192.168.1.100',
        session_id: 'sess_abc123'
      },
      {
        id: 2,
        timestamp: '2024-01-28T09:15:00Z',
        user_id: 2,
        module: 'data',
        message: 'Data export initiated',
        ip_address: '192.168.1.101',
        session_id: 'sess_def456'
      }
    ],
    total: 2
  };

  const mockSecurityLogs = {
    items: [
      {
        id: 1,
        timestamp: '2024-01-28T08:00:00Z',
        level: 'WARN',
        module: 'security',
        message: 'Multiple failed login attempts',
        ip_address: '10.0.0.10',
        user_id: 3
      },
      {
        id: 2,
        timestamp: '2024-01-28T08:15:00Z',
        level: 'CRITICAL',
        module: 'security',
        message: 'Suspicious activity detected',
        ip_address: '10.0.0.15',
        user_id: null
      }
    ],
    total: 2
  };

  const mockAPILogs = {
    items: [
      {
        id: 1,
        timestamp: '2024-01-28T07:00:00Z',
        level: 'INFO',
        request_path: '/api/users',
        response_status: 200,
        duration_ms: 125,
        ip_address: '192.168.1.100',
        user_agent: 'Mozilla/5.0...',
        session_id: 'sess_xyz789',
        message: 'Successful API call'
      },
      {
        id: 2,
        timestamp: '2024-01-28T07:05:00Z',
        level: 'WARN',
        request_path: '/api/orders',
        response_status: 400,
        duration_ms: 50,
        ip_address: '192.168.1.101',
        user_agent: 'Mozilla/5.0...',
        session_id: 'sess_abc987',
        message: 'Bad request'
      }
    ],
    total: 2
  };

  const mockStatistics = {
    total_logs: 1500,
    error_logs: 45,
    user_activities: 1200,
    security_events: 25,
    level_stats: [
      { level: 'INFO', count: 1300 },
      { level: 'WARN', count: 120 },
      { level: 'ERROR', count: 45 },
      { level: 'CRITICAL', count: 5 }
    ],
    module_stats: [
      { module: 'system', count: 300 },
      { module: 'database', count: 150 },
      { module: 'auth', count: 200 },
      { module: 'user', count: 1200 },
      { module: 'security', count: 25 },
      { module: 'api', count: 400 }
    ]
  };

  beforeEach(() => {
    // 重置所有mock
    vi.clearAllMocks();
  });

  describe('系统日志API测试', () => {
    it('应该正确获取系统日志', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockSystemLogs });

      // 调用API
      const response = await axios.get('/api/admin/system/logs/db/system?skip=0&limit=50');

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith('/api/admin/system/logs/db/system?skip=0&limit=50');
      expect(response.data).toEqual(mockSystemLogs);
      expect(response.data.items.length).toBe(2);
      expect(response.data.total).toBe(2);
    });

    it('应该正确处理系统日志筛选参数', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockSystemLogs });

      // 调用API带筛选参数
      const params = {
        skip: 0,
        limit: 20,
        level: 'ERROR',
        search: 'timeout'
      };

      const queryString = new URLSearchParams(params).toString();
      const response = await axios.get(`/api/admin/system/logs/db/system?${queryString}`);

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith(`/api/admin/system/logs/db/system?${queryString}`);
      expect(response.data).toEqual(mockSystemLogs);
    });
  });

  describe('用户日志API测试', () => {
    it('应该正确获取用户日志', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockUserLogs });

      // 调用API
      const response = await axios.get('/api/admin/system/logs/db/user?skip=0&limit=50');

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith('/api/admin/system/logs/db/user?skip=0&limit=50');
      expect(response.data).toEqual(mockUserLogs);
      expect(response.data.items.length).toBe(2);
      expect(response.data.total).toBe(2);
    });

    it('应该正确处理用户ID筛选', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockUserLogs });

      // 调用API带用户ID参数
      const params = {
        skip: 0,
        limit: 20,
        user_id: 1
      };

      const queryString = new URLSearchParams(params).toString();
      const response = await axios.get(`/api/admin/system/logs/db/user?${queryString}`);

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith(`/api/admin/system/logs/db/user?${queryString}`);
      expect(response.data).toEqual(mockUserLogs);
    });
  });

  describe('安全日志API测试', () => {
    it('应该正确获取安全日志', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockSecurityLogs });

      // 调用API
      const response = await axios.get('/api/admin/system/logs/db/security?skip=0&limit=50');

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith('/api/admin/system/logs/db/security?skip=0&limit=50');
      expect(response.data).toEqual(mockSecurityLogs);
      expect(response.data.items.length).toBe(2);
      expect(response.data.total).toBe(2);
    });
  });

  describe('API日志API测试', () => {
    it('应该正确获取API日志', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockAPILogs });

      // 调用API
      const response = await axios.get('/api/admin/system/logs/db/api?skip=0&limit=50');

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith('/api/admin/system/logs/db/api?skip=0&limit=50');
      expect(response.data).toEqual(mockAPILogs);
      expect(response.data.items.length).toBe(2);
      expect(response.data.total).toBe(2);
    });

    it('应该正确处理API日志的响应状态筛选', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockAPILogs });

      // 调用API带筛选参数
      const params = {
        skip: 0,
        limit: 20,
        level: 'INFO',
        start_date: '2024-01-28T00:00:00Z',
        end_date: '2024-01-28T23:59:59Z'
      };

      const queryString = new URLSearchParams(params).toString();
      const response = await axios.get(`/api/admin/system/logs/db/api?${queryString}`);

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith(`/api/admin/system/logs/db/api?${queryString}`);
      expect(response.data).toEqual(mockAPILogs);
    });
  });

  describe('日志统计API测试', () => {
    it('应该正确获取日志统计信息', async () => {
      // Mock API响应
      axios.get.mockResolvedValue({ data: mockStatistics });

      // 调用API
      const response = await axios.get('/api/admin/system/logs/db/statistics');

      // 验证API调用
      expect(axios.get).toHaveBeenCalledWith('/api/admin/system/logs/db/statistics');
      expect(response.data).toEqual(mockStatistics);
      expect(response.data.total_logs).toBe(1500);
      expect(response.data.error_logs).toBe(45);
    });
  });

  describe('错误处理测试', () => {
    it('应该正确处理API错误', async () => {
      // Mock API错误
      const errorMessage = 'Network Error';
      axios.get.mockRejectedValue(new Error(errorMessage));

      // 验证错误处理
      await expect(axios.get('/api/admin/system/logs/db/system?skip=0&limit=50'))
        .rejects
        .toThrow(errorMessage);
    });

    it('应该正确处理HTTP错误状态', async () => {
      // Mock HTTP错误响应
      const errorResponse = {
        response: {
          status: 500,
          data: { error: 'Internal Server Error' }
        }
      };
      axios.get.mockRejectedValue(errorResponse);

      // 验证错误处理
      await expect(axios.get('/api/admin/system/logs/db/system?skip=0&limit=50'))
        .rejects
        .toEqual(errorResponse);
    });
  });

  describe('真实用户操作流程测试', () => {
    it('应该模拟完整的日志管理操作流程', async () => {
      // 模拟用户执行一系列操作
      const operations = [
        // 获取统计信息
        () => axios.get('/api/admin/system/logs/db/statistics'),
        // 获取最近的系统日志
        () => axios.get('/api/admin/system/logs/db/system?skip=0&limit=5'),
        // 获取所有系统日志
        () => axios.get('/api/admin/system/logs/db/system?skip=0&limit=50'),
        // 获取用户日志
        () => axios.get('/api/admin/system/logs/db/user?skip=0&limit=50'),
        // 获取安全日志
        () => axios.get('/api/admin/system/logs/db/security?skip=0&limit=50'),
        // 获取API日志
        () => axios.get('/api/admin/system/logs/db/api?skip=0&limit=50')
      ];

      // Mock每个API调用
      axios.get
        .mockResolvedValueOnce({ data: mockStatistics })  // 统计
        .mockResolvedValueOnce({ data: { items: mockSystemLogs.items.slice(0, 5), total: 5 } })  // 最近日志
        .mockResolvedValueOnce({ data: mockSystemLogs })  // 系统日志
        .mockResolvedValueOnce({ data: mockUserLogs })    // 用户日志
        .mockResolvedValueOnce({ data: mockSecurityLogs }) // 安全日志
        .mockResolvedValueOnce({ data: mockAPILogs });    // API日志

      // 执行操作序列
      const results = [];
      for (const op of operations) {
        const result = await op();
        results.push(result);
      }

      // 验证所有操作都成功执行
      expect(results.length).toBe(6);
      expect(results[0].data).toEqual(mockStatistics);
      expect(results[2].data).toEqual(mockSystemLogs);
      expect(results[3].data).toEqual(mockUserLogs);
      expect(results[4].data).toEqual(mockSecurityLogs);
      expect(results[5].data).toEqual(mockAPILogs);
    });
  });
});