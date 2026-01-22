// frontend/src/store/modules/matches.js
import { defineStore } from 'pinia';

export const useMatchesStore = defineStore('matches', {
  state: () => ({
    matchesList: [],
    currentMatch: null, // 当前查看的比赛详情
    loading: false,
    error: null,
    pagination: {
      page: 1,
      pageSize: 10,
      total: 0,
    },
  }),

  getters: {
    // 获取当前页的数据
    currentPageMatches: (state) => {
      const start = (state.pagination.page - 1) * state.pagination.pageSize;
      const end = start + state.pagination.pageSize;
      return state.matchesList.slice(start, end);
    },
    // 获取当前比赛的对手信息
    currentMatchOpponents: (state) => {
      if (!state.currentMatch) return {};
      return {
        homeTeam: state.currentMatch.homeTeam,
        awayTeam: state.currentMatch.awayTeam,
      };
    }
  },

  actions: {
    // 获取比赛列表
    async fetchMatches(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        // 构建请求参数
        const queryParams = new URLSearchParams({
          page: params.page || this.pagination.page,
          pageSize: params.pageSize || this.pagination.pageSize,
          ...params.filters, // 假设有 filters 参数传递筛选条件
        }).toString();

        const response = await fetch(`/api/matches?${queryParams}`);
        if (!response.ok) throw new Error('获取比赛列表失败');

        const data = await response.json();
        this.matchesList = data.matches; // 假设 API 返回 { matches: [...], total: 100 }
        this.pagination.total = data.total;
        this.pagination.page = data.currentPage; // 假设 API 返回当前页

      } catch (error) {
        this.error = error.message;
        console.error('Fetch matches error:', error);
      } finally {
        this.loading = false;
      }
    },

    // 获取单个比赛详情
    async fetchMatchDetail(matchId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await fetch(`/api/matches/${matchId}`);
        if (!response.ok) throw new Error('获取比赛详情失败');

        const data = await response.json();
        this.currentMatch = data.match; // 假设 API 返回 { match: {...} }

      } catch (error) {
        this.error = error.message;
        console.error(`Fetch match ${matchId} detail error:`, error);
      } finally {
        this.loading = false;
      }
    },

    // 更新当前比赛数据 (例如比分变化)
    updateCurrentMatch(updates) {
      if (this.currentMatch) {
        this.currentMatch = { ...this.currentMatch, ...updates };
      }
    },

    // 清空当前比赛详情
    clearCurrentMatch() {
      this.currentMatch = null;
    }
  },
});