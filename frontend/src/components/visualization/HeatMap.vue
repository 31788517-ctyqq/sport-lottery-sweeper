<template>
  <div class="heatmap-container">
    <div class="heatmap-header">
      <div class="header-info">
        <h3>{{ title }}</h3>
        <div class="header-stats" v-if="showStats">
          <span class="stat-item">
            最小值: <strong>{{ formatValue(minValue) }}</strong>
          </span>
          <span class="stat-item">
            最大值: <strong>{{ formatValue(maxValue) }}</strong>
          </span>
          <span class="stat-item">
            平均值: <strong>{{ formatValue(avgValue) }}</strong>
          </span>
        </div>
      </div>
      
      <div class="header-controls" v-if="showControls">
        <div class="color-scale-selector">
          <span>配色方案:</span>
          <select v-model="selectedColorScale" @change="updateColorScale">
            <option value="viridis">Viridis</option>
            <option value="plasma">Plasma</option>
            <option value="inferno">Inferno</option>
            <option value="magma">Magma</option>
            <option value="coolwarm">冷暖色</option>
            <option value="rdbu">红蓝</option>
            <option value="ylorrd">黄橙红</option>
          </select>
        </div>
        
        <div class="cell-size-control">
          <span>单元格大小:</span>
          <input 
            type="range" 
            v-model.number="cellSize" 
            min="20" 
            max="80" 
            step="5"
            @input="updateCellSize"
          >
          <span>{{ cellSize }}px</span>
        </div>
      </div>
    </div>
    
    <div class="heatmap-main">
      <div class="y-axis-labels" v-if="showAxes">
        <div 
          v-for="(label, index) in yLabels" 
          :key="'y-' + index"
          class="y-label"
        >
          {{ label }}
        </div>
      </div>
      
      <div class="heatmap-content">
        <div class="x-axis-labels" v-if="showAxes">
          <div 
            v-for="(label, index) in xLabels" 
            :key="'x-' + index"
            class="x-label"
          >
            {{ label }}
          </div>
        </div>
        
        <div class="heatmap-grid">
          <div 
            v-for="(row, rowIndex) in normalizedData" 
            :key="'row-' + rowIndex"
            class="heatmap-row"
          >
            <div
              v-for="(cell, colIndex) in row"
              :key="'cell-' + rowIndex + '-' + colIndex"
              class="heatmap-cell"
              :style="getCellStyle(cell.value)"
              :title="getCellTooltip(rowIndex, colIndex, cell.value)"
              @click="handleCellClick(rowIndex, colIndex, cell.value)"
              @mouseenter="handleCellHover(rowIndex, colIndex, cell.value)"
              @mouseleave="handleCellLeave"
            >
              <span class="cell-value" v-if="showValues">
                {{ formatCellValue(cell.value) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="heatmap-footer">
      <div class="color-scale" v-if="showColorScale">
        <div class="scale-gradient" :style="colorScaleStyle"></div>
        <div class="scale-labels">
          <span>{{ formatValue(minValue) }}</span>
          <span>{{ formatValue((minValue + maxValue) / 2) }}</span>
          <span>{{ formatValue(maxValue) }}</span>
        </div>
      </div>
      
      <div class="footer-info" v-if="hoveredCell">
        <div class="info-item">
          <span class="info-label">位置:</span>
          <span class="info-value">
            {{ yLabels[hoveredCell.row] }} × {{ xLabels[hoveredCell.column] }}
          </span>
        </div>
        <div class="info-item">
          <span class="info-label">值:</span>
          <span class="info-value">{{ formatValue(hoveredCell.value) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">百分比:</span>
          <span class="info-value">{{ hoveredCell.percentage }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  // 数据配置
  data: {
    type: Array,
    default: () => []
  },
  xLabels: {
    type: Array,
    default: () => []
  },
  yLabels: {
    type: Array,
    default: () => []
  },
  title: String,
  
  // 显示配置
  showStats: {
    type: Boolean,
    default: true
  },
  showControls: {
    type: Boolean,
    default: true
  },
  showAxes: {
    type: Boolean,
    default: true
  },
  showValues: {
    type: Boolean,
    default: false
  },
  showColorScale: {
    type: Boolean,
    default: true
  },
  
  // 样式配置
  colorScale: {
    type: String,
    default: 'viridis'
  },
  cellSize: {
    type: Number,
    default: 40
  },
  borderRadius: {
    type: Number,
    default: 4
  },
  
  // 数值配置
  minValue: {
    type: Number,
    default: null
  },
  maxValue: {
    type: Number,
    default: null
  },
  
  // 格式配置
  valueFormatter: {
    type: Function,
    default: (value) => {
      if (value >= 1000) {
        return (value / 1000).toFixed(1) + 'k'
      }
      return value.toFixed(1)
    }
  },
  percentage: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'cell-click',
  'cell-hover',
  'cell-leave',
  'color-scale-change'
])

// 状态
const selectedColorScale = ref(props.colorScale)
const cellSize = ref(props.cellSize)
const hoveredCell = ref(null)

// 预定义的色阶方案
const colorScales = {
  viridis: [
    '#440154', '#482878', '#3e4989', '#31688e', '#26828e',
    '#1f9e89', '#35b779', '#6ece58', '#b5de2b', '#fde725'
  ],
  plasma: [
    '#0d0887', '#41049d', '#6a00a8', '#8f0da4', '#b12a90',
    '#cc4778', '#e16462', '#f2844b', '#fca636', '#f0f921'
  ],
  inferno: [
    '#000004', '#1c0d3e', '#4a0c6b', '#781c6d', '#a52c60',
    '#cf4446', '#ed6925', '#fb9b06', '#f7d13d', '#fcffa4'
  ],
  magma: [
    '#000004', '#180f3d', '#440f76', '#721f81', '#9e2f7f',
    '#cd4071', '#f1605d', '#fd9668', '#feca8d', '#fcfdbf'
  ],
  coolwarm: [
    '#3b4cc0', '#5b7bd5', '#7da7ea', '#abd3f5', '#dceef7',
    '#f6e5c8', '#f3b987', '#e88c4d', '#d95a30', '#b40426'
  ],
  rdbu: [
    '#67001f', '#b2182b', '#d6604d', '#f4a582', '#fddbc7',
    '#d1e5f0', '#92c5de', '#4393c3', '#2166ac', '#053061'
  ],
  ylorrd: [
    '#ffffcc', '#ffeda0', '#fed976', '#feb24c', '#fd8d3c',
    '#fc4e2a', '#e31a1c', '#bd0026', '#800026', '#400013'
  ]
}

// 计算属性
const flatData = computed(() => {
  if (!props.data || !Array.isArray(props.data)) return []
  return props.data.flat().filter(val => val !== null && val !== undefined)
})

const computedMinValue = computed(() => {
  if (props.minValue !== null && props.minValue !== undefined) {
    return props.minValue
  }
  if (flatData.value.length === 0) return 0
  return Math.min(...flatData.value)
})

const computedMaxValue = computed(() => {
  if (props.maxValue !== null && props.maxValue !== undefined) {
    return props.maxValue
  }
  if (flatData.value.length === 0) return 1
  return Math.max(...flatData.value)
})

const avgValue = computed(() => {
  if (flatData.value.length === 0) return 0
  const sum = flatData.value.reduce((a, b) => a + b, 0)
  return sum / flatData.value.length
})

const normalizedData = computed(() => {
  if (!props.data || !Array.isArray(props.data)) return []
  
  const min = computedMinValue.value
  const max = computedMaxValue.value
  const range = max - min
  
  return props.data.map(row => 
    row.map(value => {
      if (value === null || value === undefined) {
        return { value: null, normalized: 0 }
      }
      const normalized = range > 0 ? (value - min) / range : 0.5
      return { value, normalized }
    })
  )
})

const colorScaleStyle = computed(() => {
  const colors = colorScales[selectedColorScale.value] || colorScales.viridis
  const gradient = colors.join(', ')
  return {
    background: `linear-gradient(to right, ${gradient})`
  }
})

// 方法
const getCellStyle = (value) => {
  if (value === null || value === undefined) {
    return {
      backgroundColor: '#f0f0f0',
      borderRadius: `${props.borderRadius}px`,
      width: `${cellSize.value}px`,
      height: `${cellSize.value}px`
    }
  }
  
  const min = computedMinValue.value
  const max = computedMaxValue.value
  const range = max - min
  const normalized = range > 0 ? (value - min) / range : 0.5
  
  const colors = colorScales[selectedColorScale.value] || colorScales.viridis
  const colorIndex = Math.floor(normalized * (colors.length - 1))
  const color = colors[colorIndex]
  
  return {
    backgroundColor: color,
    borderRadius: `${props.borderRadius}px`,
    width: `${cellSize.value}px`,
    height: `${cellSize.value}px`,
    transition: 'all 0.3s ease',
    transform: hoveredCell.value ? 'scale(1.05)' : 'scale(1)'
  }
}

const getCellTooltip = (rowIndex, colIndex, value) => {
  if (value === null || value === undefined) return '无数据'
  
  const xLabel = props.xLabels[colIndex] || `列 ${colIndex + 1}`
  const yLabel = props.yLabels[rowIndex] || `行 ${rowIndex + 1}`
  const formattedValue = formatValue(value)
  
  return `${yLabel} - ${xLabel}: ${formattedValue}`
}

const formatValue = (value) => {
  if (value === null || value === undefined) return 'N/A'
  
  if (props.percentage) {
    return `${(value * 100).toFixed(1)}%`
  }
  
  return props.valueFormatter(value)
}

const formatCellValue = (value) => {
  if (value === null || value === undefined) return ''
  
  if (props.percentage) {
    return `${(value * 100).toFixed(0)}%`
  }
  
  return props.valueFormatter(value)
}

const handleCellClick = (rowIndex, colIndex, value) => {
  if (value === null || value === undefined) return
  
  const xLabel = props.xLabels[colIndex] || `列 ${colIndex + 1}`
  const yLabel = props.yLabels[rowIndex] || `行 ${rowIndex + 1}`
  
  emit('cell-click', {
    row: rowIndex,
    column: colIndex,
    value,
    xLabel,
    yLabel,
    percentage: ((value - computedMinValue.value) / (computedMaxValue.value - computedMinValue.value) * 100).toFixed(1)
  })
}

const handleCellHover = (rowIndex, colIndex, value) => {
  if (value === null || value === undefined) {
    hoveredCell.value = null
    return
  }
  
  const percentage = ((value - computedMinValue.value) / (computedMaxValue.value - computedMinValue.value) * 100).toFixed(1)
  
  hoveredCell.value = {
    row: rowIndex,
    column: colIndex,
    value,
    percentage,
    xLabel: props.xLabels[colIndex] || `列 ${colIndex + 1}`,
    yLabel: props.yLabels[rowIndex] || `行 ${rowIndex + 1}`
  }
  
  emit('cell-hover', hoveredCell.value)
}

const handleCellLeave = () => {
  hoveredCell.value = null
  emit('cell-leave')
}

const updateColorScale = () => {
  emit('color-scale-change', selectedColorScale.value)
}

const updateCellSize = () => {
  // 更新逻辑在样式绑定中自动处理
}

// 公开方法
defineExpose({
  exportAsImage: () => {
    const container = document.querySelector('.heatmap-grid')
    if (!container) return null
    
    // 创建一个canvas来绘制热力图
    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    
    const rows = normalizedData.value.length
    const cols = rows > 0 ? normalizedData.value[0].length : 0
    
    canvas.width = cols * (cellSize.value + 2)
    canvas.height = rows * (cellSize.value + 2)
    
    // 绘制每个单元格
    normalizedData.value.forEach((row, rowIndex) => {
      row.forEach((cell, colIndex) => {
        const style = getCellStyle(cell.value)
        ctx.fillStyle = style.backgroundColor || '#f0f0f0'
        ctx.fillRect(
          colIndex * (cellSize.value + 2),
          rowIndex * (cellSize.value + 2),
          cellSize.value,
          cellSize.value
        )
        
        // 绘制数值
        if (props.showValues && cell.value !== null && cell.value !== undefined) {
          ctx.fillStyle = cell.value > (computedMaxValue.value + computedMinValue.value) / 2 ? '#fff' : '#000'
          ctx.font = '12px Arial'
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(
            formatCellValue(cell.value),
            colIndex * (cellSize.value + 2) + cellSize.value / 2,
            rowIndex * (cellSize.value + 2) + cellSize.value / 2
          )
        }
      })
    })
    
    return canvas.toDataURL('image/png')
  },
  
  getCellValue: (row, column) => {
    if (normalizedData.value[row] && normalizedData.value[row][column]) {
      return normalizedData.value[row][column].value
    }
    return null
  }
})
</script>

<style scoped>
.heatmap-container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.heatmap-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1a1a1a;
}

.header-stats {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-item {
  font-size: 13px;
  color: #666;
}

.stat-item strong {
  color: #1a1a1a;
  font-weight: 600;
  margin-left: 4px;
}

.header-controls {
  display: flex;
  gap: 24px;
  align-items: center;
  flex-wrap: wrap;
}

.color-scale-selector,
.cell-size-control {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #666;
}

.color-scale-selector select,
.cell-size-control input {
  padding: 4px 8px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  background: white;
  color: #333;
  font-size: 13px;
}

.cell-size-control input {
  width: 80px;
}

.heatmap-main {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.y-axis-labels {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding-top: 20px; /* 对齐x轴标签高度 */
}

.y-label {
  height: v-bind(cellSize + 'px');
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  min-width: 80px;
}

.heatmap-content {
  flex: 1;
  overflow: auto;
}

.x-axis-labels {
  display: flex;
  gap: 2px;
  margin-bottom: 8px;
  padding-left: 20px; /* 对齐y轴标签宽度 */
}

.x-label {
  width: v-bind(cellSize + 'px');
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: #666;
  font-weight: 500;
  text-align: center;
}

.heatmap-grid {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.heatmap-row {
  display: flex;
  gap: 2px;
}

.heatmap-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.heatmap-cell:hover {
  z-index: 2;
  box-shadow: 0 0 0 2px #409eff;
}

.cell-value {
  font-size: 11px;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  pointer-events: none;
}

.heatmap-footer {
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.color-scale {
  margin-bottom: 16px;
}

.scale-gradient {
  height: 20px;
  border-radius: 4px;
  margin-bottom: 4px;
}

.scale-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.footer-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 12px;
  color: #666;
}

.info-value {
  font-size: 13px;
  font-weight: 600;
  color: #1a1a1a;
}

@media (max-width: 768px) {
  .heatmap-header {
    flex-direction: column;
  }
  
  .header-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .heatmap-main {
    flex-direction: column;
  }
  
  .y-axis-labels {
    flex-direction: row;
    overflow-x: auto;
    padding-top: 0;
    padding-bottom: 8px;
  }
  
  .y-label {
    height: auto;
    min-width: 60px;
    justify-content: center;
    padding-right: 0;
  }
  
  .x-axis-labels {
    padding-left: 0;
  }
}
</style>