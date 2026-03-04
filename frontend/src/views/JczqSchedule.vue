<template>
  <div class="lottery-schedule">
    <div class="lottery-schedule__header">
      <h1>⚽ 竞彩足球</h1>
      <p>近三天赛程数据 | 实时更新</p>
    </div>

    <div class="lottery-schedule__controls">
      <div class="lottery-schedule__control">
        <label>日期范围:</label>
        <select v-model="filters.days" @change="handleDaysChange">
          <option value="3">近3天</option>
          <option value="5">近5天</option>
          <option value="7">近7天</option>
        </select>
      </div>

      <div class="lottery-schedule__control">
        <label>联赛:</label>
        <select v-model="filters.league" @change="handleLeagueChange">
          <option value="">全部</option>
          <option v-for="league in leagues" :key="league.name" :value="league.name">
            {{ league.name }} ({{ league.match_count }})
          </option>
        </select>
      </div>

      <div class="lottery-schedule__control">
        <label>排序:</label>
        <select v-model="filters.sortBy" @change="handleSortChange">
          <option value="date">按时间</option>
          <option value="popularity">按热度</option>
          <option value="odds">按赔率</option>
        </select>
      </div>

      <button @click="refreshData" class="lottery-schedule__refresh-btn">🔄 刷新</button>
    </div>

    <div class="lottery-schedule__stats" v-if="stats">
      <div class="lottery-schedule__stat">
        <div class="lottery-schedule__stat-value">{{ stats.totalMatches }}</div>
        <div class="lottery-schedule__stat-label">总场数</div>
      </div>
      <div class="lottery-schedule__stat">
        <div class="lottery-schedule__stat-value">{{ stats.uniqueLeagues }}</div>
        <div class="lottery-schedule__stat-label">联赛数</div>
      </div>
      <div class="lottery-schedule__stat">
        <div class="lottery-schedule__stat-value">{{ stats.avgOdds.home }}</div>
        <div class="lottery-schedule__stat-label">平均主胜赔</div>
      </div>
      <div class="lottery-schedule__stat">
        <div class="lottery-schedule__stat-value">{{ stats.avgOdds.draw }}</div>
        <div class="lottery-schedule__stat-label">平均平赔</div>
      </div>
      <div class="lottery-schedule__stat">
        <div class="lottery-schedule__stat-value">{{ stats.avgOdds.away }}</div>
        <div class="lottery-schedule__stat-label">平均客胜赔</div>
      </div>
    </div>

    <div v-if="error" class="lottery-schedule__error">
      ⚠️ {{ error }}
    </div>

    <div v-if="loading" class="lottery-schedule__loading">
      <div class="lottery-schedule__spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="!matches || matches.length === 0" class="lottery-schedule__empty">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>
      <p>暂无比赛数据</p>
    </div>

    <div v-else class="lottery-schedule__matches">
      <div v-for="match in paginatedMatches" :key="match.id" class="lottery-schedule__match">
        <div class="lottery-schedule__match-header">
          <div class="lottery-schedule__match-time">
            📅 {{ formatDate(match.match_date) }}
          </div>
          <div class="lottery-schedule__match-league">
            <span class="lottery-schedule__league-badge">{{ match.league }}</span>
          </div>
        </div>
        <div class="lottery-schedule__match-teams">
          <div class="lottery-schedule__team">
            <div class="lottery-schedule__team-name">{{ match.home_team }}</div>
          </div>
          <div class="lottery-schedule__vs">VS</div>
          <div class="lottery-schedule__team">
            <div class="lottery-schedule__team-name">{{ match.away_team }}</div>
          </div>
          <div class="lottery-schedule__popularity">
            🔥 {{ match.popularity }}/100
          </div>
        </div>
        <div class="lottery-schedule__odds">
          <div class="lottery-schedule__odds-item">
            <div class="lottery-schedule__odds-label">{{ match.home_team }} 胜</div>
            <div class="lottery-schedule__odds-value">{{ match.odds_home_win }}</div>
          </div>
          <div class="lottery-schedule__odds-item">
            <div class="lottery-schedule__odds-label">平局</div>
            <div class="lottery-schedule__odds-value">{{ match.odds_draw }}</div>
          </div>
          <div class="lottery-schedule__odds-item">
            <div class="lottery-schedule__odds-label">{{ match.away_team }} 胜</div>
            <div class="lottery-schedule__odds-value">{{ match.odds_away_win }}</div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="totalPages > 1" class="lottery-schedule__pagination">
      <button 
        v-for="page in totalPages" 
        :key="page"
        :class="{ 'lottery-schedule__pagination-btn--active': page === currentPage }"
        class="lottery-schedule__pagination-btn"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { getMockData, getLotteryMatches } from '@/api/lottery';

