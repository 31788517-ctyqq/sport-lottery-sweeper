<template>
  <div :class="chartClasses" :style="chartStyles">
    <!-- 图表头部 -->
    <div v-if="showHeader" class="stats-chart__header">
      <div class="stats-chart__header-content">
        <h4 class="stats-chart__title">{{ title }}</h4>
        <div v-if="subtitle" class="stats-chart__subtitle">{{ subtitle }}</div>
      </div>
      
      <div class="stats-chart__header-actions">
        <!-- 图表类型切换 -->
        <div v-if="showTypeSwitch" class="stats-chart__type-switch">
          <button
            v-for="type in chartTypes"
            :key="type.value"
            :class="['stats-chart__type-button', { 'stats-chart__type-button--active': type.value === chartType }]"
            @click="changeChartType(type.value)"
          >
            {{ type.label }}
          </button>
        </div>
        
        <!-- 图例 -->
        <div v-if="showLegend" class="stats-chart__legend">
          <div
            v-for="(item, index) in legendItems"
            :key="index"
            :class="['stats-chart__legend-item', { 'stats-chart__legend-item--hidden': item.hidden }]"
            @click="toggleLegend(item)"
          >
            <span class="stats-chart__legend-color" :style="{ backgroundColor: item.color }"></span>
            <span class="stats-chart__legend-label">{{ item.name }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表容器 -->
    <div class="stats-chart__container" ref="chartContainer" :style="containerStyles">
      <!-- 图表占位符（实际项目中替换为真实图表库） -->
      <div v-if="!loading && !error" class="stats-chart__placeholder">
        <!-- 这里可以集成 ECharts、Chart.js 等图表库 -->
        <div class="stats-chart__placeholder-content">
          <div class="stats-chart__placeholder-title">图表预览</div>
          <div class="stats-chart__placeholder-desc">
            类型: {{ chartType }} | 数据点: {{ dataPoints }}
          </div>
          <div class="stats-chart__placeholder-canvas">
            <!-- 简单模拟图表 -->
            <div class="stats-chart__simulation">
              <div v-if="chartType === 'line'" class="stats-chart__simulation-line">
                <div
                  v-for="(point, index) in simulatedPoints"
                  :key="index"
                  class="stats-chart__simulation-point"
                  :style="{
                    left: `${point.x}%`,
                    bottom: `${point.y}%`,
                    backgroundColor: point.color
                  }"
                ></div>
              </div>
              <div v-else-if="chartType === 'bar'" class="stats-chart__simulation-bar">
                <div
                  v-for="(bar, index) in simulatedBars"
                  :key="index"
                  class="stats-chart__simulation-bar-item"
                  :style="{
                    height: `${bar.height}%`,
                    backgroundColor: bar.color,
                    width: `${100 / simulatedBars.length - 10}%`
                  }"
                ></div>
              </div>
              <div v-else-if="chartType === 'pie'" class="stats-chart__simulation-pie">
                <div class="stats-chart__simulation-pie-circle">
                  <div
                    v-for="(slice, index) in simulatedSlices"
                    :key="index"
                    class="stats-chart__simulation-slice"
                    :style="{
                      transform: `rotate(${slice.rotation}deg)`,
                      backgroundColor: slice.color
                    }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="stats-chart__loading">
        <LoadingSpinner size="medium" text="加载图表数据..." />
      </div>

      <!-- 错误状态 -->
      <div v-if="error" class="stats-chart__error">
        <EmptyState
          :title="errorTitle"
          :description="errorDescription"
          icon="📉"
          variant="compact"
          :action-text="errorActionText"
          @action="$emit('retry')"
        />
      </div>
    </div>

    <!-- 图表底部 -->
    <div v-if="showFooter" class="stats-chart__footer">
      <!-- X轴标签 -->
      <div v-if="showXAxis && xAxisLabels" class="stats-chart__x-axis">
        <div class="stats-chart__x-axis-labels">
          <span
            v-for="(label, index) in visibleXAxisLabels"
            :key="index"
            class="stats-chart__x-axis-label"
          >
            {{ label }}
          </span>
        </div>
      </div>

      <!-- 统计数据 -->
      <div v-if="showStats" class="stats-chart__stats">
        <div
          v-for="stat in chartStats"
          :key="stat.label"
          class="stats-chart__stat"
        >
          <div class="stats-chart__stat-label">{{ stat.label }}</div>
          <div class="stats-chart__stat-value">{{ stat.value }}</div>
        </div>
      </div>

      <!-- 数据来源 -->
      <div v-if="dataSource" class="stats-chart__source">
        <span class="stats-chart__source-label">数据来源:</span>
        <span class="stats-chart__source-name">{{ dataSource }}</span>
      </div>
    </div>

    <!-- 工具提示 -->
    <div v-if="showTooltip && tooltipData" class="stats-chart__tooltip" :style="tooltipStyles">
      <div class="stats-chart__tooltip-header">
        {{ tooltipData.title }}
      </div>
      <div class="stats-chart__tooltip-content">
        <div
          v-for="item in tooltipData.items"
          :key="item.name"
          class="stats-chart__tooltip-item"
        >
          <span class="stats-chart__tooltip-color" :style="{ backgroundColor: item.color }"></span>
          <span class="stats-chart__tooltip-name">{{ item.name }}:</span>
          <span class="stats-chart__tooltip-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import LoadingSpinner from '../common/LoadingSpinner.vue'
