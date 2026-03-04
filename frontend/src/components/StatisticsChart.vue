<template>
  <div class="statistics-chart">
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><TrendCharts /></el-icon>
            {{ title }}
          </span>
          <div class="card-actions">
            <el-select 
              v-model="selectedPeriod" 
              size="small"
              style="width: 120px; margin-right: 8px;"
              @change="handlePeriodChange"
            >
              <el-option label="今日" value="today" />
              <el-option label="本周" value="week" />
              <el-option label="本月" value="month" />
            </el-select>
            <el-button 
              type="primary" 
              :icon="Refresh" 
              circle 
              size="small"
              @click="refreshData"
              :loading="loading"
            />
          </div>
        </div>
      </template>

      <!-- 图表区域 -->
      <div class="chart-container">
        <div v-if="loading" class="loading-container">
          <el-skeleton animated :rows="8" />
        </div>
        
        <div v-else-if="!chartData.length" class="empty-container">
          <el-empty description="暂无数据">
            <el-button type="primary" @click="refreshData">
              <el-icon><Refresh /></el-icon>
              刷新数据
            </el-button>
          </el-empty>
        </div>

        <div v-else class="chart-content">
          <!-- 柱状图 -->
          <div v-if="chartType === 'bar'" class="bar-chart">
            <div class="chart-bars">
              <div 
                v-for="item in chartData" 
                :key="item.label"
                class="chart-bar-item"
              >
                <div class="bar-label">
                  {{ item.label }}
                </div>
                <div class="bar-wrapper">
                  <div 
                    class="bar"
                    :style="{ height: getBarHeight(item.value) + '%' }"
                    :class="getBarClass(item.value)"
                  >
                    <span class="bar-value">{{ item.value }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 折线图 -->
          <div v-else-if="chartType === 'line'" class="line-chart">
            <svg class="line-svg" viewBox="0 0 400 200">
              <!-- 网格线 -->
              <defs>
                <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 20" fill="none" stroke="var(--el-border-color-lighter)" stroke-width="1"/>
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#grid)" />
              
              <!-- 折线 -->
              <polyline
                :points="getLinePoints()"
                fill="none"
                stroke="var(--el-color-primary)"
                stroke-width="2"
              />
              
              <!-- 数据点 -->
              <circle
                v-for="(point, index) in getLinePointsArray()"
                :key="index"
                :cx="point.x"
                :cy="point.y"
                r="3"
                fill="var(--el-color-primary)"
                class="data-point"
              />
            </svg>
            
            <!-- X轴标签 -->
            <div class="axis-labels">
              <div 
                v-for="(item, index) in chartData" 
                :key="index"
                class="axis-label"
                :style="{ left: (index * 100 / (chartData.length - 1)) + '%' }"
              >
                {{ item.label }}
              </div>
            </div>
          </div>

          <!-- 饼图 -->
          <div v-else-if="chartType === 'pie'" class="pie-chart">
            <div class="pie-container">
              <svg class="pie-svg" viewBox="0 0 200 200">
                <g v-for="(slice, index) in pieSlices" :key="index">
                  <path
                    :d="slice.path"
                    :fill="slice.color"
                    class="pie-slice"
                  />
                </g>
              </svg>
              <div class="pie-center">
                <div class="total-value">{{ totalValue }}</div>
                <div class="total-label">总计</div>
              </div>
            </div>
            
            <!-- 图例 -->
            <div class="pie-legend">
              <div 
                v-for="(item, index) in chartData" 
                :key="index"
                class="legend-item"
              >
                <div 
                  class="legend-color"
                  :style="{ backgroundColor: getColor(index) }"
                ></div>
                <span class="legend-label">{{ item.label }}</span>
                <span class="legend-value">{{ item.value }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计摘要 -->
      <div v-if="chartData.length" class="chart-summary">
        <el-row :gutter="16">
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">总计</div>
              <div class="summary-value highlight">{{ totalValue }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">平均值</div>
              <div class="summary-value">{{ averageValue }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">最大值</div>
              <div class="summary-value success">{{ maxValue }}</div>
            </div>
          </el-col>
          <el-col :span="6">
            <div class="summary-item">
              <div class="summary-label">最小值</div>
              <div class="summary-value warning">{{ minValue }}</div>
            </div>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { TrendCharts, Refresh } from '@element-plus/icons-vue'
import { getDashboardStats } from '@/api/example.js'

// Props
const props = defineProps({
  title: {
    type: String,
    default: '数据统计图表'
  },
  chartType: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'line', 'pie'].includes(value)
  },
  dataType: {
    type: String,
    default: 'dashboard' // dashboard, intelligence, custom
  },
  data: {
    type: Array,
    default: () => []
  },
  colors: {
    type: Array,
    default: () => [
      '#409eff', '#67c23a', '#e6a23c', '#f56c6c', 
      '#909399', '#c06c84', '#6c5ce7', '#a29bfe'
    ]
  }
})

// Emits
const emit = defineEmits(['period-change', 'refresh'])

// 响应式数据
const loading = ref(false)
const selectedPeriod = ref('today')
const rawData = ref([])

// 计算属性 - 图表数据
const chartData = computed(() => {
  if (props.data.length) {
    return props.data
  }
  
  // 根据数据类型生成示例数据
  switch (props.dataType) {
    case 'dashboard':
      return generateDashboardData()
    case 'intelligence':
      return generateIntelligenceData()
    default:
      return generateDefaultData()
  }
})

// 计算属性 - 统计值
const totalValue = computed(() => {
  return chartData.value.reduce((sum, item) => sum + (item.value || 0), 0)
})

const averageValue = computed(() => {
  if (!chartData.value.length) return 0
  return Math.round(totalValue.value / chartData.value.length)
})

const maxValue = computed(() => {
  if (!chartData.value.length) return 0
  return Math.max(...chartData.value.map(item => item.value || 0))
})

const minValue = computed(() => {
  if (!chartData.value.length) return 0
  return Math.min(...chartData.value.map(item => item.value || 0))
})

// 计算属性 - 饼图切片
const pieSlices = computed(() => {
  const total = totalValue.value
  if (!total) return []
  
  let currentAngle = 0
  return chartData.value.map((item, index) => {
    const percentage = (item.value || 0) / total
    const angle = percentage * 360
    const largeArcFlag = angle > 180 ? 1 : 0
    
    const startX = 100 + 80 * Math.cos((currentAngle * Math.PI) / 180)
    const startY = 100 + 80 * Math.sin((currentAngle * Math.PI) / 180)
    
    currentAngle += angle
    const endX = 100 + 80 * Math.cos((currentAngle * Math.PI) / 180)
    const endY = 100 + 80 * Math.sin((currentAngle * Math.PI) / 180)
    
    const path = `M 100 100 L ${startX} ${startY} A 80 80 0 ${largeArcFlag} 1 ${endX} ${endY} Z`
    
    return {
      path,
      color: getColor(index),
      percentage: (percentage * 100).toFixed(1)
    }
  })
})

// 生成仪表板数据
const generateDashboardData = () => {
  return [
    { label: '活跃用户', value: 1247 },
    { label: '今日扫描', value: 89 },
    { label: '异常检测', value: 23 },
    { label: '处理完成', value: 156 },
    { label: '系统告警', value: 3 }
  ]
}

// 生成情报数据
const generateIntelligenceData = () => {
  return [
    { label: '足球赛事', value: 45 },
    { label: '篮球赛事', value: 32 },
    { label: '网球赛事', value: 18 },
    { label: '其他赛事', value: 12 }
  ]
}

// 生成默认数据
const generateDefaultData = () => {
  return [
    { label: '类别A', value: 120 },
    { label: '类别B', value: 200 },
    { label: '类别C', value: 150 },
    { label: '类别D', value: 80 },
    { label: '类别E', value: 170 }
  ]
}

// 获取颜色
const getColor = (index) => {
  return props.colors[index % props.colors.length]
}

// 获取柱状图高度
const getBarHeight = (value) => {
  if (!chartData.value.length) return 0
  const maxVal = Math.max(...chartData.value.map(item => item.value || 0))
  return maxVal > 0 ? (value / maxVal) * 100 : 0
}

// 获取柱状图样式类
const getBarClass = (value) => {
  const avg = averageValue.value
  if (value > avg * 1.2) return 'high'
  if (value < avg * 0.8) return 'low'
  return 'normal'
}

// 获取折线图点
const getLinePoints = () => {
  const points = getLinePointsArray()
  return points.map(p => `${p.x},${p.y}`).join(' ')
}

const getLinePointsArray = () => {
  const width = 400
  const height = 200
  const maxVal = Math.max(...chartData.value.map(item => item.value || 0), 1)
  
  return chartData.value.map((item, index) => {
    const x = (index * width) / (chartData.value.length - 1 || 1)
    const y = height - (item.value / maxVal) * height
    return { x, y }
  })
}

// 处理周期变化
const handlePeriodChange = () => {
  emit('period-change', selectedPeriod.value)
  loadData()
}

// 刷新数据
const refreshData = () => {
  emit('refresh')
  loadData()
}

// 加载数据
const loadData = async () => {
  loading.value = true
  
  try {
    if (props.dataType === 'dashboard') {
      const response = await getDashboardStats()
      rawData.value = response.data || response
      // 这里可以根据实际API响应格式调整数据处理逻辑
    }
    
    // 模拟加载延迟
    setTimeout(() => {
      loading.value = false
    }, 500)
    
  } catch (error) {
    console.error('加载图表数据失败:', error)
    loading.value = false
  }
}

// 生命周期
onMounted(() => {
  loadData()
})

// 暴露方法给父组件
defineExpose({
  refreshData,
  chartData,
  totalValue,
  averageValue,
  maxValue,
  minValue
})
</script>

<style scoped>
.statistics-chart {
  width: 100%;
}

.chart-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.card-actions {
  display: flex;
  align-items: center;
}

.chart-container {
  min-height: 300px;
}

.loading-container,
.empty-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 250px;
}

.chart-content {
  space-y: 20px;
}

/* 柱状图样式 */
.bar-chart {
  padding: 20px 0;
}

.chart-bars {
  display: flex;
  align-items: end;
  justify-content: space-around;
  height: 200px;
  padding: 0 20px;
}

.chart-bar-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 80px;
}

