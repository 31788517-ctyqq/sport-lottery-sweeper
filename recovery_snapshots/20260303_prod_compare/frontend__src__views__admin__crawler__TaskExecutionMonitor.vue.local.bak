<template>
  <div class="task-execution-monitor">
    <el-container>
      <el-header height="auto">
        <RealtimeDashboard :metrics="dashboardMetrics" />
      </el-header>

      <el-main>
        <el-row :gutter="20">
          <el-col :span="16">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>任务执行列表</span>
                  <div>
                    <el-button @click="refreshList">刷新</el-button>
                    <el-button type="primary" @click="$router.push('/admin/data-source/task-console')">任务控制台</el-button>
                  </div>
                </div>
              </template>
              <ExecutionList
                :executions="executions"
                :loading="loading"
                @view-details="handleViewDetails"
                @cancel-execution="handleCancelExecution"
              />
            </el-card>
          </el-col>

          <el-col :span="8">
            <el-card>
              <template #header>
                <div class="card-header">
                  <span>执行统计</span>
                </div>
              </template>
              <StatisticsPanel :stats="statistics" />

              <el-card style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>任务状态分布</span>
                  </div>
                </template>
                <el-table :data="statusDistribution" style="width: 100%" :show-header="false">
                  <el-table-column prop="status" width="100" />
                  <el-table-column prop="count" />
                </el-table>
              </el-card>
            </el-card>
          </el-col>
        </el-row>

        <el-drawer
          v-model="logDrawerVisible"
          title="任务执行日志"
          size="60%"
          :destroy-on-close="true"
        >
          <LogViewer
            v-if="logDrawerVisible"
            :execution-id="selectedExecutionId"
            :websocket-connected="websocketConnected"
          />
        </el-drawer>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import taskMonitorApi from '@/api/taskMonitorApi'
import { useTaskMonitorStore } from '@/stores/taskMonitorStore'
import ExecutionList from './components/ExecutionList.vue'
import LogViewer from './components/LogViewer.vue'
import RealtimeDashboard from './components/RealtimeDashboard.vue'
import StatisticsPanel from './components/StatisticsPanel.vue'

const store = useTaskMonitorStore()
const executions = ref([])
const loading = ref(false)
const logDrawerVisible = ref(false)
const selectedExecutionId = ref(null)
const websocketConnected = computed(() => store.connected)

const dashboardMetrics = ref({
  runningTasks: 0,
  todayTotal: 0,
  todaySuccess: 0,
  successRate: 0,
  avgDuration: 0,
  hourlyErrorRate: 0
})

const statistics = ref({
  successRate: 0,
  avgExecutionTime: 0,
  failureRate: 0,
  runningTasks: 0,
  todayExecutions: 0,
  maxExecutionTime: 0,
  topIssues: []
})

const statusDistribution = computed(() => {
  const distribution = {}
  executions.value.forEach((exec) => {
    distribution[exec.status] = (distribution[exec.status] || 0) + 1
  })

  return Object.entries(distribution).map(([status, count]) => ({ status, count }))
})

onMounted(async () => {
  await refreshList()
  // 当前后端未提供 task-monitor 专用 realtime websocket，避免无效重连噪音
})

onUnmounted(() => {
  store.disconnectWebSocket()
})

const refreshList = async () => {
  loading.value = true
  try {
    executions.value = await store.fetchExecutions({
      page: 1,
      page_size: 20
    })
    await Promise.all([loadRealtimeOverview(), loadTopIssues()])
    updateStatistics()
  } catch (error) {
    console.error('获取任务执行列表失败:', error)
  } finally {
    loading.value = false
  }
}

const loadRealtimeOverview = async () => {
  try {
    const res = await taskMonitorApi.getRealtimeOverview()
    const data = res.data || {}
    dashboardMetrics.value = {
      runningTasks: Number(data.running_tasks || data.runningTasks || 0),
      todayTotal: Number(data.today_total || data.todayTotal || 0),
      todaySuccess: Number(data.today_success || data.todaySuccess || 0),
      successRate: Number(data.success_rate || data.successRate || 0),
      avgDuration: Number(data.avg_duration || data.avgDuration || 0),
      hourlyErrorRate: Number(data.hourly_error_rate || data.hourlyErrorRate || 0)
    }
  } catch (error) {
    console.error('获取实时概览失败:', error)
  }
}

const loadTopIssues = async () => {
  try {
    const res = await taskMonitorApi.getTopIssues()
    const issues = res.data || []
    const total = issues.reduce((sum, item) => sum + Number(item.count || 0), 0)
    statistics.value.topIssues = issues.map((item) => ({
      type: item.issue_type || item.type || '其他',
      count: Number(item.count || 0),
      percentage: total > 0 ? Number((((item.count || 0) / total) * 100).toFixed(2)) : 0
    }))
  } catch (error) {
    console.error('获取问题排行失败:', error)
    statistics.value.topIssues = []
  }
}

const updateStatistics = () => {
  const total = executions.value.length
  const successful = executions.value.filter((task) => task.status === 'SUCCESS').length
  const failed = executions.value.filter((task) => task.status === 'FAILED').length
  const running = executions.value.filter((task) => task.status === 'RUNNING').length
  const durations = executions.value.map((task) => Number(task.duration || 0)).filter((v) => v > 0)
  const avgExecutionTime = durations.length > 0
    ? Number((durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2))
    : 0
  const maxExecutionTime = durations.length > 0 ? Math.max(...durations) : 0

  statistics.value = {
    ...statistics.value,
    successRate: total > 0 ? Number(((successful / total) * 100).toFixed(2)) : 0,
    failureRate: total > 0 ? Number(((failed / total) * 100).toFixed(2)) : 0,
    runningTasks: running,
    todayExecutions: Number(dashboardMetrics.value.todayTotal || total),
    avgExecutionTime,
    maxExecutionTime
  }
}

const handleViewDetails = (executionId) => {
  selectedExecutionId.value = executionId
  logDrawerVisible.value = true
}

const handleCancelExecution = async (executionId) => {
  await store.cancelExecution(executionId)
  await refreshList()
}
</script>

<style scoped>
.task-execution-monitor {
  padding: 20px;
  height: calc(100vh - 84px);
  overflow: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.el-header {
  padding: 0;
  margin-bottom: 20px;
}

.el-main {
  padding: 0;
}
</style>
