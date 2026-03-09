<template>
  <div :class="panelClasses">
    <!-- 面板头部 -->
    <div v-if="showHeader" class="stats-panel__header">
      <div class="stats-panel__header-content">
        <h3 class="stats-panel__title">{{ title }}</h3>
        <div v-if="subtitle" class="stats-panel__subtitle">{{ subtitle }}</div>
      </div>
      
      <div class="stats-panel__header-actions">
        <!-- 时间范围选择器 -->
        <div v-if="showTimeRange" class="stats-panel__time-range">
          <BaseSelect
            v-model="selectedTimeRange"
            :options="timeRangeOptions"
            size="small"
            :clearable="false"
            @change="handleTimeRangeChange"
          />
        </div>
        
        <!-- 刷新按钮 -->
        <button
          v-if="showRefresh"
          class="stats-panel__refresh"
          @click="refreshData"
          :disabled="loading"
          aria-label="刷新数据"
        >
          <LoadingSpinner v-if="loading" size="small" />
          <svg v-else width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M17.65 6.35C16.2 4.9 14.21 4 12 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08c-.82 2.33-3.04 4-5.65 4-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/>
          </svg>
        </button>
        
        <!-- 更多操作 -->
        <div v-if="showMoreActions" class="stats-panel__more-actions">
          <BaseButton
            variant="outline"
            size="small"
            icon-right="more-vert"
            @click="showActionMenu = !showActionMenu"
          >
            操作
          </BaseButton>
        </div>
      </div>
    </div>

    <!-- 统计摘要 -->
    <div v-if="showSummary && statsSummary" class="stats-panel__summary">
      <div class="stats-panel__summary-grid">
        <div
          v-for="item in statsSummary"
          :key="item.id"
          :class="['stats-panel__summary-item', `stats-panel__summary-item--${item.type || 'default'}`]"
        >
          <StatsCard
            :title="item.title"
            :value="item.value"
            :change="item.change"
            :change-type="item.changeType"
            :icon="item.icon"
            :color="item.color"
            :loading="loading"
            compact
          />
        </div>
      </div>
    </div>

    <!-- 统计内容 -->
    <div class="stats-panel__content">
      <!-- 图表视图 -->
      <div v-if="showChart && chartData" class="stats-panel__chart">
        <StatsChart
          :data="chartData"
          :type="chartType"
          :options="chartOptions"
          :loading="loading"
          :height="chartHeight"
          @chart-click="handleChartClick"
        />
      </div>

      <!-- 网格布局 -->
      <div v-if="showGrid && gridItems" class="stats-panel__grid">
        <div class="stats-panel__grid-container">
          <div
            v-for="(item, index) in gridItems"
            :key="index"
            :class="[
              'stats-panel__grid-item',
              `stats-panel__grid-item--${item.span || 1}`,
              `stats-panel__grid-item--${item.type || 'default'}`
            ]"
          >
            <component
              v-if="item.component"
              :is="item.component"
              v-bind="item.props"
            />
            <StatsCard
              v-else-if="item.card"
              v-bind="item.card"
            />
            <StatsChart
              v-else-if="item.chart"
              v-bind="item.chart"
            />
            <StatsTrend
              v-else-if="item.trend"
              v-bind="item.trend"
            />
          </div>
        </div>
      </div>

      <!-- 列表视图 -->
      <div v-if="showList && listItems" class="stats-panel__list">
        <div class="stats-panel__list-container">
          <div
            v-for="(item, index) in listItems"
            :key="index"
            class="stats-panel__list-item"
          >
            <div class="stats-panel__list-item-content">
              <div class="stats-panel__list-item-title">{{ item.title }}</div>
              <div class="stats-panel__list-item-value">{{ item.value }}</div>
              <div v-if="item.change" :class="['stats-panel__list-item-change', `stats-panel__list-item-change--${item.changeType}`]">
                {{ formatChange(item.change, item.changeType) }}
              </div>
            </div>
            <div v-if="item.trend" class="stats-panel__list-item-trend">
              <StatsTrend
                :data="item.trend.data"
                :type="item.trend.type || 'line'"
                :height="40"
                :width="100"
                hide-axes
                hide-legend
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 表格视图 -->
      <div v-if="showTable && tableData" class="stats-panel__table">
        <table class="stats-panel__table-container">
          <thead>
            <tr>
              <th v-for="column in tableColumns" :key="column.key" class="stats-panel__table-header">
                {{ column.title }}
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableData" :key="row.id" class="stats-panel__table-row">
              <td v-for="column in tableColumns" :key="column.key" class="stats-panel__table-cell">
                <template v-if="column.type === 'trend'">
                  <StatsTrend
                    v-if="row[column.key]"
                    :data="row[column.key]"
                    :type="column.trendType || 'line'"
                    :height="30"
                    :width="80"
                    hide-axes
                    hide-legend
                  />
                </template>
                <template v-else-if="column.type === 'change'">
                  <span :class="['stats-panel__table-change', `stats-panel__table-change--${getChangeType(row[column.key])}`]">
                    {{ formatChange(row[column.key]) }}
                  </span>
                </template>
                <template v-else>
                  {{ row[column.key] }}
                </template>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 面板底部 -->
    <div v-if="showFooter" class="stats-panel__footer">
      <div class="stats-panel__footer-left">
        <!-- 数据来源 -->
        <div v-if="dataSource" class="stats-panel__source">
          <span class="stats-panel__source-label">数据来源:</span>
          <span class="stats-panel__source-name">{{ dataSource }}</span>
        </div>
        
        <!-- 最后更新时间 -->
        <div v-if="lastUpdated" class="stats-panel__updated">
          最后更新: {{ formatTime(lastUpdated) }}
        </div>
      </div>
      
      <div class="stats-panel__footer-right">
        <!-- 查看更多 -->
        <BaseButton
          v-if="showViewMore"
          variant="outline"
          size="small"
          @click="$emit('view-more')"
        >
          查看更多
        </BaseButton>
        
        <!-- 导出按钮 -->
        <BaseButton
          v-if="showExport"
          variant="outline"
          size="small"
          @click="$emit('export')"
        >
          导出数据
        </BaseButton>
      </div>
    </div>

    <!-- 操作菜单 -->
    <div v-if="showActionMenu" class="stats-panel__action-menu">
      <div class="stats-panel__action-menu-content">
        <button class="stats-panel__action-menu-item" @click="$emit('export')">
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
          导出数据
        </button>
        <button class="stats-panel__action-menu-item" @click="$emit('print')">
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/>
          </svg>
          打印
        </button>
        <button class="stats-panel__action-menu-item" @click="$emit('share')">
          <svg width="16" height="16" viewBox="0 0 24 24">
            <path fill="currentColor" d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92 1.61 0 2.92-1.31 2.92-2.92s-1.31-2.92-2.92-2.92z"/>
          </svg>
          分享
        </button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading && showLoading" class="stats-panel__loading">
      <LoadingSpinner size="large" text="加载统计数据..." />
    </div>

    <!-- 空状态 -->
    <div v-if="showEmptyState && !hasData" class="stats-panel__empty">
      <EmptyState
        :title="emptyTitle"
        :description="emptyDescription"
        icon="📊"
        variant="compact"
        :action-text="emptyActionText"
        @action="$emit('refresh')"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseSelect from '../common/BaseSelect.vue'
