/**
 * 筛选选项API
 * 用于获取下拉框、多选框等所需的选项数据
 */
import client from '../client';

export const filtersAPI = {
  /**
   * 获取所有支持的体育项目
   * @returns {Promise<Array>} - [{ value: 'football', label: '足球' }, ...]
   */
  getSports() {
    return client.get('/filters/sports');
  },

  /**
   * 根据体育项目获取联赛列表
   * @param {string} sportCode - 体育项目代码
   * @returns {Promise<Array>} - [{ value: 'premier_league', label: '英超' }, ...]
   */
  getLeaguesBySport(sportCode) {
    return client.get(`/filters/leagues/${sportCode}`);
  },

  /**
   * 获取情报分类
   * @returns {Promise<Array>}
   */
  getIntelligenceCategories() {
    return client.get('/filters/intelligence/categories');
  },

  /**
   * 获取情报优先级
   * @returns {Promise<Array>}
   */
  getIntelligencePriorities() {
    return client.get('/filters/intelligence/priorities');
  },

  /**
   * 获取用户角色 (用于管理员界面)
   * @returns {Promise<Array>}
   */
  getUserRoles() {
    return client.get('/filters/user/roles');
  },
};

export const { getSports, getLeaguesBySport, getIntelligenceCategories, getIntelligencePriorities, getUserRoles } = filtersAPI;