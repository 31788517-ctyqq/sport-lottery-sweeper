// AI_WORKING: coder1 @2026-01-29 - 创建存根文件以修复测试引用错误
// 管理员功能组合式函数（待实现）

import { ref, computed, watch } from 'vue';
import { adminAPI } from '@/api/modules/admin.js';

export function useAdmin() {
  const users = ref([]);
  const logs = ref([]);
  const stats = ref({});
  const loading = ref(false);
  const error = ref(null);
  
  // 获取用户列表
  const fetchUsers = async (params = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminAPI.getUsersList(params);
      users.value = response.items || [];
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch users:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 获取操作日志
  const fetchLogs = async (params = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminAPI.getOperationLogs(params);
      logs.value = response.items || [];
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch logs:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 获取统计信息
  const fetchStats = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminAPI.getStats();
      stats.value = response;
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch stats:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 更新用户状态
  const updateUserStatus = async (userId, status) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await adminAPI.updateUserStatus(userId, status);
      // 更新本地用户状态
      const userIndex = users.value.findIndex(user => user.id === userId);
      if (userIndex !== -1) {
        users.value[userIndex].status = status;
      }
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to update user status:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 计算属性
  const totalUsers = computed(() => users.value.length);
  const activeUsers = computed(() => users.value.filter(user => user.status === 'active').length);
  
  return {
    users,
    logs,
    stats,
    loading,
    error,
    fetchUsers,
    fetchLogs,
    fetchStats,
    updateUserStatus,
    totalUsers,
    activeUsers
  };
}