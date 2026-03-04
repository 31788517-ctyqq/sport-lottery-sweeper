<template>
  <div class="line-chart-container">
    <div class="chart-header" v-if="title || showControls">
      <h3 v-if="title">{{ title }}</h3>
      <div class="chart-controls" v-if="showControls">
        <button @click="zoomIn" title="放大">
          <i class="fas fa-search-plus"></i>
        </button>
        <button @click="zoomOut" title="缩小">
          <i class="fas fa-search-minus"></i>
        </button>
        <button @click="resetView" title="重置视图">
          <i class="fas fa-redo"></i>
        </button>
        <button @click="exportChart" title="导出图表">
          <i class="fas fa-download"></i>
        </button>
      </div>
    </div>
    
    <div class="chart-wrapper" :style="{ height: height + 'px' }">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <div class="chart-legend" v-if="showLegend && legendData.length > 0">
      <div 
        v-for="(item, index) in legendData" 
        :key="index" 
        class="legend-item"
        @click="toggleDataset(index)"
      >
        <span 
          class="legend-color" 
          :style="{ backgroundColor: item.color }"
        ></span>
        <span class="legend-label">{{ item.label }}</span>
        <span class="legend-value" v-if="item.value !== undefined">
          {{ item.value }}
        </span>
      </div>
    </div>
    
    <div class="chart-footer" v-if="showTooltip">
      <div class="tooltip-info" v-if="hoveredData">
        时间: {{ hoveredData.label }} | 值: {{ hoveredData.value }}
      </div>
      <div class="no-data" v-else-if="!data || data.length === 0">
        暂无数据
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import { Chart, registerables } from 'chart.js'
import zoomPlugin from 'chartjs-plugin-zoom'

Chart.register(...registerables, zoomPlugin)

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
  datasets: {
    type: Array,
    default: () => []
  },
  
  // 显示配置
  title: String,
  height: {
    type: Number,
    default: 300
  },
  width: {
    type: Number,
    default: null
  },
  
  // 图表配置
  type: {
    type: String,
    default: 'line'
  },
  colors: {
    type: Array,
    default: () => [
      'rgba(54, 162, 235, 1)',
      'rgba(255, 99, 132, 1)',
      'rgba(75, 192, 192, 1)',
      'rgba(255, 159, 64, 1)',
      'rgba(153, 102, 255, 1)'
    ]
  },
  
  // 功能配置
  showControls: {
    type: Boolean,
    default: true
  },
  showLegend: {
    type: Boolean,
    default: true
  },
  showTooltip: {
    type: Boolean,
    default: true
  },
  responsive: {
    type: Boolean,
    default: true
  },
  
  // 动画配置
  animation: {
    type: Boolean,
    default: true
  },
  animationDuration: {
    type: Number,
    default: 1000
  },
  
  // 交互配置
  zoomEnabled: {
    type: Boolean,
    default: true
  },
  panEnabled: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'chart-click',
  'chart-hover',
  'chart-export',
  'chart-loaded',
  'chart-error'
])

// 图表实例
const chartCanvas = ref(null)
let chartInstance = null

// 状态
const hoveredData = ref(null)
const isZoomed = ref(false)

// 计算属性
const chartData = computed(() => {
  if (props.datasets && props.datasets.length > 0) {
    return {
      labels: props.labels,
      datasets: props.datasets.map((dataset, index) => ({
        label: dataset.label || `数据集 ${index + 1}`,
        data: dataset.data || [],
        borderColor: dataset.borderColor || props.colors[index % props.colors.length],
        backgroundColor: dataset.backgroundColor || 
          props.colors[index % props.colors.length].replace('1)', '0.2)'),
        borderWidth: dataset.borderWidth || 2,
        pointRadius: dataset.pointRadius || 3,
        pointHoverRadius: dataset.pointHoverRadius || 6,
        tension: dataset.tension || 0.3,
        fill: dataset.fill || false,
        showLine: dataset.showLine !== undefined ? dataset.showLine : true,
        ...dataset
      }))
    }
  } else {
    return {
      labels: props.labels,
      datasets: [{
        label: props.title || '数据',
        data: props.data,
        borderColor: props.colors[0],
        backgroundColor: props.colors[0].replace('1)', '0.2)'),
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 6,
        tension: 0.3,
        fill: false
      }]
    }
  }
})

const legendData = computed(() => {
  if (!chartInstance || !props.showLegend) return []
  
  const datasets = chartInstance.data.datasets
  return datasets.map((dataset, index) => ({
    label: dataset.label,
    color: dataset.borderColor || dataset.backgroundColor,
    value: dataset.data?.length > 0 
      ? dataset.data[dataset.data.length - 1]
      : undefined,
    hidden: !chartInstance.isDatasetVisible(index)
  }))
})

