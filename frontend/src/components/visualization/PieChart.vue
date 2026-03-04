<template>
  <div class="pie-chart-container">
    <div class="chart-header">
      <div class="header-left">
        <h3>{{ title }}</h3>
        <span class="total-value" v-if="showTotal">
          {{ formatTotal }}
        </span>
      </div>
      <div class="header-actions" v-if="showActions">
        <button @click="toggleDonut" title="切换环形图">
          <i :class="donutMode ? 'fas fa-circle' : 'fas fa-dot-circle'"></i>
        </button>
        <button @click="toggleAnimation" title="切换动画">
          <i :class="animationEnabled ? 'fas fa-pause' : 'fas fa-play'"></i>
        </button>
        <button @click="exportChart" title="导出图表">
          <i class="fas fa-download"></i>
        </button>
      </div>
    </div>
    
    <div class="chart-content">
      <div class="chart-main" :style="{ width: chartSize + 'px', height: chartSize + 'px' }">
        <canvas ref="chartCanvas"></canvas>
      </div>
      
      <div class="chart-legend" v-if="showLegend">
        <div 
          v-for="(item, index) in legendItems" 
          :key="index"
          class="legend-item"
          @click="toggleSlice(index)"
          @mouseenter="highlightSlice(index)"
          @mouseleave="resetHighlight"
        >
          <span class="legend-marker" :style="{ backgroundColor: item.color }"></span>
          <div class="legend-info">
            <span class="legend-label">{{ item.label }}</span>
            <div class="legend-details">
              <span class="legend-value">{{ formatValue(item.value) }}</span>
              <span class="legend-percentage">({{ item.percentage }}%)</span>
            </div>
          </div>
          <button 
            class="legend-action"
            @click.stop="focusSlice(index)"
            title="聚焦此部分"
          >
            <i class="fas fa-search-plus"></i>
          </button>
        </div>
      </div>
    </div>
    
    <div class="chart-footer" v-if="showDetails">
      <div class="detail-item" v-for="detail in detailInfo" :key="detail.label">
        <span class="detail-label">{{ detail.label }}</span>
        <span class="detail-value">{{ detail.value }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { Chart, ArcElement, Tooltip, Legend, Title } from 'chart.js'

Chart.register(ArcElement, Tooltip, Legend, Title)

const props = defineProps({
  // 数据配置
  data: {
    type: Array,
    default: () => []
  },
  labels: {
    type: Array,
    default: () => []
  },
  title: String,
  
  // 显示配置
  showTotal: {
    type: Boolean,
    default: true
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showDetails: {
    type: Boolean,
    default: false
  },
  
  // 图表配置
  donut: {
    type: Boolean,
    default: false
  },
  chartSize: {
    type: Number,
    default: 250
  },
  colors: {
    type: Array,
    default: () => [
      '#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de',
      '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc', '#60acfc'
    ]
  },
  
  // 交互配置
  hoverOffset: {
    type: Number,
    default: 10
  },
  cutout: {
    type: String,
    default: '50%'
  },
  
  // 格式配置
  valueFormatter: {
    type: Function,
    default: (value) => value.toLocaleString()
  },
  currency: String,
  
  // 动画配置
  animation: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'slice-click',
  'slice-hover',
  'chart-loaded',
  'chart-exported'
])

// 图表实例
const chartCanvas = ref(null)
let chartInstance = null

// 状态
const donutMode = ref(props.donut)
const animationEnabled = ref(props.animation)
const hoveredIndex = ref(null)

// 计算属性
const chartData = computed(() => ({
  labels: props.labels,
  datasets: [{
    data: props.data,
    backgroundColor: props.colors,
    borderColor: '#ffffff',
    borderWidth: 2,
    hoverBorderWidth: 3,
    hoverOffset: props.hoverOffset,
    hoverBackgroundColor: props.colors.map(color => 
      color.replace(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/, (match, r, g, b) => 
        `rgb(${Math.min(255, parseInt(r) + 20)}, ${Math.min(255, parseInt(g) + 20)}, ${Math.min(255, parseInt(b) + 20)})`
      ).replace(/#([0-9A-F]{2})([0-9A-F]{2})([0-9A-F]{2})/i, (match, r, g, b) => {
        const lighten = (hex, percent) => {
          const num = parseInt(hex, 16)
          const amt = Math.round(2.55 * percent)
          const R = (num >> 16) + amt
          const G = (num >> 8 & 0x00FF) + amt
          const B = (num & 0x0000FF) + amt
          return `#${(
            0x1000000 +
            (R < 255 ? R < 1 ? 0 : R : 255) * 0x10000 +
            (G < 255 ? G < 1 ? 0 : G : 255) * 0x100 +
            (B < 255 ? B < 1 ? 0 : B : 255)
          ).toString(16).slice(1)}`
        }
        return lighten(r + g + b, 20)
      })
    )
  }]
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  animation: animationEnabled.value ? {
    animateRotate: true,
    animateScale: true,
    duration: 1000,
    easing: 'easeInOutQuart'
  } : false,
  
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          const label = context.label || ''
          const value = context.raw || 0
          const total = context.dataset.data.reduce((a, b) => a + b, 0)
          const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0
          
          let formattedValue = props.valueFormatter(value)
          if (props.currency) {
            formattedValue = `${props.currency}${formattedValue}`
          }
          
          return `${label}: ${formattedValue} (${percentage}%)`
        }
      }
    }
  },
  
  cutout: donutMode.value ? props.cutout : 0,
  
  onClick: (event, elements) => {
    if (elements.length > 0) {
      const element = elements[0]
      const index = element.index
      const value = props.data[index]
      const label = props.labels[index]
      
      emit('slice-click', { index, label, value })
    }
  },
  
  onHover: (event, elements) => {
    if (elements.length > 0) {
      const element = elements[0]
      const index = element.index
      hoveredIndex.value = index
      emit('slice-hover', { index, label: props.labels[index], value: props.data[index] })
    } else {
      hoveredIndex.value = null
    }
  }
}))