import EmptyState from '../common/EmptyState.vue'

const props = defineProps({
  data: {
    type: [Array, Object],
    default: () => []
  },
  type: {
    type: String,
    default: 'line',
    validator: (value) => ['line', 'bar', 'area', 'pie', 'radar', 'scatter', 'heatmap', 'candlestick'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  options: {
    type: Object,
    default: () => ({})
  },
  height: {
    type: [Number, String],
    default: 300
  },
  width: {
    type: [Number, String],
    default: '100%'
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: Boolean,
    default: false
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showXAxis: {
    type: Boolean,
    default: true
  },
  showYAxis: {
    type: Boolean,
    default: true
  },
  showGrid: {
    type: Boolean,
    default: true
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  showTypeSwitch: {
    type: Boolean,
    default: false
  },
  showStats: {
    type: Boolean,
    default: false
  },
  colors: {
    type: Array,
    default: () => ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4']
  },
  xAxisLabels: {
    type: Array,
    default: null
  },
  dataSource: {
    type: String,
    default: ''
  },
  errorTitle: {
    type: String,
    default: '图表加载失败'
  },
  errorDescription: {
    type: String,
    default: '无法加载图表数据，请检查网络连接或数据源'
  },
  errorActionText: {
    type: String,
    default: '重试'
  }
})

const emit = defineEmits([
  'chart-click',
  'chart-ready',
  'type-change',
  'retry'
])

// 响应式状态
const chartContainer = ref(null)
const chartType = ref(props.type)
const hiddenSeries = ref([])
const tooltipData = ref(null)
const tooltipPosition = ref({ x: 0, y: 0 })

// 计算属性
const chartClasses = computed(() => ({
  'stats-chart': true,
  'stats-chart--loading': props.loading,
  'stats-chart--error': props.error,
  [`stats-chart--${chartType.value}`]: true
}))

const chartStyles = computed(() => ({
  width: typeof props.width === 'number' ? `${props.width}px` : props.width
}))

const containerStyles = computed(() => ({
  height: typeof props.height === 'number' ? `${props.height}px` : props.height
}))

const chartTypes = computed(() => [
  { value: 'line', label: '折线图' },
  { value: 'bar', label: '柱状图' },
  { value: 'area', label: '面积图' },
  { value: 'pie', label: '饼图' }
])

const legendItems = computed(() => {
  if (!props.data || !Array.isArray(props.data)) return []
  
  return props.data.map((series, index) => ({
    name: series.name || `系列${index + 1}`,
    color: series.color || props.colors[index % props.colors.length],
    hidden: hiddenSeries.value.includes(index)
  }))
})

const dataPoints = computed(() => {
  if (!props.data) return 0
  
  if (Array.isArray(props.data)) {
    return props.data.reduce((total, series) => {
      return total + (series.data ? series.data.length : 0)
    }, 0)
  }
  
  return Object.keys(props.data).length
})

const chartStats = computed(() => {
  const stats = []
  
  if (props.data && Array.isArray(props.data)) {
    props.data.forEach((series, index) => {
      if (series.data && Array.isArray(series.data)) {
        const values = series.data.filter(v => typeof v === 'number')
        if (values.length > 0) {
          const max = Math.max(...values)
          const min = Math.min(...values)
          const sum = values.reduce((a, b) => a + b, 0)
          const avg = sum / values.length
          
          stats.push({
            label: `${series.name || `系列${index + 1}`} (最大值)`,
            value: max.toFixed(2)
          })
        }
      }
    })
  }
  
  return stats
})

const visibleXAxisLabels = computed(() => {
  if (!props.xAxisLabels) return []
  
  // 根据容器宽度决定显示多少个标签
  const maxLabels = Math.min(props.xAxisLabels.length, 10)
  const step = Math.ceil(props.xAxisLabels.length / maxLabels)
  
  return props.xAxisLabels.filter((_, index) => index % step === 0)
})

const tooltipStyles = computed(() => ({
  left: `${tooltipPosition.value.x}px`,
  top: `${tooltipPosition.value.y}px`,
  display: tooltipData.value ? 'block' : 'none'
}))

// 模拟数据用于占位图
const simulatedPoints = computed(() => {
  const points = []
  const count = 8
  
  for (let i = 0; i < count; i++) {
    points.push({
      x: (i / (count - 1)) * 100,
      y: 20 + Math.random() * 60,
      color: props.colors[0]
    })
  }
  
  return points
})

const simulatedBars = computed(() => {
  const bars = []
  const count = 6
  
  for (let i = 0; i < count; i++) {
    bars.push({
      height: 20 + Math.random() * 60,
      color: props.colors[i % props.colors.length]
    })
  }
  
  return bars
})

const simulatedSlices = computed(() => {
  const slices = [
    { percentage: 30, color: props.colors[0] },
    { percentage: 25, color: props.colors[1] },
    { percentage: 20, color: props.colors[2] },
    { percentage: 15, color: props.colors[3] },
    { percentage: 10, color: props.colors[4] }
  ]
  
  let rotation = 0
  return slices.map(slice => {
    const result = {
      rotation,
      color: slice.color
    }
    rotation += (slice.percentage / 100) * 360
    return result
  })
})

// 方法
const changeChartType = (type) => {
  chartType.value = type
  emit('type-change', type)
}

const toggleLegend = (item) => {
  const index = legendItems.value.findIndex(i => i.name === item.name)
  if (index !== -1) {
    if (hiddenSeries.value.includes(index)) {
      hiddenSeries.value = hiddenSeries.value.filter(i => i !== index)
    } else {
      hiddenSeries.value.push(index)
    }
  }
}

const handleMouseMove = (event) => {
  if (!props.showTooltip || !chartContainer.value) return
  
  const rect = chartContainer.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  // 模拟工具提示数据
  tooltipData.value = {
    title: '模拟数据点',
    items: legendItems.value.slice(0, 3).map(item => ({
      name: item.name,
      color: item.color,
      value: (Math.random() * 100).toFixed(1)
    }))
  }
  
  tooltipPosition.value = {
    x: Math.min(x + 10, rect.width - 200),
    y: Math.min(y + 10, rect.height - 150)
  }
}

const handleMouseLeave = () => {
  tooltipData.value = null
}

const initChart = () => {
  // 这里应该初始化真实的图表库
  // 例如: echarts.init(chartContainer.value)
  emit('chart-ready')
}

// 生命周期
onMounted(() => {
  initChart()
  
  if (chartContainer.value && props.showTooltip) {
    chartContainer.value.addEventListener('mousemove', handleMouseMove)
    chartContainer.value.addEventListener('mouseleave', handleMouseLeave)
  }
})

onUnmounted(() => {
  if (chartContainer.value && props.showTooltip) {
    chartContainer.value.removeEventListener('mousemove', handleMouseMove)
    chartContainer.value.removeEventListener('mouseleave', handleMouseLeave)
  }
})
</script>

<style scoped>
.stats-chart {
  position: relative;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  overflow: hidden;
}

.stats-chart__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: var(--spacing-4) var(--spacing-5);
  border-bottom: 1px solid var(--color-border-light);
}

.stats-chart__header-content {
  flex: 1;
  min-width: 0;
}

.stats-chart__title {
  margin: 0;
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.stats-chart__subtitle {
  margin-top: var(--spacing-1);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.stats-chart__header-actions {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
  align-items: flex-end;
}

.stats-chart__type-switch {
  display: flex;
  gap: var(--spacing-1);
  background-color: var(--color-bg-tertiary);
  padding: var(--spacing-1);
  border-radius: var(--radius-md);
}

.stats-chart__type-button {
  padding: var(--spacing-1) var(--spacing-3);
  border: none;
  background: transparent;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.stats-chart__type-button:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.stats-chart__type-button--active {
  background-color: var(--color-bg-card);
  color: var(--color-text-primary);
  font-weight: 600;
  box-shadow: var(--shadow-sm);
}

.stats-chart__legend {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-2);
  justify-content: flex-end;
}

.stats-chart__legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-1);
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  cursor: pointer;
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
}

.stats-chart__legend-item:hover {
  background-color: var(--color-bg-secondary);
}

.stats-chart__legend-item--hidden {
  opacity: 0.5;
}

.stats-chart__legend-color {
  width: 12px;
  height: 12px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.stats-chart__legend-label {
  white-space: nowrap;
}

.stats-chart__container {
  position: relative;
  padding: var(--spacing-4);
}

.stats-chart__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stats-chart__placeholder-content {
  text-align: center;
  max-width: 300px;
}

.stats-chart__placeholder-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
}

.stats-chart__placeholder-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-4);
}

.stats-chart__placeholder-canvas {
  width: 100%;
  height: 200px;
  background-color: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border);
  overflow: hidden;
  position: relative;
}