// 图表配置
const chartOptions = computed(() => ({
  responsive: props.responsive,
  maintainAspectRatio: false,
  animation: props.animation ? {
    duration: props.animationDuration,
    easing: 'easeInOutQuart'
  } : false,
  
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: props.showTooltip,
      mode: 'index',
      intersect: false,
      callbacks: {
        label: (context) => {
          const label = context.dataset.label || ''
          const value = context.parsed.y
          return `${label}: ${value}`
        }
      }
    },
    zoom: props.zoomEnabled ? {
      pan: {
        enabled: props.panEnabled,
        mode: 'xy',
        modifierKey: 'ctrl'
      },
      zoom: {
        wheel: {
          enabled: true,
        },
        pinch: {
          enabled: true
        },
        mode: 'xy',
        onZoomComplete: ({ chart }) => {
          isZoomed.value = true
        }
      }
    } : {}
  },
  
  scales: {
    x: {
      grid: {
        color: 'rgba(200, 200, 200, 0.2)'
      },
      ticks: {
        color: '#666',
        maxRotation: 45,
        minRotation: 0
      }
    },
    y: {
      beginAtZero: props.datasets?.some(d => Math.min(...(d.data || [])) >= 0) || 
                  (props.data && Math.min(...props.data) >= 0),
      grid: {
        color: 'rgba(200, 200, 200, 0.2)'
      },
      ticks: {
        color: '#666'
      }
    }
  },
  
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  },
  
  onClick: (event, elements) => {
    if (elements.length > 0) {
      const element = elements[0]
      const datasetIndex = element.datasetIndex
      const index = element.index
      const dataset = chartInstance.data.datasets[datasetIndex]
      const value = dataset.data[index]
      const label = chartInstance.data.labels[index]
      
      emit('chart-click', {
        datasetIndex,
        index,
        label,
        value,
        dataset: dataset.label
      })
    }
  },
  
  onHover: (event, elements) => {
    if (elements.length > 0) {
      const element = elements[0]
      const datasetIndex = element.datasetIndex
      const index = element.index
      const dataset = chartInstance.data.datasets[datasetIndex]
      const value = dataset.data[index]
      const label = chartInstance.data.labels[index]
      
      hoveredData.value = { label, value, dataset: dataset.label }
      emit('chart-hover', {
        datasetIndex,
        index,
        label,
        value,
        dataset: dataset.label
      })
    } else {
      hoveredData.value = null
    }
  }
}))

// 生命周期
onMounted(() => {
  initializeChart()
})

onBeforeUnmount(() => {
  destroyChart()
})

// 监听数据变化
watch(() => [props.data, props.labels, props.datasets], () => {
  updateChart()
}, { deep: true })

// 方法
const initializeChart = () => {
  if (!chartCanvas.value) return
  
  try {
    const ctx = chartCanvas.value.getContext('2d')
    chartInstance = new Chart(ctx, {
      type: props.type,
      data: chartData.value,
      options: chartOptions.value
    })
    
    emit('chart-loaded', chartInstance)
  } catch (error) {
    console.error('图表初始化失败:', error)
    emit('chart-error', error)
  }
}

const updateChart = () => {
  if (!chartInstance) return
  
  try {
    chartInstance.data = chartData.value
    chartInstance.options = chartOptions.value
    chartInstance.update('none')
  } catch (error) {
    console.error('图表更新失败:', error)
    emit('chart-error', error)
  }
}

const destroyChart = () => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}

// 交互方法
const zoomIn = () => {
  if (chartInstance) {
    chartInstance.zoom(1.1)
  }
}

const zoomOut = () => {
  if (chartInstance) {
    chartInstance.zoom(0.9)
  }
}

const resetView = () => {
  if (chartInstance) {
    chartInstance.resetZoom()
    isZoomed.value = false
  }
}

const exportChart = () => {
  if (!chartInstance) return
  
  const image = chartInstance.toBase64Image()
  const link = document.createElement('a')
  link.href = image
  link.download = `折线图_${new Date().toISOString().slice(0, 10)}.png`
  link.click()
  
  emit('chart-export', { image, type: 'png' })
}

const toggleDataset = (datasetIndex) => {
  if (chartInstance) {
    const meta = chartInstance.getDatasetMeta(datasetIndex)
    meta.hidden = meta.hidden === null ? !chartInstance.data.datasets[datasetIndex].hidden : !meta.hidden
    chartInstance.update()
  }
}

// 公开方法
defineExpose({
  getChartInstance: () => chartInstance,
  updateData: (newData) => {
    if (chartInstance) {
      chartInstance.data = newData
      chartInstance.update()
    }
  },
  exportAsImage: exportChart,
  resetZoom: resetView
})
</script>

<style scoped>
.line-chart-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  background: white;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  transition: all 0.3s ease;
}

.line-chart-container:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-controls button {
  width: 32px;
  height: 32px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: white;
  color: #606266;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.chart-controls button:hover {
  border-color: #409eff;
  color: #409eff;
  background: #ecf5ff;
}

.chart-wrapper {
  position: relative;
  width: 100%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 16px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}

.legend-item:hover {
  background: #f0f0f0;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  display: inline-block;
}

.legend-label {
  font-size: 13px;
  color: #606266;
}

.legend-value {
  font-size: 13px;
  font-weight: 600;
  color: #303133;
  margin-left: 4px;
}

.chart-footer {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e4e7ed;
}

.tooltip-info {
  font-size: 13px;
  color: #909399;
  text-align: center;
}

.no-data {
  text-align: center;
  color: #c0c4cc;
  font-style: italic;
  padding: 20px;
}

@media (max-width: 768px) {
  .line-chart-container {
    padding: 12px;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .chart-controls {
    align-self: flex-end;
  }
}
</style>