const totalValue = computed(() => 
  props.data.reduce((sum, value) => sum + value, 0)
)

const formatTotal = computed(() => {
  const formatted = props.valueFormatter(totalValue.value)
  return props.currency ? `${props.currency}${formatted}` : formatted
})

const legendItems = computed(() => {
  if (!props.labels || !props.data) return []
  
  return props.labels.map((label, index) => {
    const value = props.data[index] || 0
    const percentage = totalValue.value > 0 
      ? ((value / totalValue.value) * 100).toFixed(1)
      : '0.0'
    
    return {
      label,
      value,
      percentage,
      color: props.colors[index % props.colors.length],
      hovered: hoveredIndex.value === index
    }
  })
})

const detailInfo = computed(() => {
  if (!props.showDetails) return []
  
  return [
    { label: '数据总数', value: props.data.length },
    { label: '最大值', value: Math.max(...props.data) },
    { label: '最小值', value: Math.min(...props.data) },
    { label: '平均值', value: (totalValue.value / props.data.length).toFixed(1) }
  ]
})

// 生命周期
onMounted(() => {
  initializeChart()
})

onBeforeUnmount(() => {
  destroyChart()
})

// 监听
watch(() => [props.data, props.labels, donutMode.value], () => {
  updateChart()
}, { deep: true })

// 方法
const initializeChart = () => {
  if (!chartCanvas.value) return
  
  try {
    const ctx = chartCanvas.value.getContext('2d')
    chartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: chartData.value,
      options: chartOptions.value
    })
    
    emit('chart-loaded', chartInstance)
  } catch (error) {
    console.error('饼图初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance) return
  
  chartInstance.data = chartData.value
  chartInstance.options = chartOptions.value
  chartInstance.update()
}

const destroyChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const toggleDonut = () => {
  donutMode.value = !donutMode.value
  updateChart()
}

const toggleAnimation = () => {
  animationEnabled.value = !animationEnabled.value
  updateChart()
}

const exportChart = () => {
  if (chartInstance) {
    const image = chartInstance.toBase64Image('image/png', 1)
    const link = document.createElement('a')
    link.href = image
    link.download = `饼图_${props.title || 'chart'}_${new Date().toISOString().slice(0, 10)}.png`
    link.click()
    emit('chart-exported', { image, type: 'png' })
  }
}

const toggleSlice = (index) => {
  if (chartInstance) {
    const meta = chartInstance.getDatasetMeta(0)
    if (meta.data[index]) {
      meta.data[index].hidden = !meta.data[index].hidden
      chartInstance.update()
    }
  }
}

const highlightSlice = (index) => {
  if (chartInstance) {
    chartInstance.setActiveElements([{ datasetIndex: 0, index }])
    chartInstance.update()
  }
}

const resetHighlight = () => {
  if (chartInstance) {
    chartInstance.setActiveElements([])
    chartInstance.update()
  }
}

const focusSlice = (index) => {
  if (chartInstance && chartInstance.data && chartInstance.data.datasets[0]) {
    // 将指定切片移动到前面
    const data = [...chartInstance.data.datasets[0].data]
    const labels = [...chartInstance.data.labels]
    const colors = [...chartInstance.data.datasets[0].backgroundColor]
    
    const targetData = data[index]
    const targetLabel = labels[index]
    const targetColor = colors[index]
    
    data.splice(index, 1)
    labels.splice(index, 1)
    colors.splice(index, 1)
    
    data.unshift(targetData)
    labels.unshift(targetLabel)
    colors.unshift(targetColor)
    
    chartInstance.data.datasets[0].data = data
    chartInstance.data.labels = labels
    chartInstance.data.datasets[0].backgroundColor = colors
    
    chartInstance.update()
  }
}

const formatValue = (value) => {
  const formatted = props.valueFormatter(value)
  return props.currency ? `${props.currency}${formatted}` : formatted
}

// 公开方法
defineExpose({
  getChartInstance: () => chartInstance,
  exportAsImage: exportChart,
  toggleDonutMode: toggleDonut,
  highlightSlice,
  resetHighlight
})
</script>

<style scoped>
.pie-chart-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
}

.pie-chart-container:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-left h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.total-value {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.header-actions button {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #f5f7fa;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.header-actions button:hover {
  background: #409eff;
  color: white;
  transform: translateY(-1px);
}

.chart-content {
  display: flex;
  gap: 32px;
  align-items: center;
  margin-bottom: 24px;
}

@media (max-width: 768px) {
  .chart-content {
    flex-direction: column;
    gap: 24px;
  }
}

.chart-main {
  flex-shrink: 0;
}

.chart-legend {
  flex: 1;
  max-height: 300px;
  overflow-y: auto;
}

.legend-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.legend-item:hover {
  background: #f8f9fa;
  border-color: #e4e7ed;
  transform: translateX(4px);
}

.legend-item.highlighted {
  background: #f0f7ff;
  border-color: #409eff;
}

.legend-marker {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  margin-right: 12px;
  flex-shrink: 0;
}

.legend-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.legend-label {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 2px;
}

.legend-details {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-value {
  font-size: 13px;
  font-weight: 600;
  color: #409eff;
}

.legend-percentage {
  font-size: 12px;
  color: #909399;
}

.legend-action {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: #c0c4cc;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  flex-shrink: 0;
  opacity: 0;
}

.legend-item:hover .legend-action {
  opacity: 1;
}

.legend-action:hover {
  background: #409eff;
  color: white;
}

.chart-footer {
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>