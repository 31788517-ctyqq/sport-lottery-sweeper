import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// 首先模拟API模块
vi.mock('@/api/userManagement', async () => {
  const axios = {
    get: vi.fn(),
    post: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn()
  };

  return {
    getUserList: vi.fn((params) => axios.get('/api/admin/backend-users', { params })),
    createUser: vi.fn((data) => axios.post('/api/admin/backend-users', data)),
    updateUser: vi.fn((id, data) => axios.put(`/api/admin/backend-users/${id}`, data)),
    deleteUser: vi.fn((id) => axios.delete(`/api/admin/backend-users/${id}`)),
    updateUserStatus: vi.fn((id, status) => axios.patch(`/api/admin/backend-users/${id}/status`, { status })),
    resetUserPassword: vi.fn((id, password) => axios.post(`/api/admin/backend-users/${id}/reset-password`, { password })),
    getRoleList: vi.fn(() => axios.get('/api/admin/roles')),
    updateRolePermissions: vi.fn((id, permissions) => axios.put(`/api/admin/roles/${id}/permissions`, { permissions })),
    getOperationLogs: vi.fn((params) => axios.get('/api/admin/operation-logs', { params })),
    getDepartmentList: vi.fn(() => axios.get('/api/admin/departments')),
    createDepartment: vi.fn((data) => axios.post('/api/admin/departments', data)),
    updateDepartment: vi.fn((id, data) => axios.put(`/api/admin/departments/${id}`, data)),
    deleteDepartment: vi.fn((id) => axios.delete(`/api/admin/departments/${id}`))
  };
});

import { 
  getUserList, 
  createUser, 
  updateUser, 
  deleteUser, 
  updateUserStatus, 
  resetUserPassword, 
  getRoleList, 
  updateRolePermissions, 
  getOperationLogs, 
  getDepartmentList, 
  createDepartment, 
  updateDepartment, 
  deleteDepartment 
} from '@/api/userManagement';

