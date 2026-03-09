<template>
  <div :class="statsClasses">
    <!-- 标题 -->
    <div v-if="showTitle" class="match-stats__header">
      <h4 class="match-stats__title">比赛统计</h4>
      <div v-if="lastUpdated" class="match-stats__updated">
        更新于 {{ formatTime(lastUpdated) }}
      </div>
    </div>

    <!-- 统计类型标签 -->
    <div v-if="showStatsTypeTabs" class="match-stats__tabs">
      <button
        v-for="tab in statsTypeTabs"
        :key="tab.value"
        :class="['match-stats__tab', { 'match-stats__tab--active': activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 统计摘要（柱状图） -->
    <div v-if="showSummary && statsData.length > 0" class="match-stats__summary">
      <div class="match-stats__summary-grid">
        <div
          v-for="stat in statsData"
          :key="stat.key"
          class="match-stats__summary-item"
        >
          <div class="match-stats__stat-label">{{ stat.label }}</div>
          <div class="match-stats__stat-bars">
            <!-- 主队柱状图 -->
            <div class="match-stats__bar-container">
              <div
                class="match-stats__bar match-stats__bar--home"
                :style="{ width: calculateBarWidth(stat.homeValue, stat.total) }"
              ></div>
              <span class="match-stats__bar-value match-stats__bar-value--home">
                {{ formatStatValue(stat.homeValue, stat.unit) }}
              </span>
            </div>
            
            <!-- 客队柱状图 -->
            <div class="match-stats__bar-container">
              <div
                class="match-stats__bar match-stats__bar--away"
                :style="{ width: calculateBarWidth(stat.awayValue, stat.total) }"
              ></div>
              <span class="match-stats__bar-value match-stats__bar-value--away">
                {{ formatStatValue(stat.awayValue, stat.unit) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详细统计表格 -->
    <div v-if="showDetailed && detailedStats.length > 0" class="match-stats__detailed">
      <table class="match-stats__table">
        <thead>
          <tr>
            <th class="match-stats__table-header match-stats__table-header--stat">统计项</th>
            <th class="match-stats__table-header match-stats__table-header--home">主队</th>
            <th class="match-stats__table-header match-stats__table-header--away">客队</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="stat in detailedStats"
            :key="stat.key"
            class="match-stats__table-row"
          >
            <td class="match-stats__table-cell match-stats__table-cell--stat">
              <span class="match-stats__table-label">{{ stat.label }}</span>
              <span v-if="stat.description" class="match-stats__table-description">
                {{ stat.description }}
              </span>
            </td>
            <td class="match-stats__table-cell match-stats__table-cell--home">
              <span class="match-stats__table-value">{{ formatStatValue(stat.homeValue, stat.unit) }}</span>
              <span v-if="stat.homePercentage" class="match-stats__table-percentage">
                {{ stat.homePercentage }}%
              </span>
            </td>
            <td class="match-stats__table-cell match-stats__table-cell--away">
              <span class="match-stats__table-value">{{ formatStatValue(stat.awayValue, stat.unit) }}</span>
              <span v-if="stat.awayPercentage" class="match-stats__table-percentage">
                {{ stat.awayPercentage }}%
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 高级统计（图表） -->
    <div v-if="showAdvanced && advancedStats" class="match-stats__advanced">
      <div class="match-stats__advanced-section">
        <div class="match-stats__advanced-title">控球率</div>
        <div class="match-stats__possession-chart">
          <div class="match-stats__possession-home">
            <div
              class="match-stats__possession-bar match-stats__possession-bar--home"
              :style="{ width: possessionPercentage.home + '%' }"
            ></div>
            <span class="match-stats__possession-value">
              {{ possessionPercentage.home }}%
            </span>
          </div>
          <div class="match-stats__possession-away">
            <div
              class="match-stats__possession-bar match-stats__possession-bar--away"
              :style="{ width: possessionPercentage.away + '%' }"
            ></div>
            <span class="match-stats__possession-value">
              {{ possessionPercentage.away }}%
            </span>
          </div>
        </div>
      </div>

      <div v-if="shotsData" class="match-stats__advanced-section">
        <div class="match-stats__advanced-title">射门分布</div>
        <div class="match-stats__shots-chart">
          <div class="match-stats__shots-home">
            <div class="match-stats__shots-total">
              总射门: {{ shotsData.home.total }}
            </div>
            <div class="match-stats__shots-on-target">
              射正: {{ shotsData.home.onTarget }}
            </div>
            <div class="match-stats__shots-off-target">
              射偏: {{ shotsData.home.offTarget }}
            </div>
            <div class="match-stats__shots-blocked">
              被封堵: {{ shotsData.home.blocked }}
            </div>
          </div>
          <div class="match-stats__shots-away">
            <div class="match-stats__shots-total">
              总射门: {{ shotsData.away.total }}
            </div>
            <div class="match-stats__shots-on-target">
              射正: {{ shotsData.away.onTarget }}
            </div>
            <div class="match-stats__shots-off-target">
              射偏: {{ shotsData.away.offTarget }}
            </div>
            <div class="match-stats__shots-blocked">
              被封堵: {{ shotsData.away.blocked }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无统计数据 -->
    <div v-if="showEmptyState && !hasStatsData" class="match-stats__empty">
      <EmptyState
        title="暂无统计数据"
        description="当前比赛暂无统计信息"
        icon="📊"
        variant="compact"
      />
    </div>

    <!-- 数据来源 -->
    <div v-if="showDataSource && dataSource" class="match-stats__source">
      <span class="match-stats__source-label">数据来源:</span>
      <span class="match-stats__source-name">{{ dataSource }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EmptyState from '../common/EmptyState.vue'
import { formatTime } from '@/utils/date'

const props = defineProps({
  stats: {
    type: Object,
    default: () => ({})
  },
  type: {
    type: String,
    default: 'summary',
    validator: (value) => ['summary', 'detailed', 'advanced', 'all'].includes(value)
  },
  show: {
    type: Array,
    default: () => ['possession', 'shots', 'corners', 'fouls', 'yellowCards', 'redCards']
  },
  compact: {
    type: Boolean,
    default: false
  },
  showTitle: {
    type: Boolean,
    default: true
  },
  showStatsTypeTabs: {
    type: Boolean,
    default: false
  },
  showDataSource: {
    type: Boolean,
    default: false
  },
  showEmptyState: {
    type: Boolean,
    default: true
  },
  lastUpdated: {
    type: [String, Date],
    default: ''
  },
  dataSource: {
    type: String,
    default: ''
  }
})

const activeTab = ref(props.type)

// 统计类型定义
const statDefinitions = {
  possession: { label: '控球率', unit: '%', type: 'percentage', max: 100 },
  shots: { label: '射门', unit: '次', type: 'count', max: null },
  shotsOnTarget: { label: '射正', unit: '次', type: 'count', max: null },
  shotsOffTarget: { label: '射偏', unit: '次', type: 'count', max: null },
  shotsBlocked: { label: '被封堵', unit: '次', type: 'count', max: null },
  corners: { label: '角球', unit: '个', type: 'count', max: null },
  fouls: { label: '犯规', unit: '次', type: 'count', max: null },
  yellowCards: { label: '黄牌', unit: '张', type: 'count', max: null },
  redCards: { label: '红牌', unit: '张', type: 'count', max: null },
  offsides: { label: '越位', unit: '次', type: 'count', max: null },
  passes: { label: '传球', unit: '次', type: 'count', max: null },
  passAccuracy: { label: '传球成功率', unit: '%', type: 'percentage', max: 100 },
  tackles: { label: '抢断', unit: '次', type: 'count', max: null },
  interceptions: { label: '拦截', unit: '次', type: 'count', max: null },
  clearances: { label: '解围', unit: '次', type: 'count', max: null },
  saves: { label: '扑救', unit: '次', type: 'count', max: null }
}

// 计算属性
const statsClasses = computed(() => ({
  'match-stats': true,
  'match-stats--compact': props.compact,
  'match-stats--summary': props.type === 'summary',
  'match-stats--detailed': props.type === 'detailed',
  'match-stats--advanced': props.type === 'advanced',
  'match-stats--all': props.type === 'all'
}))

const statsTypeTabs = computed(() => [
  { value: 'summary', label: '摘要' },
  { value: 'detailed', label: '详细' },
  { value: 'advanced', label: '高级' }
])

const statsData = computed(() => {
  const result = []
  
  props.show.forEach(key => {
    const definition = statDefinitions[key]
    if (definition && props.stats[key]) {
      const homeValue = props.stats[key].home || props.stats[key].homeValue || 0
      const awayValue = props.stats[key].away || props.stats[key].awayValue || 0
      const total = homeValue + awayValue
      
      result.push({
        key,
        label: definition.label,
        unit: definition.unit,
        homeValue,
        awayValue,
        total: total || 1 // 避免除以0
      })
    }
  })
  
  return result
})

const detailedStats = computed(() => {
  return Object.entries(props.stats)
    .filter(([key, value]) => value !== null && value !== undefined)
    .map(([key, value]) => {
      const definition = statDefinitions[key] || { label: key, unit: '', type: 'count' }
      const homeValue = value.home || value.homeValue || 0
      const awayValue = value.away || value.awayValue || 0
      const total = homeValue + awayValue
      const homePercentage = definition.type === 'percentage' ? homeValue : 
                           total > 0 ? Math.round((homeValue / total) * 100) : 0
      const awayPercentage = definition.type === 'percentage' ? awayValue : 
                           total > 0 ? Math.round((awayValue / total) * 100) : 0
      
      return {
        key,
        label: definition.label,
        description: definition.description,
        unit: definition.unit,
        homeValue,
        awayValue,
        homePercentage: definition.type === 'percentage' || definition.unit === '%' ? homeValue : homePercentage,
        awayPercentage: definition.type === 'percentage' || definition.unit === '%' ? awayValue : awayPercentage
      }
    })
})

const advancedStats = computed(() => {
  return props.type === 'advanced' || props.type === 'all'
})

const possessionPercentage = computed(() => {
  const possession = props.stats.possession || {}
  return {
    home: possession.home || possession.homeValue || 50,
    away: possession.away || possession.awayValue || 50
  }
})

const shotsData = computed(() => {
  if (!props.stats.shots) return null
  
  return {
    home: {
      total: props.stats.shots.home || props.stats.shots.homeValue || 0,
      onTarget: props.stats.shotsOnTarget?.home || 0,
      offTarget: props.stats.shotsOffTarget?.home || 0,
      blocked: props.stats.shotsBlocked?.home || 0
    },
    away: {
      total: props.stats.shots.away || props.stats.shots.awayValue || 0,
      onTarget: props.stats.shotsOnTarget?.away || 0,
      offTarget: props.stats.shotsOffTarget?.away || 0,
      blocked: props.stats.shotsBlocked?.away || 0
    }
  }
})

const hasStatsData = computed(() => {
  return statsData.value.length > 0 || detailedStats.value.length > 0
})

const showSummary = computed(() => {
  return props.type === 'summary' || props.type === 'all'
})

const showDetailed = computed(() => {
  return props.type === 'detailed' || props.type === 'all'
})

const showAdvanced = computed(() => {
  return props.type === 'advanced' || props.type === 'all'
})

// 方法
const calculateBarWidth = (value, total) => {
  if (!total) return '0%'
  const percentage = (value / total) * 100
  return `${Math.min(percentage, 100)}%`
}

const formatStatValue = (value, unit) => {
  if (value === null || value === undefined) return '0'
  
  if (unit === '%') {
    return `${value}${unit}`
  }
  
  const num = parseFloat(value)
  if (isNaN(num)) return value.toString()
  
  // 如果是整数，不显示小数
  return num % 1 === 0 ? num.toString() + (unit || '') : num.toFixed(1) + (unit || '')
}
</script>

<style scoped>
.match-stats {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.match-stats--compact {
  gap: var(--spacing-3);
}

.match-stats__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2);
}

.match-stats__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-stats__updated {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-stats__tabs {
  display: flex;
  gap: var(--spacing-1);
  background-color: var(--color-bg-tertiary);
  padding: var(--spacing-1);
  border-radius: var(--radius-md);
}

.match-stats__tab {
  flex: 1;
  padding: var(--spacing-2) var(--spacing-3);
  border: none;
  background: transparent;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  text-align: center;
}

.match-stats__tab:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.match-stats__tab--active {
  background-color: var(--color-bg-card);
  color: var(--color-text-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.match-stats__summary {
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
}

.match-stats--compact .match-stats__summary {
  padding: var(--spacing-3);
}

.match-stats__summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-4);
}

.match-stats--compact .match-stats__summary-grid {
  grid-template-columns: 1fr;
  gap: var(--spacing-3);
}

.match-stats__summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.match-stats__stat-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  text-align: center;
}

.match-stats__stat-bars {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
}

.match-stats--compact .match-stats__stat-bars {
  gap: var(--spacing-2);
}

.match-stats__bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
  min-height: 24px;
}

.match-stats__bar {
  height: 8px;
  border-radius: var(--radius-full);
  min-width: 4px;
  transition: width 0.5s ease;
}

.match-stats__bar--home {
  background-color: var(--color-primary);
  margin-left: auto;
}

.match-stats__bar--away {
  background-color: var(--color-secondary);
}

.match-stats__bar-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  min-width: 40px;
  text-align: center;
}

.match-stats__bar-value--home {
  color: var(--color-primary);
}

.match-stats__bar-value--away {
  color: var(--color-secondary);
}

.match-stats__detailed {
  overflow-x: auto;
}

.match-stats__table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);
}

