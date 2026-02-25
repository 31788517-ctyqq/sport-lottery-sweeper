<template>
  <div class="system-monitor">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>爬虫系统监控</h2>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData">
          <el-icon><Refresh /></el-icon>
          刷新数据
        </el-button>
        <el-button @click="toggleAutoRefresh">
          <el-icon><VideoPlay /></el-icon>
          {{ autoRefresh ? '停止' : '开启' }}自动刷新
        </el-button>
      </div>
    </div>

    <!-- 全局健康状态 -->
    <div class="health-status">
      <el-row :gutter="20">
        <el-col :span="6" v-for="status in healthStatuses" :key="status.name">
          <el-card shadow="hover" class="status-card">
            <template #header>
              <div class="status-header">
                <span class="status-title">{{ status.name }}</span>
                <el-tag :type="status.type" size="small" effect="dark">
                  {{ status.value }}
                </el-tag>
              </div>
            </template>
            <div class="status-body">
              <el-progress 
                :percentage="status.percentage" 
                :status="status.progressStatus"
                :stroke-width="8"
                :show-text="false"
              />
              <div class="status-metrics">
                <span class="status-value">{{ status.currentValue }}{{ status.unit }}</span>
                <div class="status-trend">
                  <el-icon v-if="status.trend === 'up'" color="#67c23a">
                    <Top />
                  </el-icon>
                  <el-icon v-else-if="status.trend === 'down'" color="#f56c6c">
                    <Bottom />
                  </el-icon>
                  <span class="trend-text">{{ status.change }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 任务与监控关联 -->
    <div class="task-monitor-association">
      <el-card shadow="hover" class="association-card">
        <template #header>
          <div class="association-header">
            <span class="association-title">任务执行与监控关联</span>
          </div>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="association-item">
              <h4>任务状态统计</h4>
              <div class="task-stats">
                <div class="stat-item">
                  <span class="label">总任务数:</span>
                  <span class="value">{{ taskStats.totalTasks }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">运行中任务:</span>
                  <span class="value running">{{ taskStats.runningTasks }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">今日执行:</span>
                  <span class="value">{{ taskStats.todayExecutions }}</span>
                </div>
                <div class="stat-item">
                  <span class="label">成功率:</span>
                  <span class="value">{{ taskStats.successRate }}%</span>
                </div>
              </div>
            </div>
          </el-col>
          <el-col :span="12">
            <div class="association-item">
              <h4>实时任务监控</h4>
              <div class="task-list">
                <div 
                  v-for="task in recentTasks" 
                  :key="task.id" 
                  class="task-item"
                  :class="{'running': task.status === 'RUNNING'}"
                >
                  <div class="task-name">{{ task.name }}</div>
                  <div class="task-status">
                    <el-tag 
                      :type="getStatusType(task.status)" 
                      size="small"
                    >
                      {{ getStatusText(task.status) }}
                    </el-tag>
                  </div>
                  <div class="task-progress">
                    <el-progress 
                      :percentage="task.progress || 0" 
                      :status="getProgressStatus(task.status)"
                      :stroke-width="6"
                    />
                  </div>
                </div>
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>
    </div>

    <!-- 实时监控图表 -->
    <div class="monitor-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <div class="chart-header">
                <span class="chart-title">采集成功率趋势</span>
                <el-select 
                  v-model="successRateRange" 
                  size="small" 
                  style="width: 120px;"
                  @change="updateSuccessRateChart"
                >
                  <el-option label="24小时" value="24h" />
                  <el-option label="7天" value="7d" />
                  <el-option label="30天" value="30d" />
                </el-select>
              </div>
            </template>
            <div class="chart-container">
              <div ref="successRateChart" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card shadow="hover" class="chart-card">
            <template #header>
              <span class="chart-title">数据采集量分布</span>
            </template>
            <div class="chart-container">
              <div ref="dataDistributionChart" style="height: 300px;"></div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 实时告警 -->
    <div class="alerts-section">
      <el-card shadow="hover" class="alerts-card">
        <template #header>
          <div class="alert-header">
            <span class="alert-title">实时告警</span>
            <div class="alert-summary">
              <el-tag type="danger" size="small">紧急: {{ alertCounts.critical }}</el-tag>
              <el-tag type="warning" size="small">警告: {{ alertCounts.warning }}</el-tag>
              <el-tag type="info" size="small">信息: {{ alertCounts.info }}</el-tag>
            </div>
          </div>
        </template>
        
        <el-table 
          :data="activeAlerts" 
          v-loading="alertsLoading"
          class="alerts-table"
        >
          <el-table-column prop="severity" label="级别" width="80">
            <template #default="{row}">
              <el-tag :type="getSeverityType(row.severity)" size="small">
                {{ getSeverityLabel(row.severity) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="metric_name" label="指标" width="150" />
          
          <el-table-column prop="message" label="告警信息" min-width="300">
            <template #default="{row}">
              <div class="alert-message">
                <div class="alert-main-message">{{ row.message }}</div>
                <div class="alert-detail">
                  当前值: {{ row.current_value }} | 阈值: {{ row.threshold }}
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column prop="triggered_at" label="触发时间" width="180">
            <template #default="{row}">
              {{ formatTime(row.triggered_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150">
            <template #default="{row}">
              <el-button size="small" @click="handleAcknowledge(row)" v-if="row.status === 'active'">
                确认
              </el-button>
              <el-button size="small" @click="handleViewDetail(row)">
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>

    <!-- 系统资源监控 -->
    <div class="resource-monitor">
      <el-card shadow="hover" class="resource-card">
        <template #header>
          <span class="resource-title">系统资源监控</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="6">
            <ResourceGauge 
              title="CPU使用率" 
              :value="systemResources.cpu" 
              :thresholds="[70, 90]"
              unit="%"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="内存使用率" 
              :value="systemResources.memory" 
              :thresholds="[80, 95]"
              unit="%"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="磁盘使用率" 
              :value="systemResources.disk" 
              :thresholds="[85, 95]"
              unit="%"
            />
          </el-col>
          <el-col :span="6">
            <ResourceGauge 
              title="数据库连接" 
              :value="systemResources.dbConnections" 
              :max="systemResources.dbMaxConnections"
              unit="个"
            />
          </el-col>
        </el-row>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, VideoPlay, Top, Bottom } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
// AI_WORKING: coder1 @2026-02-04T18:38:22 - 修复导入错误：将getSystemHealth改为getHealthStatus，getSystemResources改为getResourcesUsage
import { 
  getHealthStatus, 
  getAlerts, 
  getResourcesUsage,
  acknowledgeAlert
} from '@/api/crawlerMonitor'
// 导入任务相关的API
import { getExecutions } from '@/api/taskMonitorApi'
// AI_DONE: coder1 @2026-02-04T18:38:22

// 响应式数据
const autoRefresh = ref(true)
const refreshTimer = ref(null)
const alertsLoading = ref(false)

// 图表引用
const successRateChart = ref(null)
const dataDistributionChart = ref(null)
let successRateChartInstance = null
let dataDistributionChartInstance = null

// 筛选条件
const successRateRange = ref('24h')

// 健康状态数据
const healthStatuses = ref([
  {
    name: '系统健康度',
    value: '健康',
    type: 'success',
    percentage: 98.5,
    progressStatus: 'success',
    currentValue: 98.5,
    unit: '%',
    trend: 'up',
    change: '+0.5%'
  },
  {
    name: '采集成功率',
    value: '正常',
    type: 'success',
    percentage: 96.2,
    progressStatus: 'success',
    currentValue: 96.2,
    unit: '%',
    trend: 'up',
    change: '+1.2%'
  },
  {
    name: '数据质量',
    value: '优秀',
    type: 'success',
    percentage: 94.8,
    progressStatus: 'success',
    currentValue: 94.8,
    unit: '%',
    trend: 'up',
    change: '+0.8%'
  },
  {
    name: '响应性能',
    value: '良好',
    type: 'warning',
    percentage: 87.3,
    progressStatus: 'warning',
    currentValue: 87.3,
    unit: '%',
    trend: 'down',
    change: '-2.1%'
  }
])

// 任务统计数据
const taskStats = reactive({
  totalTasks: 0,
  runningTasks: 0,
  todayExecutions: 0,
  successRate: 0
})

// 最近任务列表
const recentTasks = ref([])

// 告警数据
const activeAlerts = ref([])
const alertCounts = reactive({
  critical: 0,
  warning: 0,
  info: 0
})

// 系统资源数据
const systemResources = reactive({
  cpu: 45.2,
  memory: 67.8,
  disk: 32.1,
  dbConnections: 24,
  dbMaxConnections: 100
})

// 加载任务统计数据
const loadTaskStats = async () => {
  try {
    // 获取任务执行数据
    const res = await getExecutions({
      page: 1,
      page_size: 20,
      status: 'RUNNING'
    })

    const payload = res?.data ?? res
    const items = payload?.data?.items ?? payload?.items ?? payload?.data ?? []
    const list = Array.isArray(items) ? items : []

    recentTasks.value = list.slice(0, 5).map(item => ({
      id: item.id,
      name: item.task_name,
      status: item.status,
      progress: item.progress,
      records_processed: item.records_processed
    }))

    taskStats.totalTasks = Number(payload?.data?.total ?? payload?.total ?? list.length) || 0
    taskStats.runningTasks = list.filter(t => t.status === 'RUNNING').length
    taskStats.todayExecutions = list.length

    // 计算成功率
    if (list.length > 0) {
      const successful = list.filter(t => t.status === 'SUCCESS').length
      taskStats.successRate = Number(((successful / list.length) * 100).toFixed(2))
    } else {
      taskStats.successRate = 0
    }
  } catch (error) {
    console.error('Load task stats failed:', error)
  }
}

// 获取状态类型
const getStatusType = (status) => {
  const types = {
    'RUNNING': 'success',
    'SUCCESS': 'primary',
    'FAILED': 'danger',
    'PENDING': 'warning',
    'CANCELLED': 'info'
  }
  return types[status] || 'info'
}

// 获取状态文本
const getStatusText = (status) => {
  const texts = {
    'RUNNING': '运行中',
    'SUCCESS': '成功',
    'FAILED': '失败',
    'PENDING': '待执行',
    'CANCELLED': '已取消'
  }
  return texts[status] || status
}

// 获取进度状态
const getProgressStatus = (status) => {
  const statuses = {
    'RUNNING': 'success',
    'SUCCESS': 'success',
    'FAILED': 'exception',
    'PENDING': 'warning'
  }
  return statuses[status] || 'normal'
}

// 加载健康状态数据
const loadHealthStatus = async () => {
  try {
    const res = await getHealthStatus()  // AI_MODIFIED: coder1 @2026-02-04T18:38:22
    // TODO: 根据实际API返回格式处理数据
    console.log('Health status:', res.data)
  } catch (error) {
    console.error('Load health status failed:', error)
  }
}

// 加载告警数据
const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const res = await getAlerts({ status: 'active' })
    activeAlerts.value = res.data?.items || []
    
    // 统计告警数量
    alertCounts.critical = activeAlerts.value.filter(a => a.severity === 'critical').length
    alertCounts.warning = activeAlerts.value.filter(a => a.severity === 'warning').length
    alertCounts.info = activeAlerts.value.filter(a => a.severity === 'info').length
  } catch (error) {
    ElMessage.error('加载告警数据失败')
  } finally {
    alertsLoading.value = false
  }
}

// 加载系统资源数据
const loadSystemResources = async () => {
  try {
    const res = await getResourcesUsage()  // AI_MODIFIED: coder1 @2026-02-04T18:38:22
    Object.assign(systemResources, res.data)
  } catch (error) {
    console.error('Load system resources failed:', error)
  }
}

// 初始化图表
const initCharts = async () => {
  await nextTick()
  
  // 成功率趋势图
  if (successRateChart.value) {
    successRateChartInstance = echarts.init(successRateChart.value)
    updateSuccessRateChart()
  }
  
  // 数据分布饼图
  if (dataDistributionChart.value) {
    dataDistributionChartInstance = echarts.init(dataDistributionChart.value)
    updateDataDistributionChart()
  }
}

// 更新成功率图表
const updateSuccessRateChart = () => {
  if (!successRateChartInstance) return
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['成功率', '采集量']
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: generateTimeLabels()
    },
    yAxis: [
      {
        type: 'value',
        name: '成功率(%)',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      {
        type: 'value',
        name: '采集量',
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '成功率',
        type: 'line',
        data: generateSuccessRateData(),
        itemStyle: {
          color: '#67C23A'
        }
      },
      {
        name: '采集量',
        type: 'bar',
        yAxisIndex: 1,
        data: generateVolumeData(),
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }
  
  successRateChartInstance.setOption(option)
}

// 更新数据分布图表
const updateDataDistributionChart = () => {
  if (!dataDistributionChartInstance) return
  
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 10,
      data: ['比赛数据', '球员信息', '球队信息', '赔率数据', '新闻资讯']
    },
    series: [
      {
        name: '数据类型',
        type: 'pie',
        radius: ['50%', '70%'],
        avoidLabelOverlap: false,
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '18',
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: 335, name: '比赛数据' },
          { value: 310, name: '球员信息' },
          { value: 234, name: '球队信息' },
          { value: 135, name: '赔率数据' },
          { value: 154, name: '新闻资讯' }
        ],
        itemStyle: {
          color: function(params) {
            const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            return colors[params.dataIndex]
          }
        }
      }
    ]
  }
  
  dataDistributionChartInstance.setOption(option)
}

// 生成模拟数据
const generateTimeLabels = () => {
  const labels = []
  const now = new Date()
  for (let i = 23; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000)
    labels.push(time.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }))
  }
  return labels
}

