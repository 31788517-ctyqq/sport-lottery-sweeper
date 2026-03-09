<template>
  <BaseCard :class="cardClasses" :hoverable="hoverable" :clickable="clickable" @click="$emit('click', $event)">
    <!-- 卡片内容 -->
    <div class="stats-card__content">
      <!-- 头部 -->
      <div class="stats-card__header">
        <!-- 图标 -->
        <div v-if="icon || $slots.icon" class="stats-card__icon" :style="iconStyles">
          <slot name="icon">
            <component v-if="icon" :is="icon" :size="iconSize" />
          </slot>
        </div>
        
        <!-- 标题 -->
        <div class="stats-card__title-area">
          <h4 class="stats-card__title">{{ title }}</h4>
          <div v-if="subtitle" class="stats-card__subtitle">{{ subtitle }}</div>
        </div>
        
        <!-- 更多操作 -->
        <div v-if="showMore" class="stats-card__more">
          <button
            class="stats-card__more-button"
            @click.stop="$emit('more')"
            aria-label="更多操作"
          >
            <svg width="16" height="16" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="6" cy="12" r="1.5" fill="currentColor"/>
              <circle cx="18" cy="12" r="1.5" fill="currentColor"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- 数值显示 -->
      <div class="stats-card__value-area">
        <!-- 主值 -->
        <div class="stats-card__value" :style="valueStyles">
          {{ formatValue(value) }}
          <span v-if="unit" class="stats-card__unit">{{ unit }}</span>
        </div>
        
        <!-- 副值 -->
        <div v-if="secondaryValue !== undefined" class="stats-card__secondary-value">
          {{ formatValue(secondaryValue, secondaryUnit) }}
        </div>
      </div>

      <!-- 变化趋势 -->
      <div v-if="showChange && change !== undefined" class="stats-card__change">
        <div class="stats-card__change-indicator" :class="changeClasses">
          <span class="stats-card__change-icon">
            <svg v-if="changeType === 'increase'" width="12" height="12" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 14l5-5 5 5z"/>
            </svg>
            <svg v-else-if="changeType === 'decrease'" width="12" height="12" viewBox="0 0 24 24">
              <path fill="currentColor" d="M7 10l5 5 5-5z"/>
            </svg>
            <svg v-else width="12" height="12" viewBox="0 0 24 24">
              <path fill="currentColor" d="M13 7h-2v10h2V7zm4 6h-2v4h2v-4zM9 9H7v8h2V9z"/>
            </svg>
          </span>
          <span class="stats-card__change-value">{{ formatChange(change) }}</span>
          <span v-if="changePeriod" class="stats-card__change-period">{{ changePeriod }}</span>
        </div>
        
        <!-- 趋势描述 -->
        <div v-if="changeDescription" class="stats-card__change-description">
          {{ changeDescription }}
        </div>
      </div>

      <!-- 进度条 -->
      <div v-if="showProgress && progress !== undefined" class="stats-card__progress">
        <div class="stats-card__progress-info">
          <span class="stats-card__progress-label">进度</span>
          <span class="stats-card__progress-value">{{ progress }}%</span>
        </div>
        <div class="stats-card__progress-bar">
          <div
            class="stats-card__progress-fill"
            :style="{ width: `${progress}%`, backgroundColor: color }"
          ></div>
        </div>
      </div>

      <!-- 趋势图表 -->
      <div v-if="showTrend && trendData" class="stats-card__trend">
        <StatsTrend
          :data="trendData"
          :type="trendType"
          :color="trendColor || color"
          :height="40"
          hide-axes
          hide-legend
        />
      </div>

      <!-- 额外信息 -->
      <div v-if="extraInfo" class="stats-card__extra">
        {{ extraInfo }}
      </div>

      <!-- 底部内容 -->
      <div v-if="$slots.default" class="stats-card__body">
        <slot></slot>
      </div>

      <!-- 底部操作 -->
      <div v-if="$slots.footer" class="stats-card__footer">
        <slot name="footer"></slot>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="stats-card__loading">
      <LoadingSpinner size="small" />
    </div>

    <!-- 角标 -->
    <div v-if="badge" class="stats-card__badge">
      <span :class="['stats-card__badge-text', `stats-card__badge-text--${badge.type || 'default'}`]">
        {{ badge.text }}
      </span>
    </div>
  </BaseCard>
