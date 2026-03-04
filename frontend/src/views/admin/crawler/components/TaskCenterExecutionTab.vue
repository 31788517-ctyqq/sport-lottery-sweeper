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
            @view-details="handleViewDetails"
            @cancel-execution="handleCancelExecution"
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
      v-model="detailDrawerVisible"
      title="任务执行详情"
      size="56%"
      :destroy-on-close="true"
    >
      <div v-if="detailLoading" class="detail-loading">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="selectedRunDetail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="run_id">{{ selectedRunDetail.run_id || '-' }}</el-descriptions-item>
          <el-descriptions-item label="dataset">{{ selectedRunDetail.dataset_slug || '-' }}</el-descriptions-item>
          <el-descriptions-item label="status">{{ selectedRunDetail.status || '-' }}</el-descriptions-item>
          <el-descriptions-item label="version">{{ selectedRunDetail.version || '-' }}</el-descriptions-item>
          <el-descriptions-item label="rows_raw">{{ selectedRunDetail.rows_raw ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="rows_upserted">{{ selectedRunDetail.rows_upserted ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="duration_ms">{{ selectedRunDetail.duration_ms ?? 0 }}</el-descriptions-item>
          <el-descriptions-item label="trigger_type">{{ selectedRunDetail.trigger_type || '-' }}</el-descriptions-item>
          <el-descriptions-item label="started_at">{{ selectedRunDetail.started_at || '-' }}</el-descriptions-item>
          <el-descriptions-item label="finished_at">{{ selectedRunDetail.finished_at || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-card style="margin-top: 12px;">
          <template #header>质量评分</template>
          <el-row :gutter="12">
            <el-col :span="8">
              <div class="quality-kv">
                <span>quality_score</span>
                <strong>{{ selectedRunQuality?.quality_score ?? 0 }}</strong>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="quality-kv">
                <span>rows_total</span>
                <strong>{{ selectedRunQuality?.rows_total ?? 0 }}</strong>
              </div>
            </el-col>
            <el-col :span="8">
              <div class="quality-kv">
                <span>rows_invalid</span>
                <strong>{{ selectedRunQuality?.rows_invalid ?? 0 }}</strong>
              </div>
            </el-col>
          </el-row>
        </el-card>

        <el-card style="margin-top: 12px;">
          <template #header>运行元数据</template>
          <pre class="meta-block">{{ JSON.stringify(selectedRunDetail.run_meta || {}, null, 2) }}</pre>
        </el-card>
      </div>

      <el-empty v-else description="暂无详情" />
    </el-drawer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getKaggleRunDetail,
  getKaggleRunQuality,
  getKaggleRuns,
  getKaggleSyncStatus
} from '@/api/modules/kaggle-sync'
import ExecutionList from './ExecutionList.vue'
import RealtimeDashboard from './RealtimeDashboard.vue'
import StatisticsPanel from './StatisticsPanel.vue'

const loading = ref(false)
const executions = ref([])
const rawRuns = ref([])

const detailDrawerVisible = ref(false)
const detailLoading = ref(false)
const selectedRunDetail = ref(null)
const selectedRunQuality = ref(null)

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

const toUpperStatus = (status) => {
  const text = String(status || '').toLowerCase()
  if (['queued', 'pending'].includes(text)) return 'PENDING'
  if (text === 'running') return 'RUNNING'
  if (['success', 'succeeded', 'completed'].includes(text)) return 'SUCCESS'
  if (text === 'failed' || text === 'error') return 'FAILED'
  if (text === 'cancelled') return 'CANCELLED'
  return 'PENDING'
}

const toExecution = (run) => {
  const status = toUpperStatus(run.status)
  const durationMs = Number(run.duration_ms || 0)
  const durationSeconds = durationMs > 0 ? Number((durationMs / 1000).toFixed(2)) : 0
  const rowsRaw = Number(run.rows_raw || 0)
  const rowsUpserted = Number(run.rows_upserted || 0)
  const recordsFailed = Math.max(0, rowsRaw - rowsUpserted)

  return {
    id: run.id,
    runId: run.run_id,
    taskName: run.dataset_slug || '-',
    type: run.trigger_type || 'manual',
    status,
    progress: status === 'RUNNING' ? 50 : status === 'SUCCESS' ? 100 : 0,
    startedAt: run.started_at || run.created_at || null,
    endedAt: run.finished_at || run.updated_at || null,
    duration: durationSeconds,
    recordsProcessed: rowsUpserted,
    recordsFailed,
    raw: run
  }
}

const loadTopIssues = (runs) => {
  const issueMap = {}
  runs.forEach((run) => {
    if (!run.error_code && !run.error_message) return
    const key = run.error_code || 'unknown_error'
    issueMap[key] = (issueMap[key] || 0) + 1
  })
  const total = Object.values(issueMap).reduce((sum, count) => sum + Number(count || 0), 0)
  statistics.value.topIssues = Object.entries(issueMap).map(([type, count]) => ({
    type,
    count,
    percentage: total > 0 ? Number(((count / total) * 100).toFixed(2)) : 0
  }))
}

const loadMetrics = async (runs) => {
  const status = await getKaggleSyncStatus()
  const runList = Array.isArray(runs) ? runs : []
  const successRuns = runList.filter((run) => toUpperStatus(run.status) === 'SUCCESS')
  const failedRuns = runList.filter((run) => toUpperStatus(run.status) === 'FAILED')

  const now = new Date()
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime()
  const oneHourAgo = Date.now() - 60 * 60 * 1000

  const todayRuns = runList.filter((run) => {
    const ts = new Date(run.started_at || run.created_at || 0).getTime()
    return Number.isFinite(ts) && ts >= startOfToday
  })
  const todaySuccess = todayRuns.filter((run) => toUpperStatus(run.status) === 'SUCCESS').length
  const oneHourRuns = runList.filter((run) => {
    const ts = new Date(run.started_at || run.created_at || 0).getTime()
    return Number.isFinite(ts) && ts >= oneHourAgo
  })
  const oneHourFailed = oneHourRuns.filter((run) => toUpperStatus(run.status) === 'FAILED').length

  const durationList = successRuns
    .map((run) => Number(run.duration_ms || 0) / 1000)
    .filter((n) => Number.isFinite(n) && n > 0)
  const avgDuration = durationList.length > 0
    ? Number((durationList.reduce((a, b) => a + b, 0) / durationList.length).toFixed(2))
    : 0

  const successRate = runList.length > 0
    ? Number(((successRuns.length / runList.length) * 100).toFixed(2))
    : 100
  const failureRate = runList.length > 0
    ? Number(((failedRuns.length / runList.length) * 100).toFixed(2))
    : 0
  const hourlyErrorRate = oneHourRuns.length > 0
    ? Number(((oneHourFailed / oneHourRuns.length) * 100).toFixed(2))
    : 0

  dashboardMetrics.value = {
    runningTasks: Number(status?.running_runs || 0),
    todayTotal: todayRuns.length,
    todaySuccess,
    successRate,
    avgDuration,
    hourlyErrorRate
  }

  statistics.value = {
    ...statistics.value,
    successRate,
    failureRate,
    runningTasks: Number(status?.running_runs || 0),
    todayExecutions: todayRuns.length,
    avgExecutionTime: avgDuration,
    maxExecutionTime: durationList.length > 0 ? Number(Math.max(...durationList).toFixed(2)) : 0
  }

  loadTopIssues(runList)
}

const refreshList = async () => {
  loading.value = true
  try {
    const payload = await getKaggleRuns({ page: 1, size: 200 })
    const runs = Array.isArray(payload?.items) ? payload.items : []
    rawRuns.value = runs
    executions.value = runs.map(toExecution)
    await loadMetrics(runs)
  } catch (error) {
    console.error('refreshList failed:', error)
    ElMessage.error('获取任务执行列表失败')
  } finally {
    loading.value = false
  }
}

const handleViewDetails = async (executionId) => {
  const target = executions.value.find((item) => item.id === executionId)
  const runIdentifier = target?.runId || executionId
  detailDrawerVisible.value = true
  detailLoading.value = true
  try {
    const [detail, quality] = await Promise.all([
      getKaggleRunDetail(runIdentifier),
      getKaggleRunQuality(runIdentifier)
    ])
    selectedRunDetail.value = detail || null
    selectedRunQuality.value = quality || null
  } catch (error) {
    selectedRunDetail.value = null
    selectedRunQuality.value = null
    ElMessage.error('加载任务详情失败')
  } finally {
    detailLoading.value = false
  }
}

const handleCancelExecution = async () => {
  ElMessage.warning('当前版本暂不支持取消 Kaggle 同步任务')
}

onMounted(async () => {
  await refreshList()
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

.detail-loading {
  padding: 12px;
}

.quality-kv {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f7f8fa;
  border-radius: 8px;
  padding: 10px 12px;
}

.quality-kv span {
  color: #6b7280;
}

.quality-kv strong {
  font-size: 18px;
  color: #1f2937;
}

.meta-block {
  margin: 0;
  background: #0b1020;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 12px;
  max-height: 300px;
  overflow: auto;
}
</style>
