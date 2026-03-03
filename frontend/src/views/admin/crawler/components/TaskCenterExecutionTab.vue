<template>
  <div class="task-center-execution-tab">
    <RealtimeDashboard :metrics="dashboardMetrics" />

    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务执行列表</span>
              <el-button @click="refreshList">刷新</el-button>
            </div>
          </template>

          <ExecutionList
            :executions="executions"
            :loading="loading"
            :total="total"
            :current-page="query.page"
            :page-size="query.pageSize"
            @view-details="handleViewDetails"
            @cancel-execution="handleCancelExecution"
            @page-change="handlePageChange"
            @size-change="handleSizeChange"
          />
        </el-card>
      </el-col>

      <el-col :span="8">
        <StatisticsPanel :stats="statistics" />

        <el-card style="margin-top: 20px;">
          <template #header>
            <div class="card-header">
              <span>状态分布</span>
            </div>
          </template>
          <el-table :data="statusDistribution" :show-header="false" style="width: 100%">
            <el-table-column prop="status" width="120" />
            <el-table-column prop="count" />
          </el-table>
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
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import taskMonitorApi from '@/api/taskMonitorApi'
import { useTaskMonitorStore } from '@/stores/taskMonitorStore'
import ExecutionList from './ExecutionList.vue'
import LogViewer from './LogViewer.vue'
import RealtimeDashboard from './RealtimeDashboard.vue'
import StatisticsPanel from './StatisticsPanel.vue'

const store = useTaskMonitorStore()

const loading = ref(false)
const executions = ref([])
const total = ref(0)
const logDrawerVisible = ref(false)
const selectedExecutionId = ref(null)
const websocketConnected = computed(() => store.connected)

const query = reactive({
  page: 1,
  pageSize: 20
})

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
    const status = exec.status || 'UNKNOWN'
    distribution[status] = (distribution[status] || 0) + 1
  })

  return Object.entries(distribution).map(([status, count]) => ({ status, count }))
})

const loadRealtimeOverview = async () => {
  try {
    const data = await taskMonitorApi.getRealtimeOverview()
    dashboardMetrics.value = {
      runningTasks: Number(data.running_tasks ?? 0),
      todayTotal: Number(data.today_total ?? 0),
      todaySuccess: Number(data.today_success ?? 0),
      successRate: Number(data.success_rate ?? 0),
      avgDuration: Number(data.avg_duration ?? 0),
      hourlyErrorRate: Number(data.hourly_error_rate ?? 0)
    }
  } catch (error) {
    console.error('loadRealtimeOverview failed:', error)
  }
}

const loadTopIssues = async () => {
  try {
    const issues = await taskMonitorApi.getTopIssues()
    const list = Array.isArray(issues) ? issues : []
    const totalCount = list.reduce((sum, item) => sum + Number(item.count || 0), 0)
    statistics.value.topIssues = list.map((item) => ({
      type: item.issue_type || '其他',
      count: Number(item.count || 0),
      percentage: totalCount > 0 ? Number((((item.count || 0) / totalCount) * 100).toFixed(2)) : 0
    }))
  } catch (error) {
    console.error('loadTopIssues failed:', error)
    statistics.value.topIssues = []
  }
}

const updateStatistics = () => {
  const totalCount = executions.value.length
  const successful = executions.value.filter((task) => task.status === 'SUCCESS').length
  const failed = executions.value.filter((task) => task.status === 'FAILED').length
  const running = executions.value.filter((task) => task.status === 'RUNNING').length
  const durations = executions.value.map((task) => Number(task.duration || 0)).filter((v) => v > 0)

  const avgExecutionTime = durations.length > 0
    ? Number((durations.reduce((a, b) => a + b, 0) / durations.length).toFixed(2))
    : 0

  statistics.value = {
    ...statistics.value,
    successRate: totalCount > 0 ? Number(((successful / totalCount) * 100).toFixed(2)) : 0,
    failureRate: totalCount > 0 ? Number(((failed / totalCount) * 100).toFixed(2)) : 0,
    runningTasks: running,
    todayExecutions: Number(dashboardMetrics.value.todayTotal || 0),
    avgExecutionTime,
    maxExecutionTime: durations.length > 0 ? Math.max(...durations) : 0
  }
}

const refreshList = async () => {
  loading.value = true
  try {
    const list = await store.fetchExecutions({
      page: query.page,
      page_size: query.pageSize
    })
    executions.value = list
    total.value = Number(store.totalCount || 0)

    await Promise.all([loadRealtimeOverview(), loadTopIssues()])
    updateStatistics()
  } catch (error) {
    console.error('refreshList failed:', error)
    ElMessage.error('获取任务执行列表失败')
  } finally {
    loading.value = false
  }
}

const handleViewDetails = (executionId) => {
  selectedExecutionId.value = executionId
  logDrawerVisible.value = true
}

const handleCancelExecution = async (executionId) => {
  try {
    await store.cancelExecution(executionId)
    ElMessage.success('任务已取消')
    await refreshList()
  } catch (error) {
    ElMessage.error('取消任务失败')
  }
}

const handlePageChange = async (page) => {
  query.page = Number(page) || 1
  await refreshList()
}

const handleSizeChange = async (size) => {
  query.pageSize = Number(size) || 20
  query.page = 1
  await refreshList()
}

onMounted(async () => {
  await refreshList()
})

onUnmounted(() => {
  store.disconnectWebSocket()
})
</script>

<style scoped>
.task-center-execution-tab {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