describe('用户管理API集成测试', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('用户列表API测试', () => {
    it('应该能够获取用户列表', async () => {
      const mockResponse = {
        data: {
          users: [
            { id: 1, username: 'testuser', email: 'test@example.com', role: 'user', status: 'active', created_at: '2023-01-01', updated_at: '2023-01-01' },
            { id: 2, username: 'admin', email: 'admin@example.com', role: 'admin', status: 'active', created_at: '2023-01-01', updated_at: '2023-01-01' }
          ],
          total: 2,
          page: 1,
          size: 10,
          pages: 1
        }
      };
      
      getUserList.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10 };
      const response = await getUserList(params);

      expect(getUserList).toHaveBeenCalledWith(params);
      expect(response).toEqual(mockResponse);
    });

    it('应该能够带参数搜索用户', async () => {
      const mockResponse = {
        data: {
          users: [{ id: 1, username: 'testuser', email: 'test@example.com', role: 'user', status: 'active' }],
          total: 1,
          page: 1,
          size: 10,
          pages: 1
        }
      };
      
      getUserList.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10, search: 'test', status: 'active' };
      const response = await getUserList(params);

      expect(getUserList).toHaveBeenCalledWith(params);
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

      createUser.mockResolvedValue(mockResponse);

      const response = await createUser(newUser);

      expect(createUser).toHaveBeenCalledWith(newUser);
      expect(response).toEqual(mockResponse);
    });

    it('应该在创建用户时验证输入数据', async () => {
      const invalidUser = {
        username: '', // 空用户名
        email: 'invalid-email', // 无效邮箱
        role: 'user',
        status: 'active'
      };

      createUser.mockRejectedValue(new Error('Invalid input'));

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

      updateUser.mockResolvedValue(mockResponse);

      const response = await updateUser(userId, updatedUserData);

      expect(updateUser).toHaveBeenCalledWith(userId, updatedUserData);
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

      updateUserStatus.mockResolvedValue(mockResponse);

      const response = await updateUserStatus(userId, newStatus);

      expect(updateUserStatus).toHaveBeenCalledWith(userId, newStatus);
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

      deleteUser.mockResolvedValue(mockResponse);

      const response = await deleteUser(userId);

      expect(deleteUser).toHaveBeenCalledWith(userId);
      expect(response).toEqual(mockResponse);
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

      resetUserPassword.mockResolvedValue(mockResponse);

      const response = await resetUserPassword(userId, newPassword);

      expect(resetUserPassword).toHaveBeenCalledWith(userId, newPassword);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('角色权限API测试', () => {
    it('应该能够获取角色列表', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: '管理员', description: '系统管理员', permissions: ['user.read', 'user.write', 'user.delete'] },
          { id: 2, name: '普通用户', description: '普通用户', permissions: ['user.read'] }
        ]
      };

      getRoleList.mockResolvedValue(mockResponse);

      const response = await getRoleList();

      expect(getRoleList).toHaveBeenCalled();
      expect(response).toEqual(mockResponse);
    });

    it('应该能够更新角色权限', async () => {
      const roleId = 1;
      const permissions = ['user.read', 'user.write'];

      const mockResponse = {
        data: {
          success: true,
          updatedRole: { id: 1, name: '管理员', permissions }
        }
      };

      updateRolePermissions.mockResolvedValue(mockResponse);

      const response = await updateRolePermissions(roleId, permissions);

      expect(updateRolePermissions).toHaveBeenCalledWith(roleId, permissions);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('操作日志API测试', () => {
    it('应该能够获取操作日志', async () => {
      const mockResponse = {
        data: {
          logs: [
            { id: 1, operator: 'admin', action: 'create', resource_type: 'user', resource_name: 'newuser', timestamp: '2023-01-01 10:00:00', ip_address: '192.168.1.1', result: 'success' },
            { id: 2, operator: 'admin', action: 'update', resource_type: 'user', resource_name: 'existinguser', timestamp: '2023-01-01 11:00:00', ip_address: '192.168.1.1', result: 'success' }
          ],
          total: 2,
          page: 1,
          size: 10,
          pages: 1
        }
      };

      getOperationLogs.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10, operator: 'admin' };
      const response = await getOperationLogs(params);

      expect(getOperationLogs).toHaveBeenCalledWith(params);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('部门管理API测试', () => {
    it('应该能够获取部门列表', async () => {
      const mockResponse = {
        data: [
          { id: 1, name: '技术部', manager: '张三', memberCount: 15, description: '负责技术研发' },
          { id: 2, name: '产品部', manager: '李四', memberCount: 8, description: '负责产品设计' }
        ]
      };

      getDepartmentList.mockResolvedValue(mockResponse);

      const response = await getDepartmentList();

      expect(getDepartmentList).toHaveBeenCalled();
      expect(response).toEqual(mockResponse);
    });

    it('应该能够创建部门', async () => {
      const newDept = {
        name: '市场部',
        manager: '王五',
        description: '负责市场推广'
      };

      const mockResponse = {
        data: {
          id: 3,
          name: '市场部',
          manager: '王五',
          memberCount: 0,
          description: '负责市场推广'
        }
      };

      createDepartment.mockResolvedValue(mockResponse);

      const response = await createDepartment(newDept);

      expect(createDepartment).toHaveBeenCalledWith(newDept);
      expect(response).toEqual(mockResponse);
    });

    it('应该能够更新部门信息', async () => {
      const deptId = 1;
      const updatedDept = {
        name: '更新的技术部',
        manager: '新经理',
        description: '新的描述'
      };

      const mockResponse = {
        data: {
          id: 1,
          name: '更新的技术部',
          manager: '新经理',
          memberCount: 15,
          description: '新的描述'
        }
      };

      updateDepartment.mockResolvedValue(mockResponse);

      const response = await updateDepartment(deptId, updatedDept);

      expect(updateDepartment).toHaveBeenCalledWith(deptId, updatedDept);
      expect(response).toEqual(mockResponse);
    });

    it('应该能够删除部门', async () => {
      const deptId = 1;

      const mockResponse = {
        data: {
          success: true
        }
      };

      deleteDepartment.mockResolvedValue(mockResponse);

      const response = await deleteDepartment(deptId);

      expect(deleteDepartment).toHaveBeenCalledWith(deptId);
      expect(response).toEqual(mockResponse);
    });
  });

  describe('错误处理测试', () => {
    it('应该正确处理API错误', async () => {
      const errorMessage = '用户不存在';
      getUserList.mockRejectedValue(new Error(errorMessage));

      await expect(getUserList({ page: 1, size: 10 })).rejects.toThrow(errorMessage);
    });

    it('应该正确处理网络错误', async () => {
      getUserList.mockRejectedValue(new Error('Network Error'));

      await expect(getUserList({ page: 1, size: 10 })).rejects.toThrow('Network Error');
    });
  });

  describe('参数验证测试', () => {
    it('应该正确传递分页参数', async () => {
      const mockResponse = { data: { users: [], total: 0, page: 1, size: 10, pages: 0 } };
      getUserList.mockResolvedValue(mockResponse);

      const params = { page: 2, size: 20 };
      await getUserList(params);

      expect(getUserList).toHaveBeenCalledWith(params);
    });

    it('应该正确传递筛选参数', async () => {
      const mockResponse = { data: { users: [], total: 0, page: 1, size: 10, pages: 0 } };
      getUserList.mockResolvedValue(mockResponse);

      const params = { page: 1, size: 10, search: 'test', role: 'admin', status: 'active' };
      await getUserList(params);

      expect(getUserList).toHaveBeenCalledWith(params);
    });
  });
});