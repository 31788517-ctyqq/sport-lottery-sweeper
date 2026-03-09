<template>
  <div class="results-section-mobile">
    <!-- 结果头部 -->
    <div class="results-header-mobile">
      <div class="header-left">
        <span class="header-title">筛选结果</span>
        <span class="header-count" v-if="totalResults > 0">({{ totalResults }} 条)</span>
      </div>
      <div class="header-actions">
        <el-button size="small" @click="onExportResults('excel')" class="export-button">Excel</el-button>
        <el-button size="small" @click="onExportResults('csv')" class="export-button">CSV</el-button>
        <el-button size="small" @click="onToggleStats" class="stats-button">
          {{ showStats ? '隐藏统计' : '显示统计' }}
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-mobile">
      <i class="el-icon-loading"></i>
      <span>加载中...</span>
    </div>

    <!-- 结果卡片列表 -->
    <div v-else-if="pagedResults.length > 0" class="results-list-mobile">
      <div class="results-cards">
        <div
          class="match-card"
          v-for="match in pagedResults"
          :key="match.match_id"
          @click="onOpenAnalysis(match)"
        >
          <div class="card-header">
            <div class="match-id">#{{ formatMatchId(match.match_id) }}</div>
            <div class="match-time">{{ formatMatchTime(match.match_time) }}</div>
          </div>
          
          <div class="card-content">
            <div class="teams">
              <div class="team home-team">
                <span class="team-label">主</span>
                <span class="team-name">{{ displayValue(match.home_team) }}</span>
              </div>
              <div class="vs">vs</div>
              <div class="team away-team">
                <span class="team-label">客</span>
                <span class="team-name">{{ displayValue(match.away_team) }}</span>
              </div>
            </div>
            
            <div class="league">
              <i class="el-icon-trophy"></i>
              <span>{{ displayValue(match.league) }}</span>
            </div>
            
            <div class="indicators">
              <div class="indicator">
                <span class="indicator-label">ΔP</span>
                <span class="indicator-value">{{ displayValue(match.power_diff) }}</span>
              </div>
              <div class="indicator">
                <span class="indicator-label">ΔWP</span>
                <span class="indicator-value">{{ displayValue(match.delta_wp) }}</span>
              </div>
              <div class="indicator">
                <span class="indicator-label">P级</span>
                <el-tag v-if="match.p_level" :type="getPLevelTagType(match.p_level)" size="small" class="p-level-tag">
                  P{{ match.p_level }}
                </el-tag>
                <span v-else class="no-p-level">-</span>
              </div>
            </div>
            
            <div class="features">
              <div class="feature" v-if="match.home_feature">
                <span class="feature-label">主特征:</span>
                <span class="feature-value">{{ displayValue(match.home_feature) }}</span>
              </div>
              <div class="feature" v-if="match.away_feature">
                <span class="feature-label">客特征:</span>
                <span class="feature-value">{{ displayValue(match.away_feature) }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-actions">
            <el-button size="small" type="success" @click.stop="onOpenAnalysis(match)" class="analysis-button">
              分析
            </el-button>
          </div>
        </div>
      </div>

      <!-- 移动端分页 -->
      <div class="pagination-mobile">
        <div class="pagination-info">
          <span>第 {{ currentPage }} 页 / 共 {{ Math.ceil(totalResults / pageSize) }} 页</span>
          <span class="total-results">共 {{ totalResults }} 条</span>
        </div>
        <div class="pagination-controls">
          <el-button 
            size="small" 
            :disabled="currentPage <= 1" 
            @click="onHandleCurrentChange(currentPage - 1)"
            class="page-button prev-button"
          >
            上一页
          </el-button>
          <el-select 
            v-model="pageSize" 
            size="small" 
            @change="onHandleSizeChange"
            class="page-size-select"
          >
            <el-option
              v-for="size in [10, 20, 50]"
              :key="size"
              :label="`${size}条/页`"
              :value="size"
            />
          </el-select>
          <el-button 
            size="small" 
            :disabled="currentPage >= Math.ceil(totalResults / pageSize)" 
            @click="onHandleCurrentChange(currentPage + 1)"
            class="page-button next-button"
          >
            下一页
          </el-button>
        </div>
        <div class="load-more" v-if="totalResults > pagedResults.length">
          <el-button type="text" @click="onHandleCurrentChange(currentPage + 1)" class="load-more-button">
            加载更多
            <i class="el-icon-arrow-down"></i>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-results-mobile">
      <i class="el-icon-files"></i>
      <span>没有符合条件的比赛场次</span>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue';
import { ElButton, ElTag, ElSelect, ElOption } from 'element-plus';

export default defineComponent({
  name: 'ResultsSectionMobile',
  components: {
    ElButton,
    ElTag,
    ElSelect,
    ElOption
  },
  props: {
    pagedResults: {
      type: Array,
      required: true
    },
    loading: {
      type: Boolean,
      required: true
    },
    showStats: {
      type: Boolean,
      required: true
    },
    totalResults: {
      type: Number,
      required: true
    },
    currentPage: {
      type: Number,
      required: true
    },
    pageSize: {
      type: Number,
      required: true
    }
  },
  emits: [
    'toggleStats', 
    'exportResults', 
    'handleSortChange', 
    'handleSizeChange', 
    'handleCurrentChange', 
    'openAnalysis'
  ],
  setup(props, { emit }) {
    const formatMatchId = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      return String(value);
    };

    const formatMatchTime = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      const raw = String(value).trim();
      if (/^\d{4}-\d{2}-\d{2}$/.test(raw)) return raw;
      if (/^\d{4}-\d{2}-\d{2}[T\s]00:00:00(?:\.000)?(?:Z)?$/.test(raw)) {
        return raw.slice(0, 10);
      }
      const date = value instanceof Date ? value : new Date(value);
      if (Number.isNaN(date.getTime())) return String(value);
      const pad = (num) => String(num).padStart(2, '0');
      return `${date.getMonth() + 1}/${pad(date.getDate())} ${pad(date.getHours())}:${pad(date.getMinutes())}`;
    };

    const displayValue = (value) => {
      if (value === null || value === undefined || value === '') return '-';
      return value;
    };

    const getPLevelTagType = (level) => {
      switch (level) {
        case 1: return 'success'; // P1级用绿色
        case 2: return 'primary'; // P2级用蓝色
        case 3: return 'warning'; // P3级用黄色
        case 4: return 'danger';  // P4级用红色
        case 5: return 'info';    // P5级用灰色
        default: return 'info';
      }
    };

    const onToggleStats = () => {
      emit('toggleStats');
    };

    const onExportResults = (format) => {
      emit('exportResults', format);
    };

    const onHandleSortChange = (params) => {
      emit('handleSortChange', params);
    };

    const onHandleSizeChange = (size) => {
      emit('handleSizeChange', size);
    };

    const onHandleCurrentChange = (page) => {
      emit('handleCurrentChange', page);
    };

    const onOpenAnalysis = (row) => {
      emit('openAnalysis', row);
    };

    return {
      formatMatchId,
      formatMatchTime,
      displayValue,
      getPLevelTagType,
      onToggleStats,
      onExportResults,
      onHandleSortChange,
      onHandleSizeChange,
      onHandleCurrentChange,
      onOpenAnalysis
    };
  }
});
</script>