.match-stats__table-header {
  padding: var(--spacing-3) var(--spacing-2);
  font-weight: 600;
  color: var(--color-text-secondary);
  border-bottom: 2px solid var(--color-border);
  text-align: center;
  white-space: nowrap;
}

.match-stats__table-header--stat {
  text-align: left;
  min-width: 120px;
}

.match-stats__table-header--home {
  color: var(--color-primary);
  min-width: 80px;
}

.match-stats__table-header--away {
  color: var(--color-secondary);
  min-width: 80px;
}

.match-stats__table-row {
  border-bottom: 1px solid var(--color-border-light);
}

.match-stats__table-row:hover {
  background-color: var(--color-bg-secondary);
}

.match-stats__table-cell {
  padding: var(--spacing-3) var(--spacing-2);
  text-align: center;
}

.match-stats__table-cell--stat {
  text-align: left;
}

.match-stats__table-label {
  display: block;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.match-stats__table-description {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-stats__table-value {
  display: block;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.match-stats__table-percentage {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-stats__table-cell--home .match-stats__table-value {
  color: var(--color-primary);
}

.match-stats__table-cell--away .match-stats__table-value {
  color: var(--color-secondary);
}

.match-stats__advanced {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-6);
}

.match-stats__advanced-section {
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
}

.match-stats--compact .match-stats__advanced-section {
  padding: var(--spacing-3);
}

.match-stats__advanced-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-3);
  text-align: center;
}

.match-stats__possession-chart {
  display: flex;
  height: 40px;
  border-radius: var(--radius-full);
  overflow: hidden;
  background-color: var(--color-bg-tertiary);
  position: relative;
}

.match-stats__possession-home,
.match-stats__possession-away {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  height: 100%;
  transition: width 1s ease;
}

.match-stats__possession-bar {
  position: absolute;
  top: 0;
  height: 100%;
}

.match-stats__possession-bar--home {
  left: 0;
  background-color: var(--color-primary);
}

.match-stats__possession-bar--away {
  right: 0;
  background-color: var(--color-secondary);
}

.match-stats__possession-value {
  position: relative;
  z-index: 1;
  font-weight: 700;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.match-stats__shots-chart {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-4);
}

.match-stats--compact .match-stats__shots-chart {
  grid-template-columns: 1fr;
  gap: var(--spacing-3);
}

.match-stats__shots-home,
.match-stats__shots-away {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.match-stats__shots-home {
  text-align: right;
}

.match-stats__shots-away {
  text-align: left;
}

.match-stats__shots-total {
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.match-stats__shots-on-target {
  color: var(--color-success);
}

.match-stats__shots-off-target {
  color: var(--color-warning);
}

.match-stats__shots-blocked {
  color: var(--color-text-secondary);
}

.match-stats__empty {
  padding: var(--spacing-8) var(--spacing-4);
}

.match-stats__source {
  text-align: center;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding-top: var(--spacing-3);
  border-top: 1px solid var(--color-border-light);
}

.match-stats__source-label {
  margin-right: var(--spacing-1);
}

.match-stats__source-name {
  font-weight: 600;
}

/* 响应式 */
@media (max-width: 640px) {
  .match-stats__summary-grid {
    grid-template-columns: 1fr;
  }
  
  .match-stats__table {
    font-size: var(--font-size-xs);
  }
  
  .match-stats__table-header,
  .match-stats__table-cell {
    padding: var(--spacing-2) var(--spacing-1);
  }
  
  .match-stats__shots-chart {
    grid-template-columns: 1fr;
  }
}
</style>