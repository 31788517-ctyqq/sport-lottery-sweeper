<template>
  <div class="bar-chart-container">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-actions" v-if="showActions">
        <select v-model="selectedGroup" @change="handleGroupChange" v-if="grouped">
          <option value="stacked">堆叠显示</option>
          <option value="grouped">分组显示</option>
        </select>
        <button @click="toggleHorizontal" title="切换方向">
          <i class="fas fa-exchange-alt"></i>
        </button>
      </div>
    </div>
    
    <div class="chart-wrapper" :style="{ height: height + 'px' }">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <div class="chart-summary" v-if="showSummary">
      <div class="summary-item" v-for="item in summaryData" :key="item.label">
        <span class="summary-label">{{ item.label }}</span>
        <span class="summary-value">{{ formatValue(item.value) }}</span>
        <span class="summary-change" :class="getChangeClass(item.change)">
          {{ formatChange(item.change) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

Chart.register(...registerables)

const props = defineProps({
  // 数据配置
  data: {
    type: Object,
    default: () => ({ labels: [], datasets: [] })
  },
  title: String,
  height: {
    type: Number,
    default: 350
  },
  
  // 显示配置
  showActions: {
    type: Boolean,
    default: true
  },
  showSummary: {
    type: Boolean,
    default: true
  },
  horizontal: {
    type: Boolean,
    default: false
  },
  stacked: {
    type: Boolean,
    default: false
  },
  grouped: {
    type: Boolean,
    default: false
  },
  
  // 样式配置
  colors: {
    type: Array,
    default: () => [
      'rgba(54, 162, 235, 0.8)',
      'rgba(255, 99, 132, 0.8)',
      'rgba(75, 192, 192, 0.8)',
      'rgba(255, 159, 64, 0.8)',
      'rgba(153, 102, 255, 0.8)'
    ]
  },
  
  // 数值格式
  valueFormatter: {
    type: Function,
    default: (value) => value.toLocaleString()
  },
  currency: String,
  percentage: Boolean,
  
  // 动画
  animation: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'bar-click',
  'chart-loaded',
  'direction-change'
])

// 图表实例
const chartCanvas = ref(null)
let chartInstance = null

// 状态
const selectedGroup = ref('stacked')
const isHorizontal = ref(props.horizontal)

// 计算属性
const chartOptions = computed(() => ({
  indexAxis: isHorizontal.value ? 'y' : 'x',
  responsive: true,
  maintainAspectRatio: false,
  animation: props.animation ? {
    duration: 800,
    easing: 'easeOutQuart'
  } : false,
  
  plugins: {
    legend: {
      position: 'top',
      labels: {
        padding: 20,
        usePointStyle: true,
        pointStyle: 'rectRounded'
      }
    },
    tooltip: {
      callbacks: {
        label: (context) => {
          let label = context.dataset.label || ''
          let value = context.parsed[isHorizontal.value ? 'x' : 'y']
          
          if (props.currency) {
            return `${label}: ${props.currency}${props.valueFormatter(value)}`
          } else if (props.percentage) {
            return `${label}: ${props.valueFormatter(value)}%`
          }
          return `${label}: ${props.valueFormatter(value)}`
        }
      }
    }
  },
  
  scales: {
    x: {
      stacked: props.stacked && !isHorizontal.value,
      grid: {
        color: 'rgba(200, 200, 200, 0.1)'
      },
      ticks: {
        color: '#666'
      }
    },
    y: {
      stacked: props.stacked && isHorizontal.value,
      beginAtZero: true,
      grid: {
        color: 'rgba(200, 200, 200, 0.1)'
      },
      ticks: {
        color: '#666',
        callback: (value) => {
          if (props.currency) {
            return `${props.currency}${props.valueFormatter(value)}`
          } else if (props.percentage) {
            return `${props.valueFormatter(value)}%`
          }
          return props.valueFormatter(value)
        }
      }
    }
  },
  
  onClick: (event, elements) => {
    if (elements.length > 0) {
      const element = elements[0]
      emit('bar-click', {
        datasetIndex: element.datasetIndex,
        index: element.index,
        label: chartInstance.data.labels[element.index],
        value: chartInstance.data.datasets[element.datasetIndex].data[element.index]
      })
    }
  }
}))

const summaryData = computed(() => {
  if (!props.data.datasets || props.data.datasets.length === 0) return []
  
  return props.data.datasets.map((dataset, index) => {
    const data = dataset.data || []
    const total = data.reduce((sum, val) => sum + val, 0)
    const avg = data.length > 0 ? total / data.length : 0
    const max = Math.max(...data)
    const min = Math.min(...data)
    
    return {
      label: dataset.label,
      value: total,
      avg,
      max,
      min,
      count: data.length,
      change: dataset.change || 0
    }
  })
})

// 生命周期
onMounted(() => {
  initializeChart()
})

onBeforeUnmount(() => {
  destroyChart()
})

// 监听
watch(() => [props.data, isHorizontal.value], () => {
  updateChart()
}, { deep: true })

// 方法
const initializeChart = () => {
  if (!chartCanvas.value) return
  
  try {
    const ctx = chartCanvas.value.getContext('2d')
    
    // 准备数据
    const datasets = props.data.datasets.map((dataset, index) => ({
      label: dataset.label,
      data: dataset.data,
      backgroundColor: dataset.backgroundColor || 
        props.colors[index % props.colors.length],
      borderColor: dataset.borderColor || '#fff',
      borderWidth: 2,
      borderRadius: 4,
      borderSkipped: false,
      ...dataset
    }))
    
    chartInstance = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: props.data.labels,
        datasets
      },
      options: chartOptions.value
    })
    
    emit('chart-loaded', chartInstance)
  } catch (error) {
    console.error('柱状图初始化失败:', error)
  }
}

