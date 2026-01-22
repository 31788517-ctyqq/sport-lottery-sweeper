<template>
  <div :class="oddsClasses">
    <!-- 标题 -->
    <div v-if="showTitle" class="match-odds__title">
      <h4 class="match-odds__title-text">{{ oddsTitle }}</h4>
      <div v-if="lastUpdated" class="match-odds__updated">
        更新于 {{ formatTime(lastUpdated) }}
      </div>
    </div>

    <!-- 赔率类型标签 -->
    <div v-if="showOddsTypeTabs" class="match-odds__tabs">
      <button
        v-for="tab in oddsTabs"
        :key="tab.value"
        :class="['match-odds__tab', { 'match-odds__tab--active': activeTab === tab.value }]"
        @click="activeTab = tab.value"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- 1X2 赔率 -->
    <div v-if="showOdds1X2" class="match-odds__section">
      <div class="match-odds__section-title">1X2</div>
      <div class="match-odds__grid match-odds__grid--1x2">
        <div class="match-odds__option">
          <div class="match-odds__option-label">主胜</div>
          <div class="match-odds__option-value">
            <span class="match-odds__value">{{ formatOdds(odds1X2.home) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="odds1X2.homeChange" />
          </div>
          <div v-if="showProbability" class="match-odds__probability">
            {{ formatProbability(odds1X2.homeProbability) }}
          </div>
        </div>
        
        <div class="match-odds__option">
          <div class="match-odds__option-label">平局</div>
          <div class="match-odds__option-value">
            <span class="match-odds__value">{{ formatOdds(odds1X2.draw) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="odds1X2.drawChange" />
          </div>
          <div v-if="showProbability" class="match-odds__probability">
            {{ formatProbability(odds1X2.drawProbability) }}
          </div>
        </div>
        
        <div class="match-odds__option">
          <div class="match-odds__option-label">客胜</div>
          <div class="match-odds__option-value">
            <span class="match-odds__value">{{ formatOdds(odds1X2.away) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="odds1X2.awayChange" />
          </div>
          <div v-if="showProbability" class="match-odds__probability">
            {{ formatProbability(odds1X2.awayProbability) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 亚洲盘赔率 -->
    <div v-if="showAsianHandicap" class="match-odds__section">
      <div class="match-odds__section-title">亚洲盘</div>
      <div class="match-odds__grid match-odds__grid--asian">
        <div class="match-odds__asian-row">
          <div class="match-odds__asian-team">主队</div>
          <div class="match-odds__asian-handicap">{{ asianHandicap.homeHandicap }}</div>
          <div class="match-odds__asian-odds">
            <span class="match-odds__value">{{ formatOdds(asianHandicap.homeOdds) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="asianHandicap.homeChange" />
          </div>
        </div>
        
        <div class="match-odds__asian-row">
          <div class="match-odds__asian-team">客队</div>
          <div class="match-odds__asian-handicap">{{ asianHandicap.awayHandicap }}</div>
          <div class="match-odds__asian-odds">
            <span class="match-odds__value">{{ formatOdds(asianHandicap.awayOdds) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="asianHandicap.awayChange" />
          </div>
        </div>
      </div>
    </div>

    <!-- 大小球赔率 -->
    <div v-if="showOverUnder" class="match-odds__section">
      <div class="match-odds__section-title">大小球 ({{ overUnder.line }})</div>
      <div class="match-odds__grid match-odds__grid--over-under">
        <div class="match-odds__over-under-row">
          <div class="match-odds__over-under-label">大球</div>
          <div class="match-odds__over-under-odds">
            <span class="match-odds__value">{{ formatOdds(overUnder.over) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="overUnder.overChange" />
          </div>
        </div>
        
        <div class="match-odds__over-under-row">
          <div class="match-odds__over-under-label">小球</div>
          <div class="match-odds__over-under-odds">
            <span class="match-odds__value">{{ formatOdds(overUnder.under) }}</span>
            <OddsChangeIndicator v-if="showChange" :change="overUnder.underChange" />
          </div>
        </div>
      </div>
    </div>

    <!-- 博彩公司信息 -->
    <div v-if="showBookmakerInfo && bookmaker" class="match-odds__bookmaker">
      <div class="match-odds__bookmaker-info">
        <img v-if="bookmaker.logo" :src="bookmaker.logo" :alt="bookmaker.name" class="match-odds__bookmaker-logo" />
        <span class="match-odds__bookmaker-name">{{ bookmaker.name }}</span>
      </div>
      <div v-if="bookmaker.returnRate" class="match-odds__return-rate">
        返还率: {{ (bookmaker.returnRate * 100).toFixed(1) }}%
      </div>
    </div>

    <!-- 赔率历史图表 -->
    <div v-if="showHistoryChart && oddsHistory" class="match-odds__history">
      <div class="match-odds__history-title">赔率变化趋势</div>
      <div class="match-odds__history-chart">
        <!-- 这里可以集成图表组件 -->
        <div class="match-odds__chart-placeholder">赔率变化图表</div>
      </div>
    </div>

    <!-- 无赔率数据 -->
    <div v-if="showEmptyState && !hasOddsData" class="match-odds__empty">
      <EmptyState
        title="暂无赔率数据"
        description="当前比赛暂无赔率信息"
        icon="😕"
        variant="compact"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import EmptyState from '../common/EmptyState.vue'
import OddsChangeIndicator from './OddsChangeIndicator.vue'
import { formatTime } from '@/utils/date'

const props = defineProps({
  odds: {
    type: Object,
    default: () => ({})
  },
  type: {
    type: String,
    default: '1x2',
    validator: (value) => ['1x2', 'asian', 'over-under', 'all'].includes(value)
  },
  compact: {
    type: Boolean,
    default: false
  },
  showTitle: {
    type: Boolean,
    default: true
  },
  showOddsTypeTabs: {
    type: Boolean,
    default: false
  },
  showChange: {
    type: Boolean,
    default: true
  },
  showProbability: {
    type: Boolean,
    default: false
  },
  showBookmakerInfo: {
    type: Boolean,
    default: false
  },
  showHistoryChart: {
    type: Boolean,
    default: false
  },
  showEmptyState: {
    type: Boolean,
    default: true
  },
  bookmaker: {
    type: Object,
    default: () => ({
      id: '',
      name: '',
      logo: '',
      returnRate: 0.94
    })
  },
  oddsHistory: {
    type: Array,
    default: () => []
  },
  lastUpdated: {
    type: [String, Date],
    default: ''
  }
})

const activeTab = ref(props.type)

// 计算属性
const oddsClasses = computed(() => ({
  'match-odds': true,
  'match-odds--compact': props.compact,
  'match-odds--detailed': !props.compact,
  [`match-odds--${props.type}`]: true
}))

const oddsTitle = computed(() => {
  const titles = {
    '1x2': '1X2 赔率',
    'asian': '亚洲盘赔率',
    'over-under': '大小球赔率',
    'all': '全部赔率'
  }
  return titles[props.type] || '赔率'
})

const oddsTabs = computed(() => [
  { value: '1x2', label: '1X2' },
  { value: 'asian', label: '亚洲盘' },
  { value: 'over-under', label: '大小球' }
])

const odds1X2 = computed(() => ({
  home: props.odds['1x2']?.home || props.odds.home || null,
  draw: props.odds['1x2']?.draw || props.odds.draw || null,
  away: props.odds['1x2']?.away || props.odds.away || null,
  homeChange: props.odds['1x2']?.homeChange || null,
  drawChange: props.odds['1x2']?.drawChange || null,
  awayChange: props.odds['1x2']?.awayChange || null,
  homeProbability: props.odds['1x2']?.homeProbability || null,
  drawProbability: props.odds['1x2']?.drawProbability || null,
  awayProbability: props.odds['1x2']?.awayProbability || null
}))

const asianHandicap = computed(() => ({
  homeHandicap: props.odds.asian?.homeHandicap || props.odds.handicap?.home || null,
  awayHandicap: props.odds.asian?.awayHandicap || props.odds.handicap?.away || null,
  homeOdds: props.odds.asian?.homeOdds || null,
  awayOdds: props.odds.asian?.awayOdds || null,
  homeChange: props.odds.asian?.homeChange || null,
  awayChange: props.odds.asian?.awayChange || null
}))

const overUnder = computed(() => ({
  line: props.odds.overUnder?.line || props.odds.line || '2.5',
  over: props.odds.overUnder?.over || props.odds.over || null,
  under: props.odds.overUnder?.under || props.odds.under || null,
  overChange: props.odds.overUnder?.overChange || null,
  underChange: props.odds.overUnder?.underChange || null
}))

const hasOddsData = computed(() => {
  if (props.type === '1x2') {
    return odds1X2.value.home !== null || odds1X2.value.draw !== null || odds1X2.value.away !== null
  }
  if (props.type === 'asian') {
    return asianHandicap.value.homeOdds !== null || asianHandicap.value.awayOdds !== null
  }
  if (props.type === 'over-under') {
    return overUnder.value.over !== null || overUnder.value.under !== null
  }
  return false
})

const showOdds1X2 = computed(() => {
  return props.type === '1x2' || props.type === 'all'
})

const showAsianHandicap = computed(() => {
  return props.type === 'asian' || props.type === 'all'
})

const showOverUnder = computed(() => {
  return props.type === 'over-under' || props.type === 'all'
})

// 方法
const formatOdds = (odds) => {
  if (odds === null || odds === undefined) return '-'
  const num = parseFloat(odds)
  return isNaN(num) ? odds : num.toFixed(2)
}

const formatProbability = (probability) => {
  if (probability === null || probability === undefined) return ''
  const percent = probability * 100
  return percent.toFixed(1) + '%'
}
</script>

<style scoped>
.match-odds {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-4);
}

.match-odds--compact {
  gap: var(--spacing-3);
  padding: var(--spacing-3);
}

.match-odds__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--spacing-2);
}

.match-odds__title-text {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-odds__updated {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-odds__tabs {
  display: flex;
  gap: var(--spacing-1);
  background-color: var(--color-bg-tertiary);
  padding: var(--spacing-1);
  border-radius: var(--radius-md);
}

.match-odds__tab {
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

.match-odds__tab:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.match-odds__tab--active {
  background-color: var(--color-bg-card);
  color: var(--color-text-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.match-odds__section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

.match-odds__section-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.match-odds__grid {
  display: grid;
  gap: var(--spacing-2);
}

.match-odds__grid--1x2 {
  grid-template-columns: repeat(3, 1fr);
}

.match-odds__grid--asian,
.match-odds__grid--over-under {
  grid-template-columns: 1fr;
  gap: var(--spacing-1);
}

.match-odds__option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  transition: all 0.2s ease;
}

.match-odds__option:hover {
  border-color: var(--color-primary);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.match-odds__option-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-odds__option-value {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.match-odds__value {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--color-primary);
  min-width: 50px;
  text-align: center;
}

.match-odds--compact .match-odds__value {
  font-size: var(--font-size-lg);
}

.match-odds__probability {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding: 2px 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
}

.match-odds__asian-row,
.match-odds__over-under-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  align-items: center;
  gap: var(--spacing-3);
  padding: var(--spacing-3);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
}

.match-odds--compact .match-odds__asian-row,
.match-odds--compact .match-odds__over-under-row {
  padding: var(--spacing-2);
  gap: var(--spacing-2);
}

.match-odds__asian-team,
.match-odds__over-under-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-odds__asian-handicap {
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--color-warning);
  text-align: center;
}

.match-odds__asian-odds,
.match-odds__over-under-odds {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: var(--spacing-2);
}

.match-odds__bookmaker {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-3);
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  margin-top: var(--spacing-2);
}

.match-odds__bookmaker-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.match-odds__bookmaker-logo {
  width: 24px;
  height: 24px;
  object-fit: contain;
}

.match-odds__bookmaker-name {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.match-odds__return-rate {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.match-odds__history {
  margin-top: var(--spacing-4);
}

.match-odds__history-title {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2);
}

.match-odds__history-chart {
  height: 100px;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.match-odds__chart-placeholder {
  color: var(--color-text-tertiary);
  font-size: var(--font-size-sm);
}

.match-odds__empty {
  padding: var(--spacing-8) var(--spacing-4);
}

/* 响应式 */
@media (max-width: 640px) {
  .match-odds__grid--1x2 {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
  }
  
  .match-odds__asian-row,
  .match-odds__over-under-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-2);
    text-align: center;
  }
  
  .match-odds__asian-odds,
  .match-odds__over-under-odds {
    justify-content: center;
  }
  
  .match-odds__bookmaker {
    flex-direction: column;
    gap: var(--spacing-2);
    text-align: center;
  }
}
</style>