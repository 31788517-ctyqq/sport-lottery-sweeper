<template>
  <div class="intelligence-management-container">
    <div class="page-header">
      <h2>情感分析</h2>
      <p class="page-description">对情报数据进行情感分析和情绪倾向判断</p>
    </div>

    <div class="quick-actions">
      <el-button type="primary" :icon="Plus" @click="analyzeSentiment">开始分析</el-button>
      <el-button type="success" :icon="VideoPlay" @click="startRealTimeMonitoring">实时监控</el-button>
      <el-button type="warning" :icon="RefreshLeft" @click="refreshData">刷新数据</el-button>
      <el-button type="info" :icon="Download" @click="exportReport">导出报告</el-button>
    </div>

    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.positiveCount }}</div>
              <div class="stats-label">正面情感</div>
            </div>
            <el-icon class="stats-icon"><CaretTop /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.negativeCount }}</div>
              <div class="stats-label">负面情感</div>
            </div>
            <el-icon class="stats-icon"><CaretBottom /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.neutralCount }}</div>
              <div class="stats-label">中性情感</div>
            </div>
            <el-icon class="stats-icon"><Minus /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.accuracy }}%</div>
              <div class="stats-label">准确率</div>
            </div>
            <el-icon class="stats-icon"><Aim /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-tabs v-model="activeTab" class="management-tabs">
      <el-tab-pane label="情感分布" name="distribution">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>情感极性分布</span>
              </div>
            </template>
            <div class="chart-container">
              <div ref="distributionChartRef" class="chart-canvas" />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="情感趋势" name="timeline">
        <div class="tab-content">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>情感趋势分析</span>
              </div>
            </template>
            <div class="chart-container">
              <div ref="timelineChartRef" class="chart-canvas" />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="详细分析" name="detailed">
        <div class="tab-content">
          <el-table :data="sentimentList" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="source" label="来源" width="150" />
            <el-table-column prop="content" label="内容摘要" show-overflow-tooltip />
            <el-table-column prop="sentiment" label="情感倾向" width="120">
              <template #default="scope">
                <el-tag :type="getSentimentTagType(scope.row.sentiment)">
                  {{ scope.row.sentiment }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="confidence" label="置信度" width="100">
              <template #default="scope">
                {{ Math.round(scope.row.confidence * 100) }}%
              </template>
            </el-table-column>
            <el-table-column prop="date" label="日期" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewDetails(scope.row)">查看</el-button>
                <el-button size="small" type="danger" @click="deleteItem(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
          <el-pagination
            class="pagination"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="pagination.currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pagination.pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="pagination.total"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="showViewDialog" title="情感分析详情" width="60%">
      <div v-if="selectedItem">
        <h3>{{ selectedItem.source }}</h3>
        <p><strong>原文内容：</strong>{{ selectedItem.content }}</p>
        <p>
          <strong>情感倾向：</strong>
          <el-tag :type="getSentimentTagType(selectedItem.sentiment)">
            {{ selectedItem.sentiment }}
          </el-tag>
        </p>
        <p><strong>置信度：</strong>{{ Math.round(selectedItem.confidence * 100) }}%</p>
        <p><strong>分析时间：</strong>{{ selectedItem.date }}</p>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showViewDialog = false">关闭</el-button>
          <el-button type="primary" @click="showViewDialog = false">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  VideoPlay,
  RefreshLeft,
  Download,
  CaretTop,
  CaretBottom,
  Minus,
  Aim
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'

const activeTab = ref('distribution')

const stats = reactive({
  positiveCount: 1240,
  negativeCount: 562,
  neutralCount: 890,
  accuracy: 92.4
})

const loading = ref(false)

const pagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 100
})

const sentimentDistributionData = {
  columns: ['情感类型', '数量'],
  rows: [
    { 情感类型: '正面', 数量: 1240 },
    { 情感类型: '负面', 数量: 562 },
    { 情感类型: '中性', 数量: 890 }
  ]
}

const sentimentTimelineData = {
  columns: ['时间', '正面', '负面', '中性'],
  rows: [
    { 时间: '2024-01-01', 正面: 320, 负面: 120, 中性: 200 },
    { 时间: '2024-01-02', 正面: 280, 负面: 180, 中性: 180 },
    { 时间: '2024-01-03', 正面: 350, 负面: 100, 中性: 220 },
    { 时间: '2024-01-04', 正面: 400, 负面: 90, 中性: 250 },
    { 时间: '2024-01-05', 正面: 380, 负面: 110, 中性: 240 },
    { 时间: '2024-01-06', 正面: 420, 负面: 80, 中性: 260 },
    { 时间: '2024-01-07', 正面: 450, 负面: 70, 中性: 280 }
  ]
}