const updateChart = () => {
  if (!chartInstance) return
  
  chartInstance.options = chartOptions.value
  chartInstance.update()
}

const destroyChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

const toggleHorizontal = () => {
  isHorizontal.value = !isHorizontal.value
  emit('direction-change', isHorizontal.value)
}

const handleGroupChange = () => {
  if (chartInstance) {
    chartInstance.options.scales.x.stacked = selectedGroup.value === 'stacked' && !isHorizontal.value
    chartInstance.options.scales.y.stacked = selectedGroup.value === 'stacked' && isHorizontal.value
    chartInstance.update()
  }
}

const formatValue = (value) => {
  if (props.currency) {
    return `${props.currency}${props.valueFormatter(value)}`
  } else if (props.percentage) {
    return `${props.valueFormatter(value)}%`
  }
  return props.valueFormatter(value)
}

const formatChange = (change) => {
  if (change > 0) {
    return `+${change.toFixed(1)}%`
  } else if (change < 0) {
    return `${change.toFixed(1)}%`
  }
  return '0%'
}

const getChangeClass = (change) => {
  if (change > 0) return 'positive'
  if (change < 0) return 'negative'
  return 'neutral'
}

// 公开方法
defineExpose({
  getChartInstance: () => chartInstance,
  toggleDirection: toggleHorizontal,
  exportChart: () => {
    if (chartInstance) {
      const image = chartInstance.toBase64Image()
      const link = document.createElement('a')
      link.href = image
      link.download = `柱状图_${props.title || 'chart'}_${new Date().toISOString().slice(0, 10)}.png`
      link.click()
      return image
    }
  }
})
</script>

<style scoped>
.bar-chart-container {
  background: white;
  border-radius: 10px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  padding: 20px;
  transition: all 0.3s ease;
}

.bar-chart-container:hover {
  box-shadow: 0 6px 30px rgba(0, 0, 0, 0.12);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.chart-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.chart-actions select {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  color: #333;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.chart-actions select:hover {
  border-color: #409eff;
}

.chart-actions select:focus {
  outline: none;
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.chart-actions button {
  width: 36px;
  height: 36px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  color: #666;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.chart-actions button:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.chart-wrapper {
  position: relative;
  width: 100%;
}

.chart-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.summary-item {
  display: flex;
  flex-direction: column;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.summary-item:hover {
  background: #f0f7ff;
  transform: translateY(-2px);
}

.summary-label {
  font-size: 13px;
  color: #666;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.summary-change {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 10px;
  display: inline-block;
  width: fit-content;
}

.summary-change.positive {
  background: rgba(76, 175, 80, 0.1);
  color: #4caf50;
}

.summary-change.negative {
  background: rgba(244, 67, 54, 0.1);
  color: #f44336;
}

.summary-change.neutral {
  background: rgba(158, 158, 158, 0.1);
  color: #9e9e9e;
}

@media (max-width: 768px) {
  .bar-chart-container {
    padding: 16px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chart-actions {
    align-self: stretch;
    justify-content: space-between;
  }
  
  .chart-summary {
    grid-template-columns: 1fr;
  }
}
</style>