/**
 * 情报相关API
 */
import client from '../client';

export const intelligenceAPI = {
  /**
   * 获取情报列表
   * @param {Object} params - 查询参数 (page, limit, category, priority, keywords等)
   * @returns {Promise<Object>} - 包含分页信息和数据列表
   */
  getIntelligenceReports(params = {}) {
    return client.get('/intelligence', { params });
  },

  /**
   * 获取单个情报详情
   * @param {number} id - 情报ID
   * @returns {Promise<Object>}
   */
  getIntelligenceReportById(id) {
    return client.get(`/intelligence/${id}`);
  },

  /**
   * 获取热门情报
   * @returns {Promise<Array>}
   */
  getPopularIntelligence() {
    return client.get('/intelligence/popular');
  },

  /**
   * 提交新情报 (如果允许用户提交)
   * @param {Object} data - 情报数据
   * @returns {Promise<Object>}
   */
  submitIntelligence(data) {
    return client.post('/intelligence', data);
  },
};

export const { getIntelligenceReports, getIntelligenceReportById, getPopularIntelligence, submitIntelligence } = intelligenceAPI;