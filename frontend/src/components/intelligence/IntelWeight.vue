<template>
  <div :class="weightClasses" :title="weightTitle">
    <!-- 权重数值 -->
    <div class="intel-weight__value">
      <span class="intel-weight__number">{{ formattedWeight }}</span>
      <span v-if="showMax && maxWeight" class="intel-weight__max">/{{ maxWeight }}</span>
    </div>

    <!-- 权重标签 -->
    <div v-if="showLabel" class="intel-weight__label">
      {{ weightLabel }}
    </div>

    <!-- 权重描述 -->
    <div v-if="showDescription && weightDescription" class="intel-weight__description">
      {{ weightDescription }}
    </div>

    <!-- 权重指示器（柱状图） -->
    <div v-if="showIndicator" class="intel-weight__indicator">
      <div class="intel-weight__indicator-track">
        <div
          class="intel-weight__indicator-fill"
          :style="{ width: `${weightPercentage}%` }"
          :class="`intel-weight__indicator-fill--${weightLevel}`"
        ></div>
      </div>
      
      <!-- 刻度标记 -->
      <div v-if="showMarks" class="intel-weight__marks">
        <span
          v-for="mark in marks"
          :key="mark.value"
          :class="['intel-weight__mark', { 'intel-weight__mark--active': mark.value <= weight }]"
          :style="{ left: `${(mark.value / maxWeight) * 100}%` }"
          :title="mark.label"
        ></span>
      </div>
    </div>

    <!-- 权重图标 -->
    <div v-if="showIcon" class="intel-weight__icon">
      <component :is="weightIcon" :size="iconSize" />
    </div>

    <!-- 趋势指示器 -->
    <div v-if="showTrend && weightTrend !== undefined" class="intel-weight__trend">
      <span :class="['intel-weight__trend-icon', `intel-weight__trend-icon--${trendDirection}`]">
        <svg width="12" height="12" viewBox="0 0 24 24">
          <path v-if="trendDirection === 'up'" fill="currentColor" d="M12 8l-6 6 1.41 1.41L12 10.83l4.59 4.58L18 14z"/>
          <path v-else-if="trendDirection === 'down'" fill="currentColor" d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"/>
          <path v-else fill="currentColor" d="M22 12l-4-4v3H6v-3l-4 4 4 4v-3h12v3l4-4z"/>
        </svg>
      </span>
      <span v-if="showTrendValue" class="intel-weight__trend-value">
        {{ Math.abs(weightTrend).toFixed(1) }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  weight: {
    type: [Number, String],
    default: 0,
    validator: (value) => {
      const num = parseFloat(value)
      return !isNaN(num) && num >= 0
    }
  },
  maxWeight: {
    type: Number,
    default: 10
  },
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large', 'x-large'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'circular', 'pill', 'minimal'].includes(value)
  },
  showLabel: {
    type: Boolean,
    default: true
  },
  showDescription: {
    type: Boolean,
    default: false
  },
  showMax: {
    type: Boolean,
    default: false
  },
  showIndicator: {
    type: Boolean,
    default: true
  },
  showMarks: {
    type: Boolean,
    default: false
  },
  showIcon: {
    type: Boolean,
    default: false
  },
  showTrend: {
    type: Boolean,
    default: false
  },
  showTrendValue: {
    type: Boolean,
    default: false
  },
  weightDescription: {
    type: String,
    default: ''
  },
  weightTrend: {
    type: Number,
    default: undefined
  },
  marks: {
    type: Array,
    default: () => [
      { value: 2, label: '低' },
      { value: 5, label: '中' },
      { value: 8, label: '高' }
    ]
  }
})

// 计算属性
const weightClasses = computed(() => ({
  'intel-weight': true,
  [`intel-weight--${props.size}`]: true,
  [`intel-weight--${props.variant}`]: true,
  [`intel-weight--${weightLevel.value}`]: true,
  'intel-weight--with-trend': props.showTrend && props.weightTrend !== undefined
}))

const weightLevel = computed(() => {
  const numWeight = parseFloat(props.weight)
  if (numWeight >= 8) return 'high'
  if (numWeight >= 5) return 'medium'
  if (numWeight >= 2) return 'low'
  return 'very-low'
})

