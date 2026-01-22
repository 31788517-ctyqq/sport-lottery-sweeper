<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <span class="card-header">预测监控</span>
      </template>
      <div class="card-content">
        <!-- 统计卡片 -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ stats.total }}</div>
            <div class="stat-label">总预测数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.hits }}</div>
            <div class="stat-label">命中数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.accuracy }}%</div>
            <div class="stat-label">命中率</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ stats.pending }}</div>
            <div class="stat-label">待确认</div>
          </div>
        </div>

        <!-- 筛选工具栏 -->
        <div class="toolbar">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            value-format="YYYY-MM-DD"
            style="width: 300px; margin-right: 10px;"
          />
          <el-button type="primary" @click="fetchPredictions">查询</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </div>

        <!-- 命中率趋势图 -->
        <div ref="chartRef" class="chart-container" style="width: 100%; height: 400px; margin-top: 20px;"></div>

        <!-- 预测结果列表 -->
        <el-table :data="predictionList" border style="width: 100%; margin-top: 20px;">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="match_id" label="比赛ID" />
          <el-table-column label="平局概率" width="120">
            <template #default="scope">
              <span>{{ (scope.row.predicted_draw_prob * 100).toFixed(1) }}%</span>
            </template>
          </el-table-column>
          <el-table-column label="实际结果" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.actual_result === 'draw'" type="success">平局</el-tag>
              <el-tag v-else-if="scope.row.actual_result === 'home'" type="primary">主胜</el-tag>
              <el-tag v-else-if="scope.row.actual_result === 'away'" type="warning">客胜</el-tag>
              <el-tag v-else type="info">未开赛</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="是否命中" width="100">
            <template #default="scope">
              <el-tag v-if="scope.row.actual_result === 'draw'" type="success">命中</el-tag>
              <el-tag v-else-if="scope.row.actual_result" type="danger">未中</el-tag>
              <el-tag v-else type="info">等待</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="match_time" label="比赛时间" :formatter="formatDate" width="180" />
          <el-table-column prop="predicted_at" label="预测时间" :formatter="formatDate" width="180" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const dateRange = ref([])
const predictionList = ref([])
const chartRef = ref(null)
let chartInstance = null

const stats = computed(() => {
  const total = predictionList.value.length
  const finished = predictionList.value.filter(p => p.actual_result)
  const hits = finished.filter(p => p.actual_result === 'draw')
  const accuracy = finished.length > 0 ? ((hits.length / finished.length) * 100).toFixed(1) : '0.0'
  const pending = total - finished.length
  return { total, hits: hits.length, accuracy, pending }
})

const fetchPredictions = async () => {
  try {
    const params = {}
    if (dateRange.value && dateRange.value.length === 2) {
      params.start_date = dateRange.value[0]
      params.end_date = dateRange.value[1]
    }
    const res = await axios.get('/api/v1/admin/draw-prediction/predictions', { params })
    predictionList.value = res.data
    await nextTick()
    initChart()
  } catch (err) {
    ElMessage.error('获取预测数据失败')
  }
}

const resetFilter = () => {
  dateRange.value = []
  fetchPredictions()
}

const formatDate = (row, column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  return d.toLocaleString()
}

const initChart = () => {
  if (!chartRef.value) return

  // 计算命中率趋势数据（按日期分组）
  const trendData = calculateAccuracyTrend()

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)
  const option = {
    title: {
      text: '命中率趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: trendData.dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
      name: '命中率 (%)'
    },
    series: [{
      name: '命中率',
      type: 'line',
      data: trendData.accuracy,
      smooth: true,
      areaStyle: {
        color: 'rgba(64, 158, 255, 0.2)'
      },
      lineStyle: {
        color: '#409EFF',
        width: 3
      },
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }

  chartInstance.setOption(option)
}

const calculateAccuracyTrend = () => {
  // 按日期分组计算每日命中率
  const dateMap = {}
  const sortedData = [...predictionList.value]
    .filter(p => p.actual_result) // 只计算已结束的比赛
    .sort((a, b) => new Date(a.predicted_at) - new Date(b.predicted_at))

  sortedData.forEach(p => {
    const date = new Date(p.predicted_at).toLocaleDateString()
    if (!dateMap[date]) {
      dateMap[date] = { total: 0, hits: 0 }
    }
    dateMap[date].total++
    if (p.actual_result === 'draw') {
      dateMap[date].hits++
    }
  })

  const dates = Object.keys(dateMap)
  const accuracy = dates.map(date => {
    const data = dateMap[date]
    return ((data.hits / data.total) * 100).toFixed(1)
  })

  return { dates, accuracy }
}

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

onMounted(async () => {
  await fetchPredictions()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  window.removeEventListener('resize', handleResize)
})

</script>

<style scoped>
.stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.stat-card {
  flex: 1;
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
