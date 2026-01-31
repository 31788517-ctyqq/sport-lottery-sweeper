// AI_WORKING: coder1 @2026-01-29 - 创建存根文件以修复测试引用错误
// 比赛数据组合式函数（待实现）

import { ref, computed, watch } from 'vue';
import { matchesAPI } from '@/api/modules/matches.js';

export function useMatches() {
  const matches = ref([]);
  const loading = ref(false);
  const error = ref(null);
  const filters = ref({
    sport: '',
    league: '',
    dateRange: [],
    searchQuery: ''
  });
  
  // 获取比赛列表
  const fetchMatches = async (params = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await matchesAPI.getMatchesList(params);
      matches.value = response.items || [];
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch matches:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 获取比赛详情
  const fetchMatchDetail = async (id) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await matchesAPI.getMatchDetail(id);
      return response;
    } catch (err) {
      error.value = err;
      console.error('Failed to fetch match detail:', err);
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // 筛选比赛
  const filteredMatches = computed(() => {
    let result = matches.value;
    
    if (filters.value.sport) {
      result = result.filter(match => match.sport === filters.value.sport);
    }
    
    if (filters.value.league) {
      result = result.filter(match => match.league === filters.value.league);
    }
    
    if (filters.value.searchQuery) {
      const query = filters.value.searchQuery.toLowerCase();
      result = result.filter(match => 
        match.home_team.toLowerCase().includes(query) ||
        match.away_team.toLowerCase().includes(query) ||
        match.league_name.toLowerCase().includes(query)
      );
    }
    
    return result;
  });
  
  // 重置筛选器
  const resetFilters = () => {
    filters.value = {
      sport: '',
      league: '',
      dateRange: [],
      searchQuery: ''
    };
  };
  
  return {
    matches,
    loading,
    error,
    filters,
    fetchMatches,
    fetchMatchDetail,
    filteredMatches,
    resetFilters
  };
}