const weightLabel = computed(() => {
  const labels = {
    'high': '高权重',
    'medium': '中权重',
    'low': '低权重',
    'very-low': '极低权重'
  }
  return labels[weightLevel.value] || '未知权重'
})

const weightTitle = computed(() => {
  const numWeight = parseFloat(props.weight)
  const descriptions = {
    'high': '此情报具有很高的参考价值，可能对比赛结果产生重大影响',
    'medium': '此情报具有中等参考价值，可能对比赛结果产生一定影响',
    'low': '此情报参考价值较低，对比赛结果影响有限',
    'very-low': '此情报参考价值极低，仅供参考'
  }
  return `${weightLabel.value}: ${numWeight.toFixed(1)}/${props.maxWeight}\n${descriptions[weightLevel.value] || ''}`
})

const weightPercentage = computed(() => {
  const numWeight = parseFloat(props.weight)
  return Math.min((numWeight / props.maxWeight) * 100, 100)
})

const formattedWeight = computed(() => {
  const numWeight = parseFloat(props.weight)
  return numWeight % 1 === 0 ? numWeight.toString() : numWeight.toFixed(1)
})

const trendDirection = computed(() => {
  if (props.weightTrend === undefined) return 'stable'
  if (props.weightTrend > 0) return 'up'
  if (props.weightTrend < 0) return 'down'
  return 'stable'
})

const weightIcon = computed(() => {
  // 这里可以根据权重级别返回不同的图标组件
  // 实际项目中应该导入真实的图标组件
  const icons = {
    'high': { template: '<span>🔥</span>' },
    'medium': { template: '<span>⚠️</span>' },
    'low': { template: '<span>ℹ️</span>' },
    'very-low': { template: '<span>💡</span>' }
  }
  return icons[weightLevel.value] || icons['low']
})

const iconSize = computed(() => {
  const sizes = {
    'small': 16,
    'medium': 20,
    'large': 24,
    'x-large': 32
  }
  return sizes[props.size] || 20
})
</script>

<style scoped>
.intel-weight {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3);
  border-radius: var(--radius-md);
  background-color: var(--color-bg-secondary);
  transition: all 0.2s ease;
  position: relative;
}

/* 尺寸 */
.intel-weight--small {
  padding: var(--spacing-2);
  gap: var(--spacing-1);
}

.intel-weight--medium {
  padding: var(--spacing-3);
  gap: var(--spacing-2);
}

.intel-weight--large {
  padding: var(--spacing-4);
  gap: var(--spacing-3);
}

.intel-weight--x-large {
  padding: var(--spacing-6);
  gap: var(--spacing-4);
}

/* 变体 */
.intel-weight--circular {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  justify-content: center;
}

.intel-weight--pill {
  border-radius: var(--radius-full);
  padding-left: var(--spacing-4);
  padding-right: var(--spacing-4);
}

.intel-weight--minimal {
  background-color: transparent;
  padding: 0;
}

/* 权重级别 */
.intel-weight--high {
  border: 2px solid var(--color-danger);
  background-color: rgba(var(--color-danger-rgb), 0.1);
}

.intel-weight--medium {
  border: 2px solid var(--color-warning);
  background-color: rgba(var(--color-warning-rgb), 0.1);
}

.intel-weight--low {
  border: 2px solid var(--color-info);
  background-color: rgba(var(--color-info-rgb), 0.1);
}

.intel-weight--very-low {
  border: 2px solid var(--color-text-tertiary);
  background-color: rgba(var(--color-text-tertiary-rgb), 0.1);
}

.intel-weight__value {
  display: flex;
  align-items: baseline;
  gap: 2px;
}

.intel-weight__number {
  font-size: var(--font-size-2xl);
  font-weight: 800;
  line-height: 1;
  color: var(--color-text-primary);
}

.intel-weight--small .intel-weight__number {
  font-size: var(--font-size-lg);
}

.intel-weight--medium .intel-weight__number {
  font-size: var(--font-size-2xl);
}