import BaseButton from '../common/BaseButton.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import EmptyState from '../common/EmptyState.vue'
import StatsCard from './StatsCard.vue'
import StatsChart from './StatsChart.vue'
import StatsTrend from './StatsTrend.vue'
import { formatTime } from '@/utils/date'

const props = defineProps({
  title: {
    type: String,
    default: '统计面板'
  },
  subtitle: {
    type: String,
    default: ''
  },
  layout: {
    type: String,
    default: 'chart', // 'chart', 'grid', 'list', 'table', 'summary'
    validator: (value) => ['chart', 'grid', 'list', 'table', 'summary'].includes(value)
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showSummary: {
    type: Boolean,
    default: true
  },
  showChart: {
    type: Boolean,
    default: true
  },
  showGrid: {
    type: Boolean,
    default: false
  },
  showList: {
    type: Boolean,
    default: false
  },
  showTable: {
    type: Boolean,
    default: false
  },
  showTimeRange: {
    type: Boolean,
    default: true
  },
  showRefresh: {
    type: Boolean,
    default: true
  },
  showMoreActions: {
    type: Boolean,
    default: false
  },
  showViewMore: {
    type: Boolean,
    default: false
  },
  showExport: {
    type: Boolean,
    default: false
  },
  showLoading: {
    type: Boolean,
    default: true
  },
  showEmptyState: {
    type: Boolean,
    default: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  statsSummary: {
    type: Array,
    default: () => []
  },
  chartData: {
    type: [Array, Object],
    default: null
  },
  chartType: {
    type: String,
    default: 'line' // 'line', 'bar', 'pie', 'area', 'radar', 'heatmap'
  },
  chartOptions: {
    type: Object,
    default: () => ({})
  },
  chartHeight: {
    type: [Number, String],
    default: 300
  },
  gridItems: {
    type: Array,
    default: null
  },
  listItems: {
    type: Array,
    default: null
  },
  tableData: {
    type: Array,
    default: null
  },
  tableColumns: {
    type: Array,
    default: () => []
  },
  dataSource: {
    type: String,
    default: ''
  },
  lastUpdated: {
    type: [String, Date],
    default: ''
  },
  emptyTitle: {
    type: String,
    default: '暂无统计数据'
  },
  emptyDescription: {
    type: String,
    default: '当前暂无统计数据，请稍后再试'
  },
  emptyActionText: {
    type: String,
    default: '刷新数据'
  },
  timeRangeOptions: {
    type: Array,
    default: () => [
      { value: 'today', label: '今天' },
      { value: 'yesterday', label: '昨天' },
      { value: '7days', label: '近7天' },
      { value: '30days', label: '近30天' },
      { value: '90days', label: '近90天' },
      { value: 'custom', label: '自定义' }
    ]
  },
  defaultTimeRange: {
    type: String,
    default: '7days'
  },
  compact: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'time-range-change',
  'refresh',
  'chart-click',
  'view-more',
  'export',
  'print',
  'share'
])

// 响应式状态
const selectedTimeRange = ref(props.defaultTimeRange)
const showActionMenu = ref(false)

// 计算属性
const panelClasses = computed(() => ({
  'stats-panel': true,
  'stats-panel--compact': props.compact,
  'stats-panel--loading': props.loading,
  'stats-panel--empty': !hasData.value,
  [`stats-panel--layout-${props.layout}`]: true
}))

const hasData = computed(() => {
  if (props.showChart && props.chartData) return true
  if (props.showGrid && props.gridItems && props.gridItems.length > 0) return true
  if (props.showList && props.listItems && props.listItems.length > 0) return true
  if (props.showTable && props.tableData && props.tableData.length > 0) return true
  if (props.showSummary && props.statsSummary && props.statsSummary.length > 0) return true
  return false
})

// 方法
const handleTimeRangeChange = (value) => {
  selectedTimeRange.value = value
  emit('time-range-change', value)
}

const refreshData = () => {
  emit('refresh')
}

const handleChartClick = (params) => {
  emit('chart-click', params)
}

const formatChange = (change, changeType) => {
  if (change === null || change === undefined) return ''
  
  const prefix = change > 0 ? '+' : ''
  const suffix = changeType === 'percent' ? '%' : ''
  return `${prefix}${change}${suffix}`
}

const getChangeType = (value) => {
  if (value === null || value === undefined) return 'neutral'
  return value > 0 ? 'positive' : value < 0 ? 'negative' : 'neutral'
}
</script>

<style scoped>
.stats-panel {
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  position: relative;
}

.stats-panel--compact {
  border-radius: var(--radius-md);
}

.stats-panel--loading {
  opacity: 0.7;
}

.stats-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-5) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.stats-panel--compact .stats-panel__header {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__header-content {
  flex: 1;
  min-width: 0;
}

.stats-panel__title {
  margin: 0;
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.stats-panel__subtitle {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-panel__header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-shrink: 0;
}

.stats-panel__time-range {
  min-width: 120px;
}

.stats-panel__refresh {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: none;
  border-radius: var(--radius-full);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.stats-panel__refresh:hover:not(:disabled) {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

.stats-panel__refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.stats-panel__summary {
  padding: var(--spacing-5) var(--spacing-6);
  border-bottom: 1px solid var(--color-border-light);
}

.stats-panel--compact .stats-panel__summary {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.stats-panel--compact .stats-panel__summary-grid {
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-3);
}

.stats-panel__content {
  flex: 1;
  overflow: hidden;
}

.stats-panel__chart {
  padding: var(--spacing-5) var(--spacing-6);
}

.stats-panel--compact .stats-panel__chart {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__grid {
  padding: var(--spacing-5) var(--spacing-6);
}

.stats-panel--compact .stats-panel__grid {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__grid-container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-4);
}

.stats-panel__grid-item {
  grid-column: span 12;
}

.stats-panel__grid-item--2 {
  grid-column: span 6;
}

.stats-panel__grid-item--3 {
  grid-column: span 4;
}

.stats-panel__grid-item--4 {
  grid-column: span 3;
}

.stats-panel__grid-item--6 {
  grid-column: span 2;
}

.stats-panel__list {
  padding: var(--spacing-5) var(--spacing-6);
}

.stats-panel--compact .stats-panel__list {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__list-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.stats-panel__list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3) var(--spacing-4);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  transition: all 0.2s ease;
}

.stats-panel__list-item:hover {
  background-color: var(--color-bg-tertiary);
}

.stats-panel__list-item-content {
  flex: 1;
  min-width: 0;
}

.stats-panel__list-item-title {
  font-size: var(--font-size-sm);
  color: var(--color-text-primary);
  font-weight: 500;
  margin-bottom: 2px;
}

.stats-panel__list-item-value {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-primary);
}

.stats-panel__list-item-change {
  font-size: var(--font-size-xs);
  font-weight: 600;
  margin-top: 2px;
}

.stats-panel__list-item-change--positive {
  color: var(--color-success);
}

.stats-panel__list-item-change--negative {
  color: var(--color-danger);
}

.stats-panel__list-item-change--neutral {
  color: var(--color-text-secondary);
}

.stats-panel__list-item-trend {
  flex-shrink: 0;
  margin-left: var(--spacing-4);
}

.stats-panel__table {
  padding: var(--spacing-5) var(--spacing-6);
  overflow-x: auto;
}

.stats-panel--compact .stats-panel__table {
  padding: var(--spacing-4) var(--spacing-5);
}

.stats-panel__table-container {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.stats-panel__table-header {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  font-weight: 600;
  color: var(--color-text-secondary);
  border-bottom: 2px solid var(--color-border);
  white-space: nowrap;
}

.stats-panel__table-row {
  border-bottom: 1px solid var(--color-border-light);
  transition: background-color 0.2s ease;
}

.stats-panel__table-row:hover {
  background-color: var(--color-bg-secondary);
}

.stats-panel__table-cell {
  padding: var(--spacing-3) var(--spacing-4);
  text-align: left;
  color: var(--color-text-primary);
  white-space: nowrap;
}

.stats-panel__table-change {
  font-weight: 600;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
}

.stats-panel__table-change--positive {
  color: var(--color-success);
  background-color: var(--color-success-light);
}

.stats-panel__table-change--negative {
  color: var(--color-danger);
  background-color: var(--color-danger-light);
}

.stats-panel__table-change--neutral {
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
}

.stats-panel__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-4) var(--spacing-6);
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
}

.stats-panel--compact .stats-panel__footer {
  padding: var(--spacing-3) var(--spacing-5);
}

.stats-panel__footer-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  flex: 1;
  min-width: 0;
}

.stats-panel__source,
.stats-panel__updated {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stats-panel__source-label {
  margin-right: var(--spacing-1);
}

.stats-panel__source-name {
  font-weight: 600;
}

.stats-panel__footer-right {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
  flex-shrink: 0;
}

.stats-panel__action-menu {
  position: absolute;
  top: 60px;
  right: 20px;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  z-index: 100;
  min-width: 160px;
}

.stats-panel__action-menu-content {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-2) 0;
}

.stats-panel__action-menu-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-4);
  background: transparent;
  border: none;
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
}

.stats-panel__action-menu-item:hover {
  background-color: var(--color-bg-secondary);
}

.stats-panel__loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.stats-panel__empty {
  padding: var(--spacing-12) var(--spacing-6);
  text-align: center;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-panel__header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-3);
  }
  
  .stats-panel__header-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .stats-panel__summary-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-panel__grid-container {
    grid-template-columns: 1fr;
  }
  
  .stats-panel__grid-item {
    grid-column: span 1;
  }
  
  .stats-panel__footer {
    flex-direction: column;
    gap: var(--spacing-3);
    align-items: flex-start;
  }
  
  .stats-panel__footer-right {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>