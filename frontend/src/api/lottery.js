/**
 * 竞彩赛程管理 API
 * 用于管理员对赛程数据进行增、删、改、查及导入操作。
 */

import apiClient from './index';

/**
 * Get sports lottery match data
 * @param {Object} params - Query parameters
 * @param {number} params.days - Days range, default 3 days
 * @param {string} params.league - League filter
 * @param {string} params.sort_by - Sort by: date/popularity/odds
 * @param {string} params.source - Data source: 500/sporttery
 * @returns {Promise} Match data
 */
export const getLotteryMatches = async (params = {}) => {
  try {
    const response = await apiClient.get('/api/v1/lottery/matches', { params });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch lottery match data:', error);
    throw error;
  }
};

/**
 * Get Monday matches (from 500.com)
 * @returns {Promise} Monday match data
 */
export const getMondayMatches = async () => {
  try {
    const response = await apiClient.get('/api/v1/lottery/matches', {
      params: {
        source: '500',
        days: 1
      }
    });
    return response.data;
  } catch (error) {
    console.error('Failed to fetch Monday match data:', error);
    throw error;
  }
};

/**
 * Get mock data (for development testing)
 * @returns {Promise} Mock match data
 */
export const getMockData = async () => {
  // Return mock data
  return [
    {
      id: "mock_001",
      match_id: "周一001",
      league: "意甲",
      home_team: "克雷莫纳",
      away_team: "维罗纳",
      match_date: "2026-01-20T01:30:00",
      match_time: "01-20 01:30",
      odds_home_win: 2.50,
      odds_draw: 2.32,
      odds_away_win: 3.20,
      status: "scheduled",
      score: "-:-",
      popularity: 75,
      source: "模拟数据"
    }
  ];
};

// AI_WORKING: coder1 @2026-01-25T00:00:00 - 添加管理员赛程管理API别名导出，解决LotterySchedule.vue导入错误
// ===== Compatibility Layer (Deprecated) =====
// Will be removed in 3 months
/** @deprecated Use getLotteryMatches instead */
export const getJczqMatches = getLotteryMatches;

// ===== Admin Schedule Management API Aliases =====
// Import admin API functions
import { adminGetMatches, adminCreateMatch, adminUpdateMatch, adminDeleteMatch } from './modules/admin.js';

// Create aliases for LotterySchedule.vue compatibility
export const getLotterySchedules = adminGetMatches;
export const createLotterySchedule = adminCreateMatch;
export const updateLotterySchedule = adminUpdateMatch;
export const deleteLotterySchedule = adminDeleteMatch;

// Real import API implementations
// Auto import from crawler database
export const importLotterySchedulesAuto = async (params = {}) => {
  try {
    const response = await apiClient.post('/api/v1/admin/lottery-schedules/import/auto', params);
    return {
      code: 200,
      message: response.data.message || `成功导入 ${response.data.imported_count || 0} 条赛程数据`,
      data: response.data
    };
  } catch (error) {
    console.error('Auto import failed:', error);
    return {
      code: error.response?.status || 500,
      message: error.response?.data?.message || '自动导入失败',
      data: null
    };
  }
};

// Manual import from external API
export const importLotterySchedulesManual = async (params = {}) => {
  try {
    const response = await apiClient.post('/api/v1/admin/lottery-schedules/import/manual', params);
    return {
      code: 200,
      message: response.data.message || `成功从接口导入 ${response.data.imported_count || 0} 条赛程数据`,
      data: response.data
    };
  } catch (error) {
    console.error('Manual import failed:', error);
    return {
      code: error.response?.status || 500,
      message: error.response?.data?.message || '手动导入失败',
      data: null
    };
  }
};

// File import (CSV/Excel)
export const importLotterySchedulesFile = async (formData) => {
  try {
    const response = await apiClient.post('/api/v1/admin/lottery-schedules/import/file', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return {
      code: 200,
      message: response.data.message || `成功从文件导入 ${response.data.imported_count || 0} 条赛程数据`,
      data: response.data
    };
  } catch (error) {
    console.error('File import failed:', error);
    return {
      code: error.response?.status || 500,
      message: error.response?.data?.message || '文件导入失败',
      data: null
    };
  }
};
// AI_DONE: coder1 @2026-01-25T00:00:00