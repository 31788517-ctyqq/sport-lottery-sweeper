import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { getUserList, createUser, updateUser, deleteUser, updateUserStatus, resetUserPassword } from '@/api/userManagement';

// Mock API 响应
const mockAxios = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn()
};

vi.mock('axios', () => ({
  default: mockAxios
}));

describe('用户管理API集成测试', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('用户列表API测试', () => {
    it('应该能够获取用户列表', async () => {
      // Mock API 响应
      const mockResponse = {
        data: {
          users: [
            { id: 1, username: 'testuser', email: 'test@example.com', role: 'user', status: 'active', created_at: '2023-01-01', updated_at: '2023-01-01' },
            { id: 2, username: 'admin', email: 'admin@example.com', role: 'admin', status: 'active', created_at: '2023-01-01', updated_at: '2023-01-01' }
          ],
          total: 2
        }
      };
      
      mockAxios.get.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10 };
      const response = await getUserList(params);

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/backend-users', { params });
      expect(response).toEqual(mockResponse);
    });

    it('应该能够带参数搜索用户', async () => {
      const mockResponse = {
        data: {
          users: [{ id: 1, username: 'testuser', email: 'test@example.com', role: 'user', status: 'active' }],
          total: 1
        }
      };
      
      mockAxios.get.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10, search: 'test', status: 'active' };
      const response = await getUserList(params);

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/backend-users', { params });
      expect(response).toEqual(mockResponse);
    });
  });

  describe('用户创建API测试', () => {
    it('应该能够创建新用户', async () => {
      const newUser = {
        username: 'newuser',
        email: 'newuser@example.com',
        role: 'user',
        status: 'active'
      };

      const mockResponse = {
        data: {
          id: 3,
          username: 'newuser',
          email: 'newuser@example.com',
          role: 'user',
          status: 'active',
          created_at: '2023-01-01',
          updated_at: '2023-01-01'
        }
      };

      mockAxios.post.mockResolvedValue(mockResponse);

      const response = await createUser(newUser);

      expect(mockAxios.post).toHaveBeenCalledWith('/api/v1/admin/backend-users', newUser);
      expect(response).toEqual(mockResponse);
    });

    it('应该在创建用户时验证输入数据', async () => {
      const invalidUser = {
        username: '', // 空用户名
        email: 'invalid-email', // 无效邮箱
        role: 'user',
        status: 'active'
      };

      mockAxios.post.mockRejectedValue(new Error('Invalid input'));

      await expect(createUser(invalidUser)).rejects.toThrow('Invalid input');
    });
  });

  describe('用户更新API测试', () => {
    it('应该能够更新用户信息', async () => {
      const userId = 1;
      const updatedUserData = {
        username: 'updateduser',
        email: 'updated@example.com',
        role: 'manager',
        status: 'active'
      };

      const mockResponse = {
        data: {
          id: 1,
          username: 'updateduser',
          email: 'updated@example.com',
          role: 'manager',
          status: 'active',
          created_at: '2023-01-01',
          updated_at: '2023-01-02'
        }
      };

      mockAxios.put.mockResolvedValue(mockResponse);

      const response = await updateUser(userId, updatedUserData);

      expect(mockAxios.put).toHaveBeenCalledWith(`/api/v1/admin/backend-users/${userId}`, updatedUserData);
      expect(response).toEqual(mockResponse);
    });

    it('应该能够更新用户状态', async () => {
      const userId = 1;
      const newStatus = 'inactive';

      const mockResponse = {
        data: {
          success: true
        }
      };

      mockAxios.patch.mockResolvedValue(mockResponse);

      const response = await updateUserStatus(userId, newStatus);

      expect(mockAxios.patch).toHaveBeenCalledWith(`/api/v1/admin/backend-users/${userId}/status`, { status: newStatus });
      expect(response).toEqual(mockResponse);
    });
  });

  describe('用户删除API测试', () => {
    it('应该能够删除用户', async () => {
      const userId = 1;

      const mockResponse = {
        data: {
          success: true
        }
      };

      mockAxios.delete.mockResolvedValue(mockResponse);

      const response = await deleteUser(userId);

      expect(mockAxios.delete).toHaveBeenCalledWith(`/api/v1/admin/backend-users/${userId}`);
      expect(response).toEqual(mockResponse);
    });

    it('应该能够批量删除用户', async () => {
      const userIds = [1, 2, 3];

      // 模拟多个删除请求
      const deletePromises = userIds.map(id => deleteUser(id));
      const results = await Promise.all(deletePromises);

      userIds.forEach((id, index) => {
        expect(mockAxios.delete).toHaveBeenCalledWith(`/api/v1/admin/backend-users/${id}`);
        expect(results[index]).toBeDefined();
      });
    });
  });

  describe('用户密码重置API测试', () => {
    it('应该能够重置用户密码', async () => {
      const userId = 1;
      const newPassword = 'newpassword123';

      const mockResponse = {
        data: {
          success: true
        }
      };

      mockAxios.post.mockResolvedValue(mockResponse);

      const response = await resetUserPassword(userId, newPassword);

      expect(mockAxios.post).toHaveBeenCalledWith(`/api/v1/admin/backend-users/${userId}/reset-password`, {
        password: newPassword
      });
      expect(response).toEqual(mockResponse);
    });
  });

  describe('错误处理测试', () => {
    it('应该正确处理API错误', async () => {
      const errorMessage = '用户不存在';
      mockAxios.get.mockRejectedValue(new Error(errorMessage));

      await expect(getUserList({ page: 1, size: 10 })).rejects.toThrow(errorMessage);
    });

    it('应该正确处理网络错误', async () => {
      mockAxios.get.mockRejectedValue(new Error('Network Error'));

      await expect(getUserList({ page: 1, size: 10 })).rejects.toThrow('Network Error');
    });
  });

  describe('参数验证测试', () => {
    it('应该正确传递分页参数', async () => {
      const mockResponse = { data: { users: [], total: 0 } };
      mockAxios.get.mockResolvedValue(mockResponse);

      const params = { page: 2, size: 20 };
      await getUserList(params);

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/backend-users', { params });
    });

    it('应该正确传递筛选参数', async () => {
      const mockResponse = { data: { users: [], total: 0 } };
      mockAxios.get.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10, search: 'test', role: 'admin', status: 'active' };
      await getUserList(params);

      expect(mockAxios.get).toHaveBeenCalledWith('/api/v1/admin/backend-users', { params });
    });
  });
});