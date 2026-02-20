<template>
  <div class="page-container">
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>预测监控</span>
          <el-button type="primary" @click="fetchPredictions" :loading="loading">刷新</el-button>
        </div>
      </template>

      <div class="card-content">
        <!-- 统计卡片 -->
        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-value">{{ summaryStats.total }}</div>
            <div class="stat-label">总预测数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ summaryStats.hits }}</div>
            <div class="stat-label">命中数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ summaryStats.accuracy }}%</div>
            <div class="stat-label">命中率</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ summaryStats.pending }}</div>
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
            style="width: 320px;"
          />
          <el-button type="primary" @click="handleSearch" :loading="loading">查询</el-button>
          <el-button @click="resetFilter" :disabled="loading">重置</el-button>
        </div>

        <!-- 命中率趋势图（当前页） -->
        <div ref="chartRef" class="chart-container"></div>

        <!-- 预测结果列表 -->
        <el-table :data="predictionList" border style="width: 100%; margin-top: 20px;" v-loading="loading">
          <el-table-column prop="id" label="ID" width="80" />
          <el-table-column prop="match_id" label="比赛ID" min-width="220" />
          <el-table-column label="平局概率" width="120">
            <template #default="scope">
              <span v-if="typeof scope.row.predicted_draw_prob === 'number'">
                {{ (scope.row.predicted_draw_prob * 100).toFixed(1) }}%
              </span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="实际结果" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.actual_result === 'draw'" type="success">平局</el-tag>
              <el-tag v-else-if="scope.row.actual_result === 'home'" type="primary">主胜</el-tag>
              <el-tag v-else-if="scope.row.actual_result === 'away'" type="warning">客胜</el-tag>
              <el-tag v-else type="info">未开奖</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="是否命中" width="120">
            <template #default="scope">
              <el-tag v-if="scope.row.actual_result === 'draw'" type="success">命中</el-tag>
              <el-tag v-else-if="scope.row.actual_result" type="danger">未中</el-tag>
              <el-tag v-else type="info">等待</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="match_time" label="比赛时间" width="180" :formatter="formatDate" />
          <el-table-column prop="predicted_at" label="预测时间" width="180" :formatter="formatDate" />
        </el-table>

        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100, 200]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          style="margin-top: 16px; text-align: right;"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import { getPredictions } from '@/api/drawPrediction'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'

const dateRange = ref([])
const predictionList = ref([])
const loading = ref(false)

const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)

const summaryStats = ref({
  total: 0,
  hits: 0,
  accuracy: 0.0,
  pending: 0
})

const chartRef = ref(null)
let chartInstance = null

const toIsoStartEnd = (range) => {
  if (!Array.isArray(range) || range.length !== 2) return {}
  const start = new Date(range[0])
  const end = new Date(range[1])
  if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return {}
  start.setHours(0, 0, 0, 0)
  end.setHours(23, 59, 59, 999)
  return { start_date: start.toISOString(), end_date: end.toISOString() }
}

const fetchPredictions = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      ...toIsoStartEnd(dateRange.value)
    }

    // `request` 拦截器会返回后端的 `data` 字段（内层对象）
    // 期望结构：{ data: [], total, page, size, stats }
    const res = await getPredictions(params)

    const list = Array.isArray(res?.data) ? res.data : []
    predictionList.value = list
    total.value = typeof res?.total === 'number' ? res.total : list.length

    const s = res?.stats || {}
    summaryStats.value = {
      total: typeof s.total === 'number' ? s.total : total.value,
      hits: typeof s.hits === 'number' ? s.hits : 0,
      accuracy: typeof s.accuracy === 'number' ? s.accuracy : 0.0,
      pending: typeof s.pending === 'number' ? s.pending : 0
    }

    await nextTick()
    initChart()
  } catch (err) {
    console.error('获取预测数据失败:', err)
    ElMessage.error('获取预测数据失败')
    predictionList.value = []
    total.value = 0
    summaryStats.value = { total: 0, hits: 0, accuracy: 0.0, pending: 0 }
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchPredictions()
}

const resetFilter = () => {
  dateRange.value = []
  currentPage.value = 1
  fetchPredictions()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchPredictions()
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchPredictions()
}

const formatDate = (_row, _column, cellValue) => {
  if (!cellValue) return ''
  const d = new Date(cellValue)
  if (Number.isNaN(d.getTime())) return String(cellValue)
  return d.toLocaleString()
}

const calculateAccuracyTrend = () => {
  const dateMap = {}
  const sorted = [...predictionList.value]
    .filter((p) => p && p.actual_result && p.predicted_at)
    .sort((a, b) => new Date(a.predicted_at) - new Date(b.predicted_at))

  for (const p of sorted) {
    const d = new Date(p.predicted_at)
    if (Number.isNaN(d.getTime())) continue
    const key = d.toLocaleDateString()
    if (!dateMap[key]) dateMap[key] = { total: 0, hits: 0 }
    dateMap[key].total += 1
    if (p.actual_result === 'draw') dateMap[key].hits += 1
  }

  const dates = Object.keys(dateMap)
  const accuracy = dates.map((k) => {
    const v = dateMap[k]
    return v.total > 0 ? Number(((v.hits / v.total) * 100).toFixed(1)) : 0
  })
  return { dates, accuracy }
}

const initChart = () => {
  if (!chartRef.value) return

  const trend = calculateAccuracyTrend()

  if (chartInstance) chartInstance.dispose()
  chartInstance = echarts.init(chartRef.value)

  chartInstance.setOption({
    title: { text: '命中率趋势（当前页）', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: trend.dates },
    yAxis: { type: 'value', min: 0, max: 100, name: '命中率(%)' },
    series: [
      {
        name: '命中率',
        type: 'line',
        data: trend.accuracy,
        smooth: true,
        areaStyle: { color: 'rgba(64, 158, 255, 0.2)' },
        lineStyle: { color: '#409EFF', width: 3 },
        itemStyle: { color: '#409EFF' }
      }
    ]
  })
}

const handleResize = () => {
  if (chartInstance) chartInstance.resize()
}

onMounted(async () => {
  await fetchPredictions()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  if (chartInstance) chartInstance.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

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
  font-weight: 700;
  color: #409eff;
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

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}
</style>

