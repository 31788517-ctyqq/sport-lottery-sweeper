// AI_WORKING: coder1 @2026-01-29 - 创建存根文件以修复测试引用错误
// 竞彩投注组合式函数（待实现）

import { ref, computed, watch } from 'vue';
import { betsAPI } from '@/api/modules/bets.js';

export function useBets() {
  const bets = ref([]);
  const loading = ref(false);
  const error = ref(null);
  
  // 获取投注列表
  const fetchBets = async (params = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await betsAPI.getBetsList(params);
      bets.value = response.items || [];
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch bets:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 创建投注
  const createBet = async (betData) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await betsAPI.createBet(betData);
      bets.value.push(response);
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to create bet:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 取消投注
  const cancelBet = async (id) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await betsAPI.cancelBet(id);
      bets.value = bets.value.filter(bet => bet.id !== id);
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to cancel bet:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 计算属性
  const totalBets = computed(() => bets.value.length);
  const pendingBets = computed(() => bets.value.filter(bet => bet.status === 'pending').length);
  
  return {
    bets,
    loading,
    error,
    fetchBets,
    createBet,
    cancelBet,
    totalBets,
    pendingBets
  };
}