<style scoped>
.results-section-mobile {
  margin-top: 16px;
}

.results-header-mobile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background-color: #fdfcfb;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  margin-bottom: 16px;
  box-shadow: 0 6px 12px rgba(107, 103, 99, 0.08);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-title {
  font-weight: 600;
  color: #6b6763;
  font-size: 16px;
}

.header-count {
  font-size: 14px;
  color: #8b8680;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.export-button,
.stats-button {
  font-size: 13px;
  padding: 6px 12px;
  height: 32px;
  border-radius: 8px;
}

.loading-mobile {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 40px 20px;
  color: #8b8680;
  font-size: 15px;
}

.loading-mobile i {
  font-size: 20px;
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.results-list-mobile {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.results-cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.match-card {
  background-color: #fdfcfb;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 4px 8px rgba(107, 103, 99, 0.08);
  transition: transform 0.15s ease, box-shadow 0.2s ease;
}

.match-card:active {
  transform: translateY(1px);
  box-shadow: 0 2px 4px rgba(107, 103, 99, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e6e2db;
}

.match-id {
  font-weight: 600;
  color: #6b6763;
  font-size: 14px;
}

.match-time {
  font-size: 13px;
  color: #8b8680;
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  gap: 4px;
}

.team-label {
  font-size: 12px;
  color: #8b8680;
  font-weight: 600;
}

.team-name {
  font-weight: 600;
  color: #4c4743;
  font-size: 15px;
  text-align: center;
  word-break: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.vs {
  font-size: 12px;
  color: #8b8680;
  padding: 0 8px;
}

.league {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
  color: #8b8680;
}

.league i {
  font-size: 14px;
}

.indicators {
  display: flex;
  justify-content: space-around;
  gap: 8px;
  margin-top: 8px;
}

.indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.indicator-label {
  font-size: 12px;
  color: #8b8680;
}

.indicator-value {
  font-weight: 600;
  color: #4c4743;
  font-size: 14px;
}

.p-level-tag {
  font-size: 11px;
  padding: 2px 8px;
  min-height: 24px;
}

.no-p-level {
  font-size: 13px;
  color: #8b8680;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px dashed #e6e2db;
}

.feature {
  display: flex;
  gap: 6px;
  font-size: 12px;
}

.feature-label {
  color: #8b8680;
  font-weight: 600;
  white-space: nowrap;
}

.feature-value {
  color: #4c4743;
  word-break: break-word;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.card-actions {
  display: flex;
  justify-content: center;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e6e2db;
}

.analysis-button {
  width: 100%;
  height: 40px;
  font-size: 14px;
  border-radius: 8px;
}

.pagination-mobile {
  margin-top: 20px;
  padding: 16px;
  background-color: #f9f8f7;
  border: 1px solid #d6d2cb;
  border-radius: 12px;
}

.pagination-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #6b6763;
}

.total-results {
  font-weight: 600;
  color: #4c4743;
}

.pagination-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.page-button {
  flex: 1;
  height: 40px;
  font-size: 14px;
  border-radius: 8px;
}

.page-size-select {
  flex: 1;
}

.page-size-select :deep(.el-input__inner) {
  height: 40px;
  border-radius: 8px;
}

.load-more {
  text-align: center;
  padding-top: 12px;
  border-top: 1px dashed #d6d2cb;
}

.load-more-button {
  color: #8b8680;
  font-size: 14px;
}

.load-more-button i {
  margin-left: 4px;
}

.empty-results-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 48px 20px;
  background-color: #f9f8f7;
  border: 1px dashed #d6d2cb;
  border-radius: 12px;
  color: #8b8680;
  font-size: 15px;
}

.empty-results-mobile i {
  font-size: 40px;
  color: #c6bdb4;
}

/* 响应式调整 */
@media (max-width: 480px) {
  .results-header-mobile {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .export-button,
  .stats-button {
    flex: 1;
  }
  
  .teams {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .team {
    flex-direction: row;
    align-items: center;
    width: 100%;
    gap: 8px;
  }
  
  .team-label {
    min-width: 24px;
  }
  
  .team-name {
    text-align: left;
    flex: 1;
  }
  
  .vs {
    align-self: center;
    padding: 4px 0;
  }
  
  .indicators {
    flex-wrap: wrap;
  }
  
  .indicator {
    flex: 0 0 calc(50% - 8px);
  }
}

@media (max-width: 375px) {
  .match-card {
    padding: 12px;
  }
  
  .header-title {
    font-size: 15px;
  }
  
  .team-name {
    font-size: 14px;
  }
}
</style>