const sentimentList = ref([
  { id: 1, source: '社交媒体', content: '这支队伍最近表现令人振奋，球员状态很好。', sentiment: '正面', confidence: 0.92, date: '2024-01-15 10:30' },
  { id: 2, source: '新闻报道', content: '由于伤病困扰，球队主力无法出场，前景堪忧。', sentiment: '负面', confidence: 0.87, date: '2024-01-15 09:45' },
  { id: 3, source: '专家评论', content: '从数据来看，两队实力相当，胜负难料。', sentiment: '中性', confidence: 0.78, date: '2024-01-15 08:20' },
  { id: 4, source: '球迷论坛', content: '虽然输了比赛，但球员拼搏精神值得称赞。', sentiment: '正面', confidence: 0.85, date: '2024-01-14 22:10' },
  { id: 5, source: '技术分析', content: '从赔率变化看，市场对本场比赛态度谨慎。', sentiment: '中性', confidence: 0.72, date: '2024-01-14 18:30' }
])

const selectedItem = ref(null)
const showViewDialog = ref(false)

const distributionChartRef = ref(null)
const timelineChartRef = ref(null)
let distributionChart = null
let timelineChart = null

const buildDistributionOption = () => {
  const [nameKey, valueKey] = sentimentDistributionData.columns || []
  const rows = sentimentDistributionData.rows || []

  return {
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        label: { show: true, formatter: '{b}: {d}%' },
        data: rows.map((row) => ({
          name: row?.[nameKey] ?? '-',
          value: Number(row?.[valueKey] ?? 0)
        }))
      }
    ]
  }
}

const buildTimelineOption = () => {
  const [xKey, ...metricKeys] = sentimentTimelineData.columns || []
  const rows = sentimentTimelineData.rows || []

  return {
    tooltip: { trigger: 'axis' },
    legend: { top: 8 },
    grid: { left: 40, right: 20, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: rows.map((row) => row?.[xKey] ?? '-')
    },
    yAxis: { type: 'value' },
    series: metricKeys.map((key) => ({
      name: key,
      type: 'line',
      smooth: true,
      data: rows.map((row) => Number(row?.[key] ?? 0))
    }))
  }
}

const renderDistributionChart = () => {
  if (!distributionChartRef.value) return
  if (!distributionChart) distributionChart = echarts.init(distributionChartRef.value)
  distributionChart.setOption(buildDistributionOption())
}

const renderTimelineChart = () => {
  if (!timelineChartRef.value) return
  if (!timelineChart) timelineChart = echarts.init(timelineChartRef.value)
  timelineChart.setOption(buildTimelineOption())
}

const renderActiveChart = () => {
  if (activeTab.value === 'distribution') {
    renderDistributionChart()
    return
  }
  if (activeTab.value === 'timeline') {
    renderTimelineChart()
  }
}

const handleChartResize = () => {
  if (distributionChart) distributionChart.resize()
  if (timelineChart) timelineChart.resize()
}

const analyzeSentiment = () => {
  ElMessage.success('开始情感分析...')
  loading.value = true
  setTimeout(() => {
    loading.value = false
    ElMessage.success('情感分析完成')
  }, 1500)
}

const startRealTimeMonitoring = () => {
  ElMessage.info('启动实时情感监控...')
}

const refreshData = () => {
  ElMessage.info('刷新数据中...')
  nextTick(() => {
    renderActiveChart()
  })
}

const exportReport = () => {
  ElMessage.info('导出报告中...')
}

const getSentimentTagType = (sentiment) => {
  if (sentiment === '正面') return 'success'
  if (sentiment === '负面') return 'danger'
  return 'info'
}

const viewDetails = (item) => {
  selectedItem.value = item
  showViewDialog.value = true
}

const deleteItem = (item) => {
  ElMessageBox.confirm(
    `确定要删除来自“${item.source}”的情感分析数据吗？`,
    '删除确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  )
    .then(() => {
      sentimentList.value = sentimentList.value.filter((i) => i.id !== item.id)
      ElMessage.success('删除成功')
    })
    .catch(() => {
      ElMessage.info('已取消删除')
    })
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
}

watch(activeTab, () => {
  nextTick(() => {
    renderActiveChart()
  })
})

onMounted(() => {
  nextTick(() => {
    renderDistributionChart()
    renderTimelineChart()
  })
  window.addEventListener('resize', handleChartResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleChartResize)
  if (distributionChart) {
    distributionChart.dispose()
    distributionChart = null
  }
  if (timelineChart) {
    timelineChart.dispose()
    timelineChart = null
  }
})
</script>

<style scoped>
.intelligence-management-container {
  padding: 20px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 24px;
  font-weight: 600;
}

.page-description {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.quick-actions {
  margin-bottom: 24px;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-card {
  position: relative;
  overflow: hidden;
}

.stats-content {
  position: relative;
  z-index: 2;
}

.stats-number {
  font-size: 28px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 48px;
  color: #409eff;
  opacity: 0.1;
  z-index: 1;
}

.management-tabs {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px;
}

.chart-container {
  height: 400px;
}

.chart-canvas {
  width: 100%;
  height: 100%;
}

.pagination {
  margin-top: 20px;
  text-align: right;
}
</style>
