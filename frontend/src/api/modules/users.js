/**
 * 用户相关API (非认证流程)
 */
import client from '../client';

export const usersAPI = {
  /**
   * 获取用户列表 (通常仅限管理员)
   * @param {Object} params
   * @returns {Promise<Object>}
   */
  getUsers(params = {}) {
    return client.get('/users', { params });
  },

  /**
   * 获取单个用户信息
   * @param {number} id - 用户ID
   * @returns {Promise<Object>}
   */
  getUserById(id) {
    return client.get(`/users/${id}`);
  },

  /**
   * 更新用户信息 (可能包括角色、状态等)
   * @param {number} id - 用户ID
   * @param {Object} data - 要更新的数据
   * @returns {Promise<Object>}
   */
  updateUser(id, data) {
    return client.put(`/users/${id}`, data);
  },

  /**
   * 删除用户 (软删除或硬删除)
   * @param {number} id - 用户ID
   * @returns {Promise<Object>}
   */
  deleteUser(id) {
    return client.delete(`/users/${id}`);
  },
};

export const { getUsers, getUserById, updateUser, deleteUser } = usersAPI;