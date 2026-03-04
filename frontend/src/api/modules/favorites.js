/**
 * 收藏相关API
 */
import client from '../client';

export const favoritesAPI = {
  /**
   * 获取当前用户的收藏列表
   * @param {Object} params - 类型 (match, intelligence), 分页参数
   * @returns {Promise<Object>}
   */
  getFavorites(params = {}) {
    return client.get('/favorites', { params });
  },

  /**
   * 添加收藏
   * @param {Object} data - { type: 'match'|'intelligence', targetId: number }
   * @returns {Promise<Object>}
   */
  addFavorite(data) {
    return client.post('/favorites', data);
  },

  /**
   * 删除收藏
   * @param {number} id - 收藏记录ID
   * @returns {Promise<Object>}
   */
  removeFavorite(id) {
    return client.delete(`/favorites/${id}`);
  },

  /**
   * 检查是否已收藏某个目标
   * @param {Object} data - { type, targetId }
   * @returns {Promise<{ exists: boolean }>}
   */
  checkFavorite(data) {
    return client.post('/favorites/check', data);
  },
};

export const { getFavorites, addFavorite, removeFavorite, checkFavorite } = favoritesAPI;