.stats-chart__simulation {
  width: 100%;
  height: 100%;
  position: relative;
}

.stats-chart__simulation-line {
  position: relative;
  width: 100%;
  height: 100%;
}

.stats-chart__simulation-point {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transform: translate(-50%, 50%);
}

.stats-chart__simulation-bar {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 100%;
  padding: var(--spacing-4);
}

.stats-chart__simulation-bar-item {
  background-color: var(--color-primary);
  border-radius: var(--radius-sm) var(--radius-sm) 0 0;
  transition: height 1s ease;
}

.stats-chart__simulation-pie {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.stats-chart__simulation-pie-circle {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
}

.stats-chart__simulation-slice {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: 50% 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 50% 100%);
}

.stats-chart__loading {
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

.stats-chart__error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.stats-chart__footer {
  padding: var(--spacing-4) var(--spacing-5);
  border-top: 1px solid var(--color-border-light);
  background-color: var(--color-bg-secondary);
}

.stats-chart__x-axis {
  margin-bottom: var(--spacing-3);
}

.stats-chart__x-axis-labels {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
}

.stats-chart__x-axis-label {
  text-align: center;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stats-chart__stats {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-4);
  margin-bottom: var(--spacing-3);
}

.stats-chart__stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.stats-chart__stat-label {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: 2px;
}

.stats-chart__stat-value {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
}

.stats-chart__source {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  text-align: center;
}

.stats-chart__source-label {
  margin-right: var(--spacing-1);
}

.stats-chart__source-name {
  font-weight: 600;
}

.stats-chart__tooltip {
  position: absolute;
  z-index: 100;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  border: 1px solid var(--color-border);
  padding: var(--spacing-3);
  min-width: 180px;
  pointer-events: none;
}

.stats-chart__tooltip-header {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-2);
  padding-bottom: var(--spacing-2);
  border-bottom: 1px solid var(--color-border-light);
}

.stats-chart__tooltip-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2);
}

.stats-chart__tooltip-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-2);
}

.stats-chart__tooltip-color {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-sm);
  flex-shrink: 0;
}

.stats-chart__tooltip-name {
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.stats-chart__tooltip-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-left: auto;
}

/* 响应式 */
@media (max-width: 768px) {
  .stats-chart__header {
    flex-direction: column;
    gap: var(--spacing-3);
  }
  
  .stats-chart__header-actions {
    width: 100%;
    align-items: flex-start;
  }
  
  .stats-chart__type-switch {
    width: 100%;
    justify-content: space-between;
  }
  
  .stats-chart__legend {
    justify-content: flex-start;
  }
  
  .stats-chart__stats {
    justify-content: center;
  }
}
</style>