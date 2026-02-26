/**
 * 认证相关API
 */
import client from '../client';

export const authAPI = {
  /**
   * 登录
   * @param {Object} credentials - 登录凭据 { username, password }
   * @returns {Promise<Object>} - 返回包含token的对象
   */
  login(credentials) {
    return client.post('/api/v1/login', credentials);
  },

  /**
   * 注册
   * @param {Object} userData - 用户注册信息
   * @returns {Promise<Object>}
   */
  register(userData) {
    return client.post('/api/register', userData);
  },

  /**
   * 刷新Token
   * @param {string} refreshToken - 刷新token
   * @returns {Promise<Object>}
   */
  refreshToken(refreshToken) {
    return client.post('/api/refresh', { refresh_token: refreshToken });
  },

  /**
   * 获取当前用户信息
   * @returns {Promise<Object>}
   */
  getCurrentUser() {
    return client.get('/api/me');
  },

  /**
   * 退出登录
   * @returns {Promise<Object>}
   */
  logout() {
    return client.post('/api/logout');
  },
};

// 为了方便解构导入
export const { login, register, refreshToken, getCurrentUser, logout } = authAPI;