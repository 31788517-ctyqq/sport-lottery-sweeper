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

// ===== Compatibility Layer (Deprecated) =====
// Will be removed in 3 months
/** @deprecated Use getLotteryMatches instead */
export const getJczqMatches = getLotteryMatches;