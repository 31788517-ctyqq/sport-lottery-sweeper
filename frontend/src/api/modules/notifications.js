/**
 * 通知相关API
 */
import client from '../client';

export const notificationsAPI = {
  /**
   * 获取当前用户的通知列表
   * @param {Object} params - 状态 (unread, read), 分页参数
   * @returns {Promise<Object>}
   */
  getNotifications(params = {}) {
    return client.get('/notifications', { params });
  },

  /**
   * 标记通知为已读
   * @param {number} id - 通知ID
   * @returns {Promise<Object>}
   */
  markAsRead(id) {
    return client.patch(`/notifications/${id}/read`);
  },

  /**
   * 标记所有通知为已读
   * @returns {Promise<Object>}
   */
  markAllAsRead() {
    return client.patch('/notifications/mark-all-read');
  },

  /**
   * 删除通知
   * @param {number} id - 通知ID
   * @returns {Promise<Object>}
   */
  deleteNotification(id) {
    return client.delete(`/notifications/${id}`);
  },
};

export const { getNotifications, markAsRead, markAllAsRead, deleteNotification } = notificationsAPI;