</template>

<script setup>
import { computed } from 'vue'
import BaseCard from '../common/BaseCard.vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import StatsTrend from './StatsTrend.vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  value: {
    type: [Number, String],
    default: 0
  },
  secondaryValue: {
    type: [Number, String],
    default: undefined
  },
  unit: {
    type: String,
    default: ''
  },
  secondaryUnit: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  color: {
    type: String,
    default: ''
  },
  change: {
    type: [Number, String],
    default: undefined
  },
  changeType: {
    type: String,
    default: 'neutral', // 'increase', 'decrease', 'neutral'
    validator: (value) => ['increase', 'decrease', 'neutral'].includes(value)
  },
  changePeriod: {
    type: String,
    default: ''
  },
  changeDescription: {
    type: String,
    default: ''
  },
  showChange: {
    type: Boolean,
    default: true
  },
  progress: {
    type: Number,
    default: undefined
  },
  showProgress: {
    type: Boolean,
    default: false
  },
  trendData: {
    type: Array,
    default: null
  },
  trendType: {
    type: String,
    default: 'line' // 'line', 'area', 'bar'
  },
  trendColor: {
    type: String,
    default: ''
  },
  showTrend: {
    type: Boolean,
    default: false
  },
  extraInfo: {
    type: String,
    default: ''
  },
  badge: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  compact: {
    type: Boolean,
    default: false
  },
  hoverable: {
    type: Boolean,
    default: true
  },
  clickable: {
    type: Boolean,
    default: false
  },
  showMore: {
    type: Boolean,
    default: false
  },
  valueFormat: {
    type: String,
    default: 'number', // 'number', 'currency', 'percent', 'decimal'
    validator: (value) => ['number', 'currency', 'percent', 'decimal'].includes(value)
  },
  currency: {
    type: String,
    default: '¥'
  },
  decimalPlaces: {
    type: Number,
    default: 0
  },
  formatOptions: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['click', 'more'])

// 计算属性
const cardClasses = computed(() => ({
  'stats-card': true,
  'stats-card--compact': props.compact,
  'stats-card--loading': props.loading,
  'stats-card--has-change': props.change !== undefined,
  'stats-card--has-progress': props.progress !== undefined,
  'stats-card--has-trend': props.trendData !== null
}))

const changeClasses = computed(() => ({
  'stats-card__change-indicator': true,
  [`stats-card__change-indicator--${props.changeType}`]: true
}))

const iconStyles = computed(() => ({
  color: props.color || undefined,
  backgroundColor: props.color ? `${props.color}20` : undefined
}))

const valueStyles = computed(() => ({
  color: props.color || undefined
}))

const iconSize = computed(() => {
  return props.compact ? 24 : 32
})

// 方法
const formatValue = (value, unit = '') => {
  if (value === undefined || value === null) return '-'
  
  let formattedValue = value
  
  // 根据类型格式化
  switch (props.valueFormat) {
    case 'currency':
      formattedValue = `${props.currency}${formatNumber(value)}`
      break
    case 'percent':
      formattedValue = `${formatNumber(value, props.decimalPlaces)}%`
      break
    case 'decimal':
      formattedValue = formatNumber(value, props.decimalPlaces)
      break
    default:
      formattedValue = formatNumber(value, 0)
  }
  
  // 添加单位
  if (unit && props.valueFormat === 'number') {
    formattedValue += ` ${unit}`
  }
  
  return formattedValue
}

const formatNumber = (value, decimalPlaces = 0) => {
  const num = parseFloat(value)
  if (isNaN(num)) return value
  
  if (Math.abs(num) >= 1000000) {
    return `${(num / 1000000).toFixed(decimalPlaces)}M`
  } else if (Math.abs(num) >= 1000) {
    return `${(num / 1000).toFixed(decimalPlaces)}K`
  } else {
    return num.toFixed(decimalPlaces)
  }
}

