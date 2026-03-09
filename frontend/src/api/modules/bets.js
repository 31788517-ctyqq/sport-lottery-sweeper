// AI_WORKING: coder1 @2026-01-29 - 创建存根文件以修复测试引用错误
// 竞彩投注相关API模块（待实现）

export const betsAPI = {
  // 获取投注列表
  getBetsList(params) {
    console.warn('betsAPI.getBetsList is not implemented');
    return Promise.resolve({ items: [], total: 0 });
  },
  
  // 获取投注详情
  getBetDetail(id) {
    console.warn('betsAPI.getBetDetail is not implemented');
    return Promise.resolve({ id, status: 'pending' });
  },
  
  // 创建投注
  createBet(data) {
    console.warn('betsAPI.createBet is not implemented');
    return Promise.resolve({ id: Date.now(), ...data });
  },
  
  // 取消投注
  cancelBet(id) {
    console.warn('betsAPI.cancelBet is not implemented');
    return Promise.resolve({ success: true });
  },
  
  // 获取投注统计
  getBetStats() {
    console.warn('betsAPI.getBetStats is not implemented');
    return Promise.resolve({ total: 0, pending: 0, won: 0, lost: 0 });
  }
};

export default betsAPI;