.intel-weight--large .intel-weight__number {
  font-size: var(--font-size-3xl);
}

.intel-weight--x-large .intel-weight__number {
  font-size: var(--font-size-4xl);
}

.intel-weight--high .intel-weight__number {
  color: var(--color-danger);
}

.intel-weight--medium .intel-weight__number {
  color: var(--color-warning);
}

.intel-weight--low .intel-weight__number {
  color: var(--color-info);
}

.intel-weight--very-low .intel-weight__number {
  color: var(--color-text-tertiary);
}

.intel-weight__max {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  font-weight: 500;
}

.intel-weight__label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
  text-align: center;
}

.intel-weight--high .intel-weight__label {
  color: var(--color-danger);
}

.intel-weight--medium .intel-weight__label {
  color: var(--color-warning);
}

.intel-weight--low .intel-weight__label {
  color: var(--color-info);
}

.intel-weight--very-low .intel-weight__label {
  color: var(--color-text-tertiary);
}

.intel-weight__description {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
  line-height: 1.4;
  max-width: 200px;
}

.intel-weight__indicator {
  width: 100%;
  position: relative;
}

.intel-weight--circular .intel-weight__indicator {
  position: absolute;
  bottom: -20px;
  left: 10%;
  right: 10%;
}

.intel-weight__indicator-track {
  width: 100%;
  height: 6px;
  background-color: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.intel-weight--small .intel-weight__indicator-track {
  height: 4px;
}

.intel-weight--large .intel-weight__indicator-track {
  height: 8px;
}

.intel-weight--x-large .intel-weight__indicator-track {
  height: 10px;
}

.intel-weight__indicator-fill {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width 1s ease-out;
}

.intel-weight__indicator-fill--high {
  background: linear-gradient(90deg, var(--color-danger-light), var(--color-danger));
}

.intel-weight__indicator-fill--medium {
  background: linear-gradient(90deg, var(--color-warning-light), var(--color-warning));
}

.intel-weight__indicator-fill--low {
  background: linear-gradient(90deg, var(--color-info-light), var(--color-info));
}

.intel-weight__indicator-fill--very-low {
  background: linear-gradient(90deg, var(--color-text-tertiary), var(--color-text-secondary));
}

.intel-weight__marks {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
}

.intel-weight__mark {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background-color: var(--color-bg-card);
  border: 2px solid var(--color-border);
  border-radius: 50%;
  transition: all 0.2s ease;
}

.intel-weight__mark--active {
  background-color: var(--color-primary);
  border-color: var(--color-primary);
}

.intel-weight__icon {
  margin-top: var(--spacing-1);
}

.intel-weight__trend {
  position: absolute;
  top: -8px;
  right: -8px;
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 6px;
  border-radius: var(--radius-full);
  background-color: var(--color-bg-card);
  box-shadow: var(--shadow-sm);
  z-index: 1;
}

.intel-weight__trend-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.intel-weight__trend-icon--up {
  color: var(--color-success);
}

.intel-weight__trend-icon--down {
  color: var(--color-danger);
}

.intel-weight__trend-icon--stable {
  color: var(--color-text-secondary);
}

.intel-weight__trend-value {
  font-size: var(--font-size-xs);
  font-weight: 600;
}

.intel-weight__trend-icon--up + .intel-weight__trend-value {
  color: var(--color-success);
}

.intel-weight__trend-icon--down + .intel-weight__trend-value {
  color: var(--color-danger);
}

/* 圆形变体的特殊样式 */
.intel-weight--circular .intel-weight__value {
  flex-direction: column;
  align-items: center;
  gap: 0;
}

.intel-weight--circular .intel-weight__number {
  font-size: var(--font-size-2xl);
}

.intel-weight--circular .intel-weight__max {
  font-size: var(--font-size-xs);
}

.intel-weight--circular .intel-weight__label {
  font-size: var(--font-size-xs);
  margin-top: 4px;
}

/* 响应式 */
@media (max-width: 640px) {
  .intel-weight--x-large {
    padding: var(--spacing-4);
  }
  
  .intel-weight--x-large .intel-weight__number {
    font-size: var(--font-size-3xl);
  }
}
</style>