export default {
  name: 'JczqSchedule',
  setup() {
    // 响应式数据
    const matches = ref([]);
    const leagues = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const currentPage = ref(1);
    const itemsPerPage = 10;

    // 过滤条件
    const filters = ref({
      days: 3,
      league: '',
      sortBy: 'date'
    });

    // 获取数据
    const fetchData = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        // 先尝试获取真实数据（从500彩票网）
        const params = {
          days: filters.value.days,
          sort_by: filters.value.sortBy,
          source: '500'  // 使用500彩票网作为数据源
        };
        
        if (filters.value.league) {
          params.league = filters.value.league;
        }

        const response = await getLotteryMatches(params);
        
        if (response.success && response.data && response.data.length > 0) {
          matches.value = response.data;
          console.log('✅ 成功获取比赛数据:', matches.value.length, '场');
        } else {
          // 如果没有数据，使用模拟数据
          console.warn('⚠️ API返回空数据，使用模拟数据');
          matches.value = await getMockData();
        }
        
        // 从比赛数据中提取联赛信息
        const uniqueLeagues = [...new Set(matches.value.map(m => m.league))];
        leagues.value = uniqueLeagues.map(league => ({
          name: league,
          match_count: matches.value.filter(m => m.league === league).length
        }));
        
      } catch (err) {
        error.value = `获取数据失败: ${err.message}`;
        console.error('❌ Error fetching data:', err);
        
        // 如果API调用失败，使用模拟数据
        try {
          console.warn('⚠️ 使用模拟数据作为后备');
          matches.value = await getMockData();
          
          // 提取联赛信息
          const uniqueLeagues = [...new Set(matches.value.map(m => m.league))];
          leagues.value = uniqueLeagues.map(league => ({
            name: league,
            match_count: matches.value.filter(m => m.league === league).length
          }));
        } catch (mockErr) {
          error.value = `获取模拟数据也失败: ${mockErr.message}`;
        }
      } finally {
        loading.value = false;
      }
    };

    // 计算统计信息
    const stats = computed(() => {
      if (!matches.value || matches.value.length === 0) {
        return null;
      }

      const uniqueLeagues = new Set(matches.value.map(m => m.league));
      const avgOdds = {
        home: (matches.value.reduce((sum, m) => sum + (m.odds_home_win || 0), 0) / matches.value.length || 0).toFixed(2),
        draw: (matches.value.reduce((sum, m) => sum + (m.odds_draw || 0), 0) / matches.value.length || 0).toFixed(2),
        away: (matches.value.reduce((sum, m) => sum + (m.odds_away_win || 0), 0) / matches.value.length || 0).toFixed(2)
      };

      return {
        totalMatches: matches.value.length,
        uniqueLeagues: uniqueLeagues.size,
        avgOdds
      };
    });

    // 分页计算
    const filteredMatches = computed(() => {
      if (!filters.value.league) return matches.value;
      return matches.value.filter(m => m.league === filters.value.league);
    });

    const totalPages = computed(() => {
      return Math.ceil(filteredMatches.value.length / itemsPerPage);
    });

    const paginatedMatches = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage;
      const end = start + itemsPerPage;
      return filteredMatches.value.slice(start, end);
    });

    // 方法
    const refreshData = () => {
      currentPage.value = 1;
      fetchData();
    };

    const handleDaysChange = () => {
      refreshData();
    };

    const handleLeagueChange = () => {
      currentPage.value = 1;
    };

    const handleSortChange = () => {
      refreshData();
    };

    const goToPage = (page) => {
      currentPage.value = page;
      window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const formatDate = (dateString) => {
      const date = new Date(dateString);
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      return `${month}-${day} ${hours}:${minutes}`;
    };

    // 组件挂载时初始化
    onMounted(() => {
      fetchData();
    });

    return {
      matches,
      leagues,
      loading,
      error,
      currentPage,
      filters,
      stats,
      totalPages,
      paginatedMatches,
      refreshData,
      handleDaysChange,
      handleLeagueChange,
      handleSortChange,
      goToPage,
      formatDate
    };
  }
};
</script>