const formatChange = (change) => {
  if (change === undefined || change === null) return ''
  
  const prefix = change > 0 ? '+' : ''
  
  if (typeof change === 'number') {
    if (Math.abs(change) >= 100) {
      return `${prefix}${change.toFixed(0)}`
    } else {
      return `${prefix}${change.toFixed(1)}`
    }
  }
  
  return `${prefix}${change}`
}
</script>

<style scoped>
.stats-card {
  position: relative;
  transition: all 0.3s ease;
  overflow: hidden;
}

.stats-card--compact {
  padding: var(--spacing-3) !important;
}

.stats-card--has-change:hover .stats-card__change {
  transform: translateY(-2px);
}

.stats-card__content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-4);
}

.stats-card--compact .stats-card__content {
  gap: var(--spacing-3);
}

.stats-card__header {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-3);
}

.stats-card__icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  flex-shrink: 0;
  background-color: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
}

.stats-card--compact .stats-card__icon {
  width: 36px;
  height: 36px;
}

.stats-card__title-area {
  flex: 1;
  min-width: 0;
}

.stats-card__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  line-height: 1.4;
}

.stats-card--compact .stats-card__title {
  font-size: var(--font-size-sm);
}

.stats-card__subtitle {
  margin-top: 2px;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-card--compact .stats-card__subtitle {
  font-size: var(--font-size-xs);
}

.stats-card__more {
  flex-shrink: 0;
}

.stats-card__more-button {
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

.stats-card__more-button:hover {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}

.stats-card__value-area {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-2);
}

.stats-card__value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  line-height: 1;
  color: var(--color-text-primary);
}

.stats-card--compact .stats-card__value {
  font-size: var(--font-size-2xl);
}

.stats-card__unit {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-secondary);
  margin-left: 4px;
}

.stats-card--compact .stats-card__unit {
  font-size: var(--font-size-sm);
}

.stats-card__secondary-value {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.stats-card--compact .stats-card__secondary-value {
  font-size: var(--font-size-sm);
}

.stats-card__change {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-1);
  transition: transform 0.2s ease;
}

.stats-card__change-indicator {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-base);
  font-weight: 600;
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  width: fit-content;
}

.stats-card--compact .stats-card__change-indicator {
  font-size: var(--font-size-sm);
}

.stats-card__change-indicator--increase {
  color: var(--color-success);
  background-color: var(--color-success-light);
}

.stats-card__change-indicator--decrease {
  color: var(--color-danger);
  background-color: var(--color-danger-light);
}

.stats-card__change-indicator--neutral {
  color: var(--color-text-secondary);
  background-color: var(--color-bg-tertiary);
}

.stats-card__change-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-card__change-value {
  font-weight: 700;
}

.stats-card__change-period {
  font-size: var(--font-size-xs);
  opacity: 0.8;
}

.stats-card__change-description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stats-card__progress {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.stats-card__progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stats-card__progress-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-card__progress-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
}

.stats-card__progress-bar {
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.stats-card__progress-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s ease-out;
  background-color: var(--color-primary);
}

.stats-card__trend {
  margin-top: var(--spacing-2);
}

.stats-card__extra {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  padding: var(--spacing-2);
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
}

.stats-card__body {
  margin-top: var(--spacing-3);
}

.stats-card__footer {
  margin-top: var(--spacing-4);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border-light);
}

.stats-card__loading {
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

.stats-card__badge {
  position: absolute;
  top: var(--spacing-3);
  right: var(--spacing-3);
  z-index: 2;
}

.stats-card__badge-text {
  display: inline-block;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: var(--shadow-sm);
}

.stats-card__badge-text--success {
  background-color: var(--color-success);
  color: white;
}

.stats-card__badge-text--warning {
  background-color: var(--color-warning);
  color: white;
}

.stats-card__badge-text--danger {
  background-color: var(--color-danger);
  color: white;
}

.stats-card__badge-text--info {
  background-color: var(--color-info);
  color: white;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.stats-card--loading .stats-card__value,
.stats-card--loading .stats-card__change-value {
  animation: pulse 1.5s ease-in-out infinite;
}
</style>