const generateSuccessRateData = () => {
  return Array.from({ length: 24 }, () => Math.floor(Math.random() * 20) + 80)
}

const generateVolumeData = () => {
  return Array.from({ length: 24 }, () => Math.floor(Math.random() * 1000) + 500)
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([
    loadHealthStatus(),
    loadAlerts(),
    loadSystemResources(),
    loadTaskStats()
  ])
  updateSuccessRateChart()
  ElMessage.success('数据刷新完成')
}

// 切换自动刷新
const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
    ElMessage.success('已开启自动刷新')
  } else {
    stopAutoRefresh()
    ElMessage.info('已停止自动刷新')
  }
}

// 开始自动刷新
const startAutoRefresh = () => {
  refreshTimer.value = setInterval(() => {
    refreshData()
  }, 30000) // 30秒刷新一次
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

// 处理告警确认
const handleAcknowledge = async (alert) => {
  try {
    await acknowledgeAlert(alert.id)
    ElMessage.success('告警已确认')
    loadAlerts()
  } catch (error) {
    ElMessage.error('确认告警失败')
  }
}

// 查看告警详情
const handleViewDetail = (alert) => {
  // TODO: 打开告警详情弹窗
  console.log('View alert detail:', alert)
}

// 获取告警级别类型
const getSeverityType = (severity) => {
  const types = {
    critical: 'danger',
    warning: 'warning',
    info: 'info'
  }
  return types[severity] || 'info'
}

// 获取告警级别标签
const getSeverityLabel = (severity) => {
  const labels = {
    critical: '紧急',
    warning: '警告',
    info: '信息'
  }
  return labels[severity] || severity
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN')
}

// 添加防抖功能的handleResize函数
let resizeTimeout = null;
const handleResize = () => {
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  resizeTimeout = setTimeout(() => {
    successRateChartInstance?.resize()
    dataDistributionChartInstance?.resize()
  }, 100); // 100ms防抖延迟
}

// 生命周期
onMounted(async () => {
  await loadHealthStatus()
  await loadAlerts()
  await loadSystemResources()
  await loadTaskStats()  // 加载任务数据
  await initCharts()
  startAutoRefresh()
  
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  stopAutoRefresh()
  window.removeEventListener('resize', handleResize)
  
  // 清除可能存在的timeout
  if (resizeTimeout) {
    clearTimeout(resizeTimeout);
  }
  
  successRateChartInstance?.dispose()
  dataDistributionChartInstance?.dispose()
})
</script>

<style scoped>
.system-monitor {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.health-status {
  margin-bottom: 20px;
}

.status-card {
  border: none;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-title {
  font-weight: 600;
  color: #303133;
}

.status-body {
  padding: 10px 0;
}

.status-metrics {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.status-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.status-trend {
  display: flex;
  align-items: center;
  gap: 4px;
}

.trend-text {
  font-size: 12px;
  color: #909399;
}

.task-monitor-association {
  margin-bottom: 20px;
}

.association-card {
  border: none;
}

.association-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.association-title {
  font-weight: 600;
  color: #303133;
}

.association-item {
  padding: 15px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  background-color: #fafafa;
}

.association-item h4 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #303133;
  font-weight: 500;
}

.task-stats {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 5px 0;
  border-bottom: 1px dashed #e4e7ed;
}

.stat-item:last-child {
  border-bottom: none;
}

.stat-item .label {
  color: #606266;
}

.stat-item .value {
  font-weight: 500;
  color: #303133;
}

.stat-item .value.running {
  color: #67c23a;
}

.task-list {
  max-height: 200px;
  overflow-y: auto;
}

.task-item {
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
}

.task-item:last-child {
  border-bottom: none;
}

.task-item.running {
  background-color: rgba(103, 194, 58, 0.1);
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 5px;
}

.task-item .task-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.task-item .task-status {
  margin-bottom: 8px;
}

.task-item .task-progress {
  margin-top: 5px;
}

.monitor-charts {
  margin-bottom: 20px;
}

.chart-card {
  border: none;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-title {
  font-weight: 600;
  color: #303133;
}

.chart-container {
  position: relative;
}

.alerts-section {
  margin-bottom: 20px;
}

.alerts-card {
  border: none;
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alert-title {
  font-weight: 600;
  color: #303133;
}

.alert-summary {
  display: flex;
  gap: 8px;
}

.alerts-table {
  margin-top: 10px;
}

.alert-message {
  line-height: 1.4;
}

.alert-main-message {
  font-weight: 500;
  color: #303133;
}

.alert-detail {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.resource-monitor {
  margin-bottom: 20px;
}

.resource-card {
  border: none;
}

.resource-title {
  font-weight: 600;
  color: #303133;
}

:deep(.el-card__header) {
  background-color: #fafafa;
  border-bottom: 1px solid #ebeef5;
}

:deep(.el-progress-bar__outer) {
  background-color: #f0f0f0;
}

:deep(.el-table) {
  --el-table-border-color: #ebeef5;
  --el-table-header-bg-color: #fafafa;
}
</style>