.bar-label {
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  text-align: center;
}

.bar-wrapper {
  flex: 1;
  display: flex;
  align-items: end;
  width: 100%;
  justify-content: center;
}

.bar {
  width: 30px;
  min-height: 4px;
  border-radius: 4px 4px 0 0;
  position: relative;
  transition: all 0.3s ease;
  display: flex;
  align-items: end;
  justify-content: center;
}

.bar.high {
  background: linear-gradient(to top, var(--el-color-danger), var(--el-color-danger-light-3));
}

.bar.normal {
  background: linear-gradient(to top, var(--el-color-primary), var(--el-color-primary-light-3));
}

.bar.low {
  background: linear-gradient(to top, var(--el-color-success), var(--el-color-success-light-3));
}

.bar-value {
  position: absolute;
  top: -20px;
  font-size: 10px;
  color: var(--el-text-color-primary);
  font-weight: 600;
}

/* 折线图样式 */
.line-chart {
  position: relative;
  padding: 20px;
}

.line-svg {
  width: 100%;
  height: 200px;
}

.data-point:hover {
  r: 5;
  fill: var(--el-color-warning);
}

.axis-labels {
  position: relative;
  height: 20px;
  margin-top: 8px;
}

.axis-label {
  position: absolute;
  transform: translateX(-50%);
  font-size: 10px;
  color: var(--el-text-color-regular);
  text-align: center;
}

/* 饼图样式 */
.pie-chart {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px 0;
}

.pie-container {
  position: relative;
  flex-shrink: 0;
}

.pie-svg {
  width: 200px;
  height: 200px;
}

.pie-slice {
  transition: all 0.3s ease;
  cursor: pointer;
}

.pie-slice:hover {
  opacity: 0.8;
}

.pie-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.total-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-color-primary);
}

.total-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.pie-legend {
  flex: 1;
}

.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.legend-value {
  font-size: 12px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

/* 统计摘要样式 */
.chart-summary {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.summary-item {
  text-align: center;
}

.summary-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
  margin-bottom: 4px;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.summary-value.highlight {
  color: var(--el-color-primary);
}

.summary-value.success {
  color: var(--el-color-success);
}

.summary-value.warning {
  color: var(--el-color-warning);
}

@media (max-width: 768px) {
  .pie-chart {
    flex-direction: column;
  }
  
  .chart-bars {
    padding: 0 10px;
  }
  
  .bar {
    width: 20px;
  }
  
  .card-actions {
    flex-direction: column;
    gap: 8px;
  }
  
  .card-actions .el-select {
    width: 100% !important;
    margin-right: 0 !important;
  }
}</style>