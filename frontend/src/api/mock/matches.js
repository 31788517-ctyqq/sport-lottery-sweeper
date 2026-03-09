/**
 * 模拟比赛数据API
 * 当后端API不可用时，用于前端开发测试
 */
export const mockMatchesAPI = {
  getMatches(params = {}) {
    console.warn('[Mock API] Fetching matches with params:', params);
    // 模拟延迟
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            list: [
              { id: 1, name: 'AC米兰 vs 国际米兰', date: '2023-11-05', league: '意甲', status: 'finished' },
              { id: 2, name: '巴塞罗那 vs 皇家马德里', date: '2023-11-26', league: '西甲', status: 'upcoming' },
              { id: 3, name: '拜仁慕尼黑 vs 多特蒙德', date: '2023-11-11', league: '德甲', status: 'live' },
            ],
            pagination: { page: params.page || 1, limit: params.limit || 10, total: 100 }
          },
          message: 'Success'
        });
      }, 500);
    });
  },

  getMatchById(id) {
    console.warn(`[Mock API] Fetching match by ID: ${id}`);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          success: true,
          data: { id, name: '模拟比赛详情', odds: { home: 2.1, draw: 3.2, away: 3.0 } },
          message: 'Success'
        });
      }, 300);
    });
  },
  // ... 其他mock方法
};