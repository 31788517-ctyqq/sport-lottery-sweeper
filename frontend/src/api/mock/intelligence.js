/**
 * 模拟情报数据API
 */
export const mockIntelligenceAPI = {
  getIntelligenceReports(params = {}) {
    console.warn('[Mock API] Fetching intelligence reports with params:', params);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          success: true,
          data: {
            list: [
              { id: 1, title: '关于XX球员转会传闻的情报', category: '转会', priority: 'high', date: '2023-11-01' },
              { id: 2, title: 'YY俱乐部财务状况分析', category: '财务', priority: 'medium', date: '2023-11-03' },
            ],
            pagination: { page: params.page || 1, limit: params.limit || 10, total: 50 }
          },
          message: 'Success'
        });
      }, 500);
    });
  },
  // ... 其他mock方法
};