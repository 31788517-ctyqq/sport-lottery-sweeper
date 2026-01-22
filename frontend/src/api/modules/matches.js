/**
 * 比赛相关API
 */
import client from '../client';

export const matchesAPI = {
  /**
   * 获取比赛列表
   * @param {Object} params - 查询参数 (page, limit, sport, league, dateRange等)
   * @returns {Promise<Object>} - 包含分页信息和数据列表
   */
  getMatches(params = {}) {
    return client.get('/api/v1/matches', { params });
  },

  /**
   * 获取单个比赛详情
   * @param {number} id - 比赛ID
   * @returns {Promise<Object>}
   */
  getMatchById(id) {
    return client.get(`/api/v1/matches/${id}`);
  },

  /**
   * 获取比赛赔率
   * @param {number} id - 比赛ID
   * @returns {Promise<Object>}
   */
  getOddsByMatchId(id) {
    return client.get(`/api/v1/matches/${id}/odds`);
  },

  /**
   * 获取比赛统计数据
   * @param {number} id - 比赛ID
   * @returns {Promise<Object>}
   */
  getStatsByMatchId(id) {
    return client.get(`/api/v1/matches/${id}/stats`);
  },

  /**
   * 获取热门比赛
   * @returns {Promise<Array>}
   */
  getPopularMatches() {
    return client.get('/api/v1/matches/popular');
  },
};

export const { getMatches, getMatchById, getOddsByMatchId, getStatsByMatchId, getPopularMatches } = matchesAPI;