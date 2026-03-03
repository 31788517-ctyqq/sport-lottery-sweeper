/**
 * 统计API
 */
import client from '../client';

export const statsAPI = {
  /**
   * 获取首页统计摘要
   * @returns {Promise<Object>} - { totalUsers, totalMatches, totalIntelligence, ... }
   */
  getSummaryStats() {
    return client.get('/api/v1/stats/data-center');
  },

  /**
   * 获取数据中心趋势图数据
   * @param {Object} params
   * @returns {Promise<Object>}
   */
  getDataCenterTrend(params = {}) {
    return client.get('/api/v1/stats/data-center/trend', { params });
  },

  /**
   * 获取数据源分布数据
   * @returns {Promise<Object>}
   */
  getDataCenterSourceDistribution() {
    return client.get('/api/v1/stats/data-center/source-distribution');
  },

  /**
   * 获取数据中心实时监控数据
   * @param {Object} params
   * @returns {Promise<Object>}
   */
  getDataCenterRealtime(params = {}) {
    return client.get('/api/v1/stats/data-center/realtime', { params });
  },


  /**
   * 获取比赛相关的图表数据
   * @param {Object} params - 时间范围等参数
   * @returns {Promise<Object>} - 图表所需的数据格式
   */
  getMatchChartStats(params = {}) {
    return client.get('/stats/matches/chart', { params });
  },

  /**
   * 获取情报相关的图表数据
   * @param {Object} params
   * @returns {Promise<Object>}
   */
  getIntelligenceChartStats(params = {}) {
    return client.get('/stats/intelligence/chart', { params });
  },

  /**
   * 获取用户行为统计 (例如登录次数、浏览量)
   * @param {Object} params
   * @returns {Promise<Object>}
   */
  getUserBehaviorStats(params = {}) {
    return client.get('/stats/users/behavior', { params });
  },
};

export const {
  getSummaryStats,
  getDataCenterTrend,
  getDataCenterSourceDistribution,
  getDataCenterRealtime,
  getMatchChartStats,
  getIntelligenceChartStats,
  getUserBehaviorStats
} = statsAPI;