<style scoped>
/* Lottery Schedule Component - BEM Naming Convention */

/* Block */
.lottery-schedule {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
}

/* Header */
.lottery-schedule__header {
  background: white;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.lottery-schedule__header h1 {
  color: #333;
  margin-bottom: 10px;
  font-size: 28px;
}

.lottery-schedule__header p {
  color: #666;
  font-size: 14px;
}

/* Controls */
.lottery-schedule__controls {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.lottery-schedule__control {
  display: flex;
  gap: 10px;
  align-items: center;
}

.lottery-schedule__control label {
  color: #333;
  font-weight: 600;
  min-width: 80px;
}

.lottery-schedule__control select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.lottery-schedule__control select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.lottery-schedule__refresh-btn {
  padding: 10px 20px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-left: auto;
}

.lottery-schedule__refresh-btn:hover {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

/* Stats */
.lottery-schedule__stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.lottery-schedule__stat {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
}

.lottery-schedule__stat-value {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.lottery-schedule__stat-label {
  font-size: 12px;
  opacity: 0.9;
}

/* Matches Container */
.lottery-schedule__matches {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Match Item */
.lottery-schedule__match {
  padding: 20px;
  border-bottom: 1px solid #eee;
  transition: background 0.3s ease;
  position: relative;
}

.lottery-schedule__match:hover {
  background: #f9f9f9;
}

.lottery-schedule__match:last-child {
  border-bottom: none;
}

.lottery-schedule__match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.lottery-schedule__match-time {
  color: #667eea;
  font-weight: bold;
  font-size: 16px;
  min-width: 180px;
}

.lottery-schedule__league-badge {
  background: #f0f0f0;
  color: #333;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.lottery-schedule__match-league {
  margin-left: auto;
}

/* Teams */
.lottery-schedule__match-teams {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
}

.lottery-schedule__team {
  flex: 1;
  text-align: center;
}

.lottery-schedule__team-name {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.lottery-schedule__vs {
  color: #999;
  font-weight: 600;
  min-width: 40px;
  text-align: center;
}

/* Odds */
.lottery-schedule__odds {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.lottery-schedule__odds-item {
  text-align: center;
  flex: 1;
}

.lottery-schedule__odds-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.lottery-schedule__odds-value {
  font-size: 20px;
  font-weight: bold;
  color: #667eea;
}

.lottery-schedule__popularity {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #ff6b6b;
}

/* Loading State */
.lottery-schedule__loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.lottery-schedule__spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: lottery-schedule-spin 1s linear infinite;
}

@keyframes lottery-schedule-spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error State */
.lottery-schedule__error {
  background: #fee;
  color: #c33;
  padding: 15px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* Empty State */
.lottery-schedule__empty {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.lottery-schedule__empty svg {
  width: 100px;
  height: 100px;
  margin-bottom: 20px;
  opacity: 0.5;
}

/* Pagination */
.lottery-schedule__pagination {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 30px;
  flex-wrap: wrap;
}

.lottery-schedule__pagination-btn {
  padding: 8px 16px;
  background: white;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.lottery-schedule__pagination-btn:hover {
  border-color: #667eea;
  color: #667eea;
}

.lottery-schedule__pagination-btn--active {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.lottery-schedule__pagination-btn:disabled {
  background: #ddd;
  cursor: not-allowed;
}

/* Responsive Design */
@media (max-width: 768px) {
  .lottery-schedule__header h1 {
    font-size: 20px;
  }

  .lottery-schedule__match-teams {
    gap: 10px;
  }

  .lottery-schedule__team-name {
    font-size: 14px;
  }

  .lottery-schedule__odds {
    flex-direction: column;
  }

  .lottery-schedule__controls {
    flex-direction: column;
  }

  .lottery-schedule__control {
    flex-direction: column;
    align-items: stretch;
  }

  .lottery-schedule__control label {
    min-width: unset;
  }

  .lottery-schedule__control select,
  .lottery-schedule__refresh-btn {
    width: 100%;
  }
}
</style>