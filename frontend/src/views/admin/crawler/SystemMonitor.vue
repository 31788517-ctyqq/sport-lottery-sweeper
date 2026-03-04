<template>
  <div class="system-monitor">
    <div class="page-header">
      <h2>{{ T.pageTitle }}</h2>
      <div class="header-actions">
        <el-button type="primary" @click="refreshData(false)">
          <el-icon><Refresh /></el-icon>
          {{ T.refreshData }}
        </el-button>
        <el-button @click="toggleAutoRefresh">
          <el-icon><VideoPlay /></el-icon>
          {{ autoRefresh ? T.disableAutoRefresh : T.enableAutoRefresh }}
        </el-button>
      </div>
    </div>

    <el-row :gutter="16" class="health-row">
      <el-col v-for="item in healthCards" :key="item.name" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="health-card">
          <div class="label">{{ item.name }}</div>
          <div class="value">{{ item.value }}</div>
          <el-tag :type="item.type" size="small">{{ item.tag }}</el-tag>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="section-row">
      <el-col :xs="24" :md="12">
        <el-card shadow="hover">
          <template #header>{{ T.sectionTaskOverview }}</template>
          <div class="kv-list">
            <div class="kv-item"><span>{{ T.kvTotalTasks }}</span><strong>{{ taskStats.totalTasks }}</strong></div>
            <div class="kv-item"><span>{{ T.kvRunningTasks }}</span><strong>{{ taskStats.runningTasks }}</strong></div>
            <div class="kv-item"><span>{{ T.kvRecentExecutions }}</span><strong>{{ taskStats.recentExecutions }}</strong></div>
            <div class="kv-item"><span>{{ T.kvSuccessRate }}</span><strong>{{ taskStats.successRate }}%</strong></div>
          </div>
          <el-table :data="recentTasks" size="small" height="220">
            <el-table-column prop="name" :label="T.tableTask" min-width="160" />
            <el-table-column prop="status" :label="T.tableStatus" width="100">
              <template #default="{ row }">
                <el-tag :type="taskStatusType(row.status)" size="small">{{ taskStatusText(row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="progress" :label="T.tableProgress" width="120">
              <template #default="{ row }">
                <el-progress :percentage="safePercent(row.progress)" :stroke-width="6" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card shadow="hover" v-loading="mappingSyncLoading">
          <template #header>{{ T.sectionMappingSync }}</template>
          <div class="kv-list">
            <div class="kv-item">
              <span>{{ T.kvCurrentStatus }}</span>
              <el-tag :type="mappingStatusTagType">{{ mappingStatusText }}</el-tag>
            </div>
            <div class="kv-item"><span>{{ T.kvPendingConflicts }}</span><strong>{{ mappingSyncStatus.pendingConflicts }}</strong></div>
            <div class="kv-item"><span>{{ T.kvTotalConflicts }}</span><strong>{{ mappingSyncStatus.totalConflicts }}</strong></div>
            <div class="kv-item"><span>{{ T.kvSuccessRate7d }}</span><strong>{{ mappingSyncStatus.syncSuccessRate7d }}%</strong></div>
            <div class="kv-item"><span>{{ T.kvLastFinishedAt }}</span><strong>{{ formatTime(mappingSyncStatus.lastFinishedAt) || '-' }}</strong></div>
            <div class="kv-item"><span>{{ T.kvLastError }}</span><strong>{{ mappingSyncStatus.lastErrorMessage || '-' }}</strong></div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="hover" class="section-row">
      <template #header>
        <div class="alerts-header">
          <span>{{ T.sectionRealtimeAlert }}</span>
          <div class="tags">
            <el-tag type="danger" size="small">{{ T.alertCritical }} {{ alertCounts.critical }}</el-tag>
            <el-tag type="warning" size="small">{{ T.alertWarning }} {{ alertCounts.warning }}</el-tag>
            <el-tag type="info" size="small">{{ T.alertInfo }} {{ alertCounts.info }}</el-tag>
            <el-tag type="success" size="small">{{ T.sourceMappingSync }} {{ mappingSyncAlerts.length }}</el-tag>
          </div>
        </div>
      </template>
      <el-table :data="activeAlerts" v-loading="alertsLoading" height="320">
        <el-table-column prop="severity" :label="T.tableLevel" width="90">
          <template #default="{ row }">
            <el-tag :type="alertTagType(row.severity)" size="small">{{ alertText(row.severity) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="metric_name" :label="T.tableMetric" min-width="180" />
        <el-table-column prop="message" :label="T.tableMessage" min-width="320" />
        <el-table-column :label="T.tableSource" width="120">
          <template #default="{ row }">
            <el-tag :type="row.source === 'entity_mapping' ? 'success' : 'info'" size="small">
              {{ row.source === 'entity_mapping' ? T.sourceMappingSync : T.sourceSystemMonitor }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="triggered_at" :label="T.tableTriggeredAt" width="180">
          <template #default="{ row }">{{ formatTime(row.triggered_at) }}</template>
        </el-table-column>
        <el-table-column :label="T.tableActions" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.source !== 'entity_mapping' && row.status === 'active'"
              size="small"
              @click="handleAcknowledge(row)"
            >
              {{ T.actionAcknowledge }}
            </el-button>
            <el-button size="small" @click="handleViewDetail(row)">{{ T.actionDetail }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card shadow="hover">
      <template #header>{{ T.sectionSystemResource }}</template>
      <el-row :gutter="16">
        <el-col :xs="24" :sm="12" :md="6">
          <ResourceGauge :title="T.resourceCpu" :value="systemResources.cpu" :thresholds="[70, 90]" unit="%" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <ResourceGauge :title="T.resourceMemory" :value="systemResources.memory" :thresholds="[80, 95]" unit="%" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <ResourceGauge :title="T.resourceDisk" :value="systemResources.disk" :thresholds="[85, 95]" unit="%" />
        </el-col>
        <el-col :xs="24" :sm="12" :md="6">
          <ResourceGauge
            :title="T.resourceDbConn"
            :value="systemResources.dbConnections"
            :max="systemResources.dbMaxConnections"
            :unit="T.resourceDbConnUnit"
          />
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh, VideoPlay } from '@element-plus/icons-vue'
import ResourceGauge from '@/components/common/ResourceGauge.vue'
import { acknowledgeAlert, getAlerts, getHealthStatus, getResourcesUsage } from '@/api/crawlerMonitor'
import { getExecutions } from '@/api/taskMonitorApi'
import { getEntityMappingOpsOverview, getEntityMappingSyncStatus } from '@/api/entityMapping'
import { SYSTEM_MONITOR_TEXT as T } from './constants/monitorText'

const autoRefresh = ref(true)
const refreshTimer = ref(null)
const alertsLoading = ref(false)
const mappingSyncLoading = ref(false)

const taskStats = reactive({
  totalTasks: 0,
  runningTasks: 0,
  recentExecutions: 0,
  successRate: 0
})

const recentTasks = ref([])
const activeAlerts = ref([])
const mappingSyncAlerts = ref([])

const alertCounts = reactive({
  critical: 0,
  warning: 0,
  info: 0
})

const systemResources = reactive({
  cpu: 0,
  memory: 0,
  disk: 0,
  dbConnections: 0,
  dbMaxConnections: 100
})

const healthCards = ref([
  { name: T.healthCardSystem, value: '-', tag: T.statusLoading, type: 'info' },
  { name: T.healthCardSuccessRate, value: '-', tag: T.statusLoading, type: 'info' },
  { name: T.healthCardDataQuality, value: '-', tag: T.statusLoading, type: 'info' },
  { name: T.healthCardPerformance, value: '-', tag: T.statusLoading, type: 'info' }
])

const mappingSyncStatus = reactive({
  isRunning: false,
  lastRunStatus: '',
  lastFinishedAt: '',
  lastErrorMessage: '',
  lastErrorAt: '',
  pendingConflicts: 0,
  totalConflicts: 0,
  syncSuccessRate7d: 0
})

const mappingStatusText = computed(() => {
  if (mappingSyncLoading.value) return T.statusLoading
  if (mappingSyncStatus.isRunning) return T.statusRunning
  if (mappingSyncStatus.lastRunStatus === 'failed') return T.statusFailed
  if (mappingSyncStatus.lastRunStatus === 'success') return T.statusSuccess
  return T.statusNotRun
})

const mappingStatusTagType = computed(() => {
  if (mappingSyncLoading.value) return 'info'
  if (mappingSyncStatus.lastRunStatus === 'failed') return 'danger'
  if (mappingSyncStatus.pendingConflicts > 50) return 'warning'
  if (mappingSyncStatus.isRunning) return 'warning'
  return 'success'
})

const unwrapData = (payload) => (
  payload && typeof payload === 'object' && Object.prototype.hasOwnProperty.call(payload, 'data')
    ? payload.data
    : payload || {}
)

const safePercent = (value) => {
  const n = Number(value)
  if (!Number.isFinite(n)) return 0
  return Math.max(0, Math.min(100, Math.round(n)))
}

const formatTime = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  return date.toLocaleString('zh-CN')
}

const taskStatusType = (status) => ({
  RUNNING: 'success',
  SUCCESS: 'primary',
  FAILED: 'danger',
  PENDING: 'warning'
}[String(status || '').toUpperCase()] || 'info')

const taskStatusText = (status) => ({
  RUNNING: T.taskStatusRunning,
  SUCCESS: T.taskStatusSuccess,
  FAILED: T.taskStatusFailed,
  PENDING: T.taskStatusPending
}[String(status || '').toUpperCase()] || status || '-')

const alertTagType = (severity) => ({
  critical: 'danger',
  warning: 'warning',
  info: 'info'
}[String(severity || '').toLowerCase()] || 'info')

const alertText = (severity) => ({
  critical: T.alertCritical,
  warning: T.alertWarning,
  info: T.alertInfo
}[String(severity || '').toLowerCase()] || severity || '-')

const updateAlertCounts = () => {
  alertCounts.critical = activeAlerts.value.filter((item) => item.severity === 'critical').length
  alertCounts.warning = activeAlerts.value.filter((item) => item.severity === 'warning').length
  alertCounts.info = activeAlerts.value.filter((item) => item.severity === 'info').length
}

const buildMappingSyncAlerts = (status) => {
  const alerts = []
  const nowIso = new Date().toISOString()

  if (status.lastRunStatus === 'failed' || status.lastErrorMessage) {
    alerts.push({
      id: 'mapping-sync-failed',
      severity: 'critical',
      metric_name: T.alertMetricSyncFailed,
      message: status.lastErrorMessage || T.alertMessageSyncFailedDefault,
      triggered_at: status.lastErrorAt || nowIso,
      status: 'active',
      source: 'entity_mapping'
    })
  }

  if (status.pendingConflicts >= 50) {
    alerts.push({
      id: 'mapping-conflicts',
      severity: status.pendingConflicts >= 200 ? 'critical' : 'warning',
      metric_name: T.alertMetricPendingConflicts,
      message: `${T.alertMessagePendingConflictsPrefix}${status.pendingConflicts}`,
      triggered_at: nowIso,
      status: 'active',
      source: 'entity_mapping'
    })
  }

  return alerts
}

const loadHealth = async () => {
  try {
    const payload = unwrapData(await getHealthStatus())
    const crawler = payload?.crawlerHealth || {}
    const overallHealthy = String(payload?.overall || '').toLowerCase() === 'healthy'
    const successRate = safePercent(crawler.successRate)
    const quality = safePercent(crawler.dataQuality)
    const performance = safePercent(crawler.responsePerformance)
    const overall = safePercent((successRate + quality + performance) / 3)

    healthCards.value = [
      { name: T.healthCardSystem, value: `${overall}%`, tag: overallHealthy ? T.statusHealthy : T.statusAbnormal, type: overallHealthy ? 'success' : 'danger' },
      { name: T.healthCardSuccessRate, value: `${successRate}%`, tag: successRate >= 90 ? T.statusNormal : T.statusFluctuate, type: successRate >= 90 ? 'success' : 'warning' },
      { name: T.healthCardDataQuality, value: `${quality}%`, tag: quality >= 90 ? T.statusExcellent : T.statusGeneral, type: quality >= 90 ? 'success' : 'warning' },
      { name: T.healthCardPerformance, value: `${performance}%`, tag: performance >= 90 ? T.statusGood : T.statusAttention, type: performance >= 90 ? 'success' : 'warning' }
    ]
  } catch (error) {
    // keep previous health cards
  }
}

const loadTaskStats = async () => {
  try {
    const payload = unwrapData(await getExecutions({ page: 1, page_size: 50 }))
    const dataBlock = payload?.data && typeof payload.data === 'object' ? payload.data : payload
    const items = Array.isArray(dataBlock?.items) ? dataBlock.items : Array.isArray(payload?.items) ? payload.items : []

    recentTasks.value = items.slice(0, 6).map((item) => ({
      id: item.id,
      name: item.task_name || item.name || `${T.taskFallbackNamePrefix}${item.id}`,
      status: item.status,
      progress: item.progress
    }))

    taskStats.totalTasks = Number(dataBlock?.total || payload?.total || items.length || 0)
    taskStats.runningTasks = items.filter((item) => String(item.status || '').toUpperCase() === 'RUNNING').length
    taskStats.recentExecutions = items.length

    const done = items.filter((item) => ['SUCCESS', 'FAILED', 'CANCELLED'].includes(String(item.status || '').toUpperCase()))
    const success = done.filter((item) => String(item.status || '').toUpperCase() === 'SUCCESS').length
    taskStats.successRate = done.length ? Number(((success / done.length) * 100).toFixed(2)) : 0
  } catch (error) {
    recentTasks.value = []
    Object.assign(taskStats, { totalTasks: 0, runningTasks: 0, recentExecutions: 0, successRate: 0 })
  }
}

const loadMappingSyncStatus = async () => {
  mappingSyncLoading.value = true
  try {
    const [sync, overview] = await Promise.all([getEntityMappingSyncStatus(), getEntityMappingOpsOverview()])
    mappingSyncStatus.isRunning = !!sync?.is_running
    mappingSyncStatus.lastRunStatus = sync?.last_run?.status || ''
    mappingSyncStatus.lastFinishedAt = sync?.last_finished_at || sync?.last_run?.finished_at || ''
    mappingSyncStatus.lastErrorMessage = sync?.last_error_message || overview?.last_failed_message || ''
    mappingSyncStatus.lastErrorAt = sync?.last_error_at || overview?.last_failed_at || ''
    mappingSyncStatus.pendingConflicts = Number(overview?.pending_conflicts || 0)
    mappingSyncStatus.totalConflicts = Number(overview?.total_conflicts || 0)
    mappingSyncStatus.syncSuccessRate7d = Number(overview?.sync_success_rate_7d || 0)
  } catch (error) {
    mappingSyncStatus.lastRunStatus = 'failed'
    mappingSyncStatus.lastErrorMessage = T.alertMessageSyncFailedDefault
  } finally {
    mappingSyncAlerts.value = buildMappingSyncAlerts(mappingSyncStatus)
    mappingSyncLoading.value = false
  }
}

const loadAlerts = async () => {
  alertsLoading.value = true
  try {
    const payload = unwrapData(await getAlerts({ page: 1, size: 50, status: 'active' }))
    const dataBlock = payload?.data && typeof payload.data === 'object' ? payload.data : payload
    const baseItems = Array.isArray(dataBlock?.items) ? dataBlock.items : Array.isArray(payload?.items) ? payload.items : []
    const merged = [
      ...mappingSyncAlerts.value,
      ...baseItems.map((item) => ({
        ...item,
        severity: String(item.severity || 'info').toLowerCase(),
        source: 'crawler'
      }))
    ].sort((a, b) => new Date(b.triggered_at || 0).getTime() - new Date(a.triggered_at || 0).getTime())

    activeAlerts.value = merged
    updateAlertCounts()
  } catch (error) {
    activeAlerts.value = [...mappingSyncAlerts.value]
    updateAlertCounts()
  } finally {
    alertsLoading.value = false
  }
}

const loadResources = async () => {
  try {
    const payload = unwrapData(await getResourcesUsage())
    systemResources.cpu = Number(payload?.cpu || 0)
    systemResources.memory = Number(payload?.memory || 0)
    systemResources.disk = Number(payload?.disk || 0)
    systemResources.dbConnections = Number(payload?.dbConnections || 0)
    systemResources.dbMaxConnections = Number(payload?.dbMaxConnections || 100)
  } catch (error) {
    // keep previous resource values
  }
}

const refreshData = async (silent = true) => {
  await loadMappingSyncStatus()
  await Promise.all([loadHealth(), loadTaskStats(), loadAlerts(), loadResources()])
  if (!silent) ElMessage.success(T.toastRefreshDone)
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer.value = setInterval(() => refreshData(true), 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer.value) {
    clearInterval(refreshTimer.value)
    refreshTimer.value = null
  }
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
    ElMessage.success(T.autoRefreshEnabled)
  } else {
    stopAutoRefresh()
    ElMessage.info(T.autoRefreshDisabled)
  }
}

const handleAcknowledge = async (row) => {
  if (row.source === 'entity_mapping') {
    ElMessage.info(T.toastMappingAlertHint)
    return
  }
  try {
    await acknowledgeAlert(row.id)
    ElMessage.success(T.toastAlertAckSuccess)
    await loadAlerts()
  } catch (error) {
    ElMessage.error(T.toastAlertAckFailed)
  }
}

const handleViewDetail = (row) => {
  ElMessage.info(`${row.metric_name || T.sectionRealtimeAlert}：${row.message || '-'}`)
}

onMounted(async () => {
  await refreshData(true)
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
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

.header-actions {
  display: flex;
  gap: 10px;
}

.health-row,
.section-row {
  margin-bottom: 16px;
}

.health-card .label {
  color: #7a8599;
  font-size: 13px;
}

.health-card .value {
  margin: 6px 0 10px;
  font-size: 24px;
  font-weight: 700;
  color: #2f3a4f;
}

.kv-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.kv-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 6px;
  border-bottom: 1px dashed #e6ebf2;
}

.kv-item:last-child {
  border-bottom: none;
}

.kv-item span {
  color: #66758a;
}

.kv-item strong {
  color: #2f3a4f;
}

.alerts-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.alerts-header .tags {
  display: flex;
  gap: 8px;
}
</style>
