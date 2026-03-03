<template>
  <div class="data-center">
    <!-- Breadcrumb -->
    <el-breadcrumb separator="/" class="breadcrumb">
      <el-breadcrumb-item :to="{ path: '/admin' }">{{ T.breadcrumbHome }}</el-breadcrumb-item>
      <el-breadcrumb-item :to="{ path: '/admin/data-source' }">{{ T.breadcrumbDataSource }}</el-breadcrumb-item>
      <el-breadcrumb-item>{{ T.breadcrumbDataCenter }}</el-breadcrumb-item>
    </el-breadcrumb>

    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h2>{{ T.pageTitle }}</h2>
        <p class="subtitle">{{ T.pageSubtitle }}</p>
      </div>
      <div class="header-right">
        <el-button type="primary" @click="handleRefresh">
          <el-icon><Refresh /></el-icon>
          {{ T.refreshData }}
        </el-button>
        <el-button type="success" @click="handleExport">
          <el-icon><Download /></el-icon>
          {{ T.exportData }}
        </el-button>
      </div>
    </div>

    <!-- Stats Cards -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card primary">
            <div class="stat-content">
              <div class="stat-number">{{ stats.totalMatches }}</div>
              <div class="stat-label">{{ T.statTotalMatches }}</div>
              <div class="stat-trend positive">
                <el-icon><ArrowUp /></el-icon>
                {{ stats.matchGrowth }}%
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card success">
            <div class="stat-content">
              <div class="stat-number">{{ stats.activeSources }}</div>
              <div class="stat-label">{{ T.statActiveSources }}</div>
              <div class="stat-trend positive">
                <el-icon><ArrowUp /></el-icon>
                {{ stats.sourceGrowth }}%
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card warning">
            <div class="stat-content">
              <div class="stat-number">{{ stats.dataQuality }}%</div>
              <div class="stat-label">{{ T.statDataQuality }}</div>
              <div class="stat-trend" :class="stats.qualityTrend === 'up' ? 'positive' : 'negative'">
                <el-icon><ArrowUp v-if="stats.qualityTrend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.qualityChange) }}%
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card danger">
            <div class="stat-content">
              <div class="stat-number">{{ stats.errorRate }}%</div>
              <div class="stat-label">{{ T.statErrorRate }}</div>
              <div class="stat-trend negative">
                <el-icon><ArrowDown /></el-icon>
                {{ stats.errorImprovement }}%
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card info">
            <div class="stat-content">
              <div class="stat-number">{{ stats.avgResponseTime }}ms</div>
              <div class="stat-label">{{ T.statAvgResponse }}</div>
              <div class="stat-trend positive">
                <el-icon><ArrowDown /></el-icon>
                {{ stats.responseImprovement }}%
              </div>
            </div>
          </el-card>
        </el-col>
        <el-col :xs="12" :sm="6" :lg="3">
          <el-card class="stat-card purple">
            <div class="stat-content">
              <div class="stat-number">{{ stats.storageUsed }}GB</div>
              <div class="stat-label">{{ T.statStorageUsed }}</div>
              <div class="stat-trend" :class="stats.storageTrend === 'up' ? 'warning' : 'positive'">
                <el-icon><ArrowUp v-if="stats.storageTrend === 'up'" /><ArrowDown v-else /></el-icon>
                {{ Math.abs(stats.storageChange) }}%
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Filters -->
    <div class="filter-section">
      <el-card>
        <el-form :model="filters" :inline="true" class="filter-form">
          <el-form-item :label="T.filterDataType">
            <el-select v-model="filters.dataType" :placeholder="T.placeholderSelectDataType" clearable>
              <el-option :label="T.optionMatchData" value="matches" />
              <el-option :label="T.optionOddsData" value="odds" />
              <el-option :label="T.optionEventData" value="events" />
              <el-option :label="T.optionStatData" value="statistics" />
            </el-select>
          </el-form-item>
          <el-form-item :label="T.filterSource">
            <el-select v-model="filters.sourceId" :placeholder="T.placeholderSelectSource" clearable>
              <el-option v-for="source in sources" :key="source.id" :label="source.name" :value="source.id" />
            </el-select>
          </el-form-item>
          <el-form-item :label="T.filterDateRange">
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              :range-separator="T.rangeSeparator"
              :start-placeholder="T.startDate"
              :end-placeholder="T.endDate"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item :label="T.filterStatus">
            <el-select v-model="filters.status" :placeholder="T.placeholderSelectStatus" clearable>
              <el-option :label="T.statusNormal" value="normal" />
              <el-option :label="T.statusError" value="error" />
              <el-option :label="T.statusWarning" value="warning" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">{{ T.search }}</el-button>
            <el-button @click="handleReset">{{ T.reset }}</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- Content -->
    <div class="content-section">
      <el-card>
        <template #header>
          <div class="card-header">
            <div class="header-tabs">
              <el-radio-group v-model="viewMode" size="large">
                <el-radio-button value="table">{{ T.viewTable }}</el-radio-button>
                <el-radio-button value="chart">{{ T.viewChart }}</el-radio-button>
                <el-radio-button value="dashboard">{{ T.viewDashboard }}</el-radio-button>
              </el-radio-group>
            </div>
            <div class="header-actions">
              <el-button-group>
                <el-button :type="showChart ? 'primary' : ''" @click="toggleChart">
                  <el-icon><TrendCharts /></el-icon>
                  {{ T.chart }}
                </el-button>
                <el-button :type="showHeatmap ? 'primary' : ''" @click="toggleHeatmap">
                  <el-icon><Grid /></el-icon>
                  {{ T.heatmap }}
                </el-button>
              </el-button-group>
            </div>
          </div>
        </template>

        <!-- Table View -->
        <div v-show="viewMode === 'table'" class="table-view">
          <el-table
            :data="filteredData"
            v-loading="loading"
            style="width: 100%"
            @selection-change="handleSelectionChange"
            stripe
            border
          >
            <el-table-column type="selection" width="55" />
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="type" :label="T.columnType" width="100">
              <template #default="scope">
                <el-tag :type="getTypeColor(scope.row.type)">{{ getTypeText(scope.row.type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sourceName" :label="T.columnSource" width="120" />
            <el-table-column prop="title" :label="T.columnTitle" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" :label="T.columnStatus" width="100">
              <template #default="scope">
                <el-tag :type="getStatusColor(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="quality" :label="T.columnQuality" width="120">
              <template #default="scope">
                <el-progress :percentage="scope.row.quality" :color="getQualityColor(scope.row.quality)" />
              </template>
            </el-table-column>
            <el-table-column prop="recordCount" :label="T.columnRecordCount" width="100" />
            <el-table-column prop="createdAt" :label="T.columnCreatedAt" width="170" />
            <el-table-column prop="updatedAt" :label="T.columnUpdatedAt" width="170" />
            <el-table-column :label="T.columnActions" width="200" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="viewDetails(scope.row)">{{ T.actionDetail }}</el-button>
                <el-button size="small" type="primary" @click="viewOdds(scope.row)">{{ T.actionOdds }}</el-button>
                <el-dropdown @command="handleCommand($event, scope.row)">
                  <el-button size="small">
                    {{ T.actionMore }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item command="analyze">{{ T.actionAnalyze }}</el-dropdown-item>
                      <el-dropdown-item command="export">{{ T.actionExportItem }}</el-dropdown-item>
                      <el-dropdown-item command="refresh" divided>{{ T.actionRefresh }}</el-dropdown-item>
                      <el-dropdown-item command="delete" divided class="text-danger">{{ T.actionDelete }}</el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </template>
            </el-table-column>
          </el-table>

          <!-- Pagination -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.size"
              :total="pagination.total"
              :page-sizes="[10, 20, 50, 100]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>
        </div>

        <!-- Chart View -->
        <div v-show="viewMode === 'chart'" class="chart-view">
          <div class="chart-container">
            <div ref="mainChart" class="main-chart"></div>
            <div class="chart-sidebar">
              <div ref="pieChart" class="side-chart"></div>
              <div ref="trendChart" class="side-chart"></div>
            </div>
          </div>
        </div>

        <!-- Dashboard View -->
        <div v-show="viewMode === 'dashboard'" class="dashboard-view">
          <el-row :gutter="20">
            <el-col :span="16">
              <div ref="realtimeChart" class="realtime-chart"></div>
            </el-col>
            <el-col :span="8">
              <el-card class="realtime-stats">
                <template #header>{{ T.realtimeStatsTitle }}</template>
                <div class="realtime-item">
                  <span class="label">{{ T.realtimeCurrentSpeed }}</span>
                  <span class="value">{{ realtimeStats.currentSpeed }}/s</span>
                </div>
                <div class="realtime-item">
                  <span class="label">{{ T.realtimeQueueLength }}</span>
                  <span class="value">{{ realtimeStats.queueLength }}</span>
                </div>
                <div class="realtime-item">
                  <span class="label">{{ T.realtimeSuccessRate }}</span>
                  <span class="value">{{ realtimeStats.successRate }}%</span>
                </div>
                <div class="realtime-item">
                  <span class="label">{{ T.realtimeActiveConnections }}</span>
                  <span class="value">{{ realtimeStats.activeConnections }}</span>
                </div>
              </el-card>
            </el-col>
          </el-row>
        </div>
      </el-card>
    </div>

    <!-- Detail Drawer -->
    <el-drawer
      v-model="detailVisible"
      :title="T.drawerDataDetail"
      size="60%"
      direction="rtl"
    >
      <MatchDetail v-if="selectedItem" :match-data="selectedItem" />
    </el-drawer>

    <!-- Odds Drawer -->
    <el-drawer
      v-model="oddsVisible"
      :title="T.drawerOddsDetail"
      size="50%"
      direction="rtl"
    >
      <OddsDetail v-if="selectedItem" :odds-data="selectedItem" />
    </el-drawer>

    <!-- Export Dialog -->
    <el-dialog
      v-model="exportVisible"
      :title="T.exportDialogTitle"
      width="500px"
    >
      <el-form :model="exportForm" label-width="100px">
        <el-form-item :label="T.exportFormat">
          <el-radio-group v-model="exportForm.format">
            <el-radio value="excel">Excel</el-radio>
            <el-radio value="csv">CSV</el-radio>
            <el-radio value="json">JSON</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="T.exportScope">
          <el-checkbox-group v-model="exportForm.scope">
            <el-checkbox value="current">{{ T.exportCurrentPage }}</el-checkbox>
            <el-checkbox value="selected">{{ T.exportSelectedPage }}</el-checkbox>
            <el-checkbox value="all">{{ T.exportAllData }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        <el-form-item :label="T.exportDateRange">
          <el-date-picker
            v-model="exportForm.dateRange"
            type="daterange"
            :range-separator="T.rangeSeparator"
            :start-placeholder="T.startDate"
            :end-placeholder="T.endDate"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="exportVisible = false">{{ T.cancel }}</el-button>
          <el-button type="primary" @click="confirmExport">{{ T.confirmExport }}</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Download,
  ArrowUp,
  ArrowDown,
  TrendCharts,
  Grid
} from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import MatchDetail from '@/components/MatchDetail.vue'
import OddsDetail from '@/components/OddsDetail.vue'
import {
  getSummaryStats,
  getDataCenterTrend,
  getDataCenterSourceDistribution,
  getDataCenterRealtime
} from '@/api/modules/stats'
import {
  getDataCenterTableData,
  exportDataCenterTable,
  getDataCenterSourceOptions
} from '@/api/modules/data-center'
import { DATA_CENTER_TEXT as T } from './constants/monitorText'

const REALTIME_REFRESH_MS = 10000
const TREND_DAYS = 7
const REALTIME_POINTS = 20
const REALTIME_INTERVAL_MINUTES = 5

const unwrapPayload = (response) => {
  if (!response || typeof response !== 'object' || Array.isArray(response)) {
    return response
  }
  if (Object.prototype.hasOwnProperty.call(response, 'data')) {
    return response.data
  }
  return response
}

const loading = ref(false)
const viewMode = ref('table')
const detailVisible = ref(false)
const oddsVisible = ref(false)
const exportVisible = ref(false)
const showChart = ref(true)
const showHeatmap = ref(false)
const selectedItem = ref(null)
const mainChart = ref(null)
const pieChart = ref(null)
const trendChart = ref(null)
const realtimeChart = ref(null)

const stats = reactive({
  totalMatches: 0,
  activeSources: 0,
  dataQuality: 0,
  errorRate: 0,
  avgResponseTime: 0,
  storageUsed: 0,
  matchGrowth: 0,
  sourceGrowth: 0,
  qualityTrend: 'up',
  qualityChange: 0,
  errorImprovement: 0,
  responseImprovement: 0,
  storageTrend: 'up',
  storageChange: 0
})

const filters = reactive({
  dataType: '',
  sourceId: '',
  dateRange: [],
  status: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

const fallbackSources = [
  { id: 1, name: T.sourceOfficial },
  { id: 2, name: T.sourceCrawler }
]
const sources = ref([])

const tableData = ref([])
const filteredData = ref([])

const chartData = reactive({
  trendLabels: [],
  matchSeries: [],
  oddsSeries: [],
  spSeries: [],
  qualitySeries: [],
  sourceDistribution: [],
  realtimeLabels: [],
  realtimeSpeed: []
})

const realtimeStats = reactive({
  currentSpeed: 0,
  queueLength: 0,
  successRate: 0,
  activeConnections: 0
})

const exportForm = reactive({
  format: 'excel',
  scope: ['current'],
  dateRange: []
})

const selectedRows = ref([])
const realtimeTimer = ref(null)

onMounted(async () => {
  await initializePage()
})

onUnmounted(() => {
  stopRealtimeUpdate()
  disposeCharts()
})

watch(
  () => viewMode.value,
  (mode) => {
    nextTick(() => {
      if (mode === 'chart') {
        initMainChart()
        initPieChart()
        initTrendChart()
      } else if (mode === 'dashboard') {
        initRealtimeChart()
      }
    })
  }
)

const initializePage = async () => {
  await Promise.all([
    loadSourceOptions(),
    loadStats(),
    loadTableData(),
    loadChartData(),
    loadRealtimeData()
  ])

  initCharts()
  startRealtimeUpdate()
}

const loadStats = async () => {
  try {
    const res = await getSummaryStats()
    const payload = unwrapPayload(res) || {}

    Object.assign(stats, {
      totalMatches: Number(payload.totalMatches || 0),
      activeSources: Number(payload.activeSources || 0),
      dataQuality: Number(payload.dataQuality || 0),
      errorRate: Number(payload.errorRate || 0),
      avgResponseTime: Number(payload.avgResponseTime || 0),
      storageUsed: Number(payload.storageUsed || 0),
      matchGrowth: Number(payload.matchGrowth || 0),
      sourceGrowth: Number(payload.sourceGrowth || 0),
      qualityTrend: payload.qualityTrend || 'up',
      qualityChange: Number(payload.qualityChange || 0),
      errorImprovement: Number(payload.errorImprovement || 0),
      responseImprovement: Number(payload.responseImprovement || 0),
      storageTrend: payload.storageTrend || 'up',
      storageChange: Number(payload.storageChange || 0)
    })
  } catch (error) {
    ElMessage.error(T.toastLoadStatsFailed)
    console.error('Error loading stats:', error)
  }
}

const loadSourceOptions = async () => {
  try {
    const res = await getDataCenterSourceOptions({ page: 1, size: 100 })
    const payload = unwrapPayload(res) || {}
    const items = Array.isArray(payload.items) ? payload.items : []
    sources.value = items
      .filter((item) => item && item.id != null)
      .map((item) => ({
        id: item.id,
        name: item.name || `${T.sourcePrefix}${item.id}`
      }))

    if (!sources.value.length) {
      sources.value = [...fallbackSources]
    }
  } catch (error) {
    sources.value = [...fallbackSources]
    console.warn('Failed to load source options, fallback to defaults:', error)
  }
}

const loadTableData = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size
    }

    if (filters.dataType) {
      params.type = filters.dataType
    }
    if (filters.sourceId) {
      params.source_id = filters.sourceId
    }
    if (filters.status) {
      params.status = filters.status
    }
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0]
      params.end_date = filters.dateRange[1]
    }

    const res = await getDataCenterTableData(params)
    const payload = unwrapPayload(res) || {}
    tableData.value = Array.isArray(payload.items) ? payload.items : []
    pagination.total = Number(payload.total || 0)
    applyFilters()
  } catch (error) {
    ElMessage.error(T.toastLoadDataFailed)
    console.error('Error loading table data:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  filteredData.value = [...tableData.value]
}

const loadChartData = async () => {
  await Promise.all([loadTrendData(), loadSourceDistribution()])
  nextTick(() => {
    initMainChart()
    initPieChart()
    initTrendChart()
  })
}

const loadTrendData = async () => {
  try {
    const res = await getDataCenterTrend({ days: TREND_DAYS })
    const payload = unwrapPayload(res) || {}

    chartData.trendLabels = Array.isArray(payload.labels) ? payload.labels : []
    chartData.matchSeries = Array.isArray(payload.matches) ? payload.matches.map((n) => Number(n || 0)) : []
    chartData.oddsSeries = Array.isArray(payload.odds) ? payload.odds.map((n) => Number(n || 0)) : []
    chartData.spSeries = Array.isArray(payload.spRecords) ? payload.spRecords.map((n) => Number(n || 0)) : []
    chartData.qualitySeries = Array.isArray(payload.quality) ? payload.quality.map((n) => Number(n || 0)) : []
  } catch (error) {
    console.error('Error loading trend data:', error)
    chartData.trendLabels = []
    chartData.matchSeries = []
    chartData.oddsSeries = []
    chartData.spSeries = []
    chartData.qualitySeries = []
  }
}

const loadSourceDistribution = async () => {
  try {
    const res = await getDataCenterSourceDistribution()
    const payload = unwrapPayload(res) || {}
    const items = Array.isArray(payload.items) ? payload.items : []

    chartData.sourceDistribution = items.map((item) => ({
      name: item.name || T.sourceUnknown,
      value: Number(item.value || 0)
    }))
  } catch (error) {
    console.error('Error loading source distribution:', error)
    chartData.sourceDistribution = []
  }
}

const loadRealtimeData = async () => {
  try {
    const res = await getDataCenterRealtime({
      points: REALTIME_POINTS,
      interval_minutes: REALTIME_INTERVAL_MINUTES
    })
    const payload = unwrapPayload(res) || {}

    const snapshot = payload.snapshot || {}
    const history = payload.history || {}

    realtimeStats.currentSpeed = Number(snapshot.currentSpeed || 0)
    realtimeStats.queueLength = Number(snapshot.queueLength || 0)
    realtimeStats.successRate = Number(snapshot.successRate || 0)
    realtimeStats.activeConnections = Number(snapshot.activeConnections || 0)

    chartData.realtimeLabels = Array.isArray(history.labels) ? history.labels : []
    chartData.realtimeSpeed = Array.isArray(history.speed)
      ? history.speed.map((n) => Number(n || 0))
      : []

    updateRealtimeChart()
  } catch (error) {
    console.error('Error loading realtime data:', error)
  }
}

const handleSearch = async () => {
  pagination.page = 1
  await loadTableData()
}

const handleReset = async () => {
  Object.keys(filters).forEach((key) => {
    filters[key] = key === 'dateRange' ? [] : ''
  })
  pagination.page = 1
  await loadTableData()
}

const handleRefresh = async () => {
  await Promise.all([loadStats(), loadTableData(), loadChartData(), loadRealtimeData()])
  ElMessage.success(T.toastDataRefreshed)
}

const handleExport = () => {
  exportVisible.value = true
}

const confirmExport = async () => {
  try {
    ElMessage.info(T.toastExportCreating)

    const exportParams = {
      format: exportForm.format,
      scope: exportForm.scope,
      dateRange: exportForm.dateRange
    }

    const res = await exportDataCenterTable(exportParams)
    const payload = unwrapPayload(res) || {}
    const fileName = payload.fileName || 'data_export'
    ElMessage.success(`${T.toastExportCreated}: ${fileName}`)
    exportVisible.value = false
  } catch (error) {
    ElMessage.error(T.toastExportFailed)
    console.error('Export failed:', error)
  }
}

const viewDetails = (row) => {
  selectedItem.value = row
  detailVisible.value = true
}

const viewOdds = (row) => {
  selectedItem.value = row
  oddsVisible.value = true
}

const handleCommand = (command, row) => {
  switch (command) {
    case 'analyze':
      ElMessage.info(T.toastOpenAnalyze)
      break
    case 'export':
      ElMessage.info(T.toastExportSingle)
      break
    case 'refresh':
      refreshItem(row)
      break
    case 'delete':
      deleteItem(row)
      break
    default:
      break
  }
}

const refreshItem = async (row) => {
  try {
    await ElMessageBox.confirm(
      `${T.confirmRefreshQuestionStart}"${row.title}"${T.confirmRefreshQuestionEnd}`,
      T.confirmRefreshTitle,
      {
      type: 'warning'
      }
    )
    ElMessage.success(T.toastRefreshSubmitted)
  } catch {
    // no-op
  }
}

const deleteItem = async (row) => {
  try {
    await ElMessageBox.confirm(
      `${T.confirmDeleteQuestionStart}"${row.title}"${T.confirmDeleteQuestionEnd}`,
      T.confirmDeleteTitle,
      {
      type: 'error'
      }
    )
    const index = tableData.value.findIndex((item) => item.id === row.id)
    if (index > -1) {
      tableData.value.splice(index, 1)
      applyFilters()
      ElMessage.success(T.toastDeleteSuccess)
    }
  } catch {
    // no-op
  }
}

const handleSelectionChange = (selection) => {
  selectedRows.value = selection
}

const handleSizeChange = async (size) => {
  pagination.size = size
  pagination.page = 1
  await loadTableData()
}

const handleCurrentChange = async (page) => {
  pagination.page = page
  await loadTableData()
}

const toggleChart = () => {
  showChart.value = !showChart.value
  if (showChart.value) {
    nextTick(() => {
      initMainChart()
      initPieChart()
      initTrendChart()
    })
  }
}

const toggleHeatmap = () => {
  showHeatmap.value = !showHeatmap.value
}

const initCharts = () => {
  nextTick(() => {
    initMainChart()
    initPieChart()
    initTrendChart()
    initRealtimeChart()
  })
}

const getChartInstance = (domRef) => {
  if (!domRef) return null
  if (!domRef.clientWidth || !domRef.clientHeight) return null
  const existing = echarts.getInstanceByDom(domRef)
  return existing || echarts.init(domRef)
}

const disposeCharts = () => {
  ;[mainChart.value, pieChart.value, trendChart.value, realtimeChart.value].forEach((domRef) => {
    if (!domRef) return
    const chart = echarts.getInstanceByDom(domRef)
    if (chart) {
      chart.dispose()
    }
  })
}

const initMainChart = () => {
  if (!mainChart.value) return

  const labels = chartData.trendLabels.length ? chartData.trendLabels : ['--']
  const matchSeries = chartData.matchSeries.length ? chartData.matchSeries : [0]
  const oddsSeries = chartData.oddsSeries.length ? chartData.oddsSeries : [0]
  const spSeries = chartData.spSeries.length ? chartData.spSeries : [0]

  const chart = getChartInstance(mainChart.value)
  if (!chart) return

  chart.setOption({
    title: {
      text: T.chartTrendTitle,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: [T.chartLegendMatches, T.chartLegendOdds, T.chartLegendSp],
      top: '10%'
    },
    xAxis: {
      type: 'category',
      data: labels
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: T.chartLegendMatches,
        type: 'line',
        smooth: true,
        data: matchSeries
      },
      {
        name: T.chartLegendOdds,
        type: 'line',
        smooth: true,
        data: oddsSeries
      },
      {
        name: T.chartLegendSp,
        type: 'line',
        smooth: true,
        data: spSeries
      }
    ]
  })
}

const initPieChart = () => {
  if (!pieChart.value) return

  const chart = getChartInstance(pieChart.value)
  if (!chart) return

  const pieItems = chartData.sourceDistribution.length
    ? chartData.sourceDistribution
    : [{ name: T.chartPieNoData, value: 1 }]

  chart.setOption({
    title: {
      text: T.chartPieTitle,
      left: 'center'
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '50%',
        data: pieItems,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  })
}

const initTrendChart = () => {
  if (!trendChart.value) return

  const chart = getChartInstance(trendChart.value)
  if (!chart) return

  const labels = chartData.trendLabels.length ? chartData.trendLabels : ['--']
  const quality = chartData.qualitySeries.length ? chartData.qualitySeries : [0]

  chart.setOption({
    title: {
      text: T.chartQualityTitle,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: labels
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        type: 'line',
        smooth: true,
        data: quality,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(54, 162, 235, 0.3)' },
            { offset: 1, color: 'rgba(54, 162, 235, 0.1)' }
          ])
        }
      }
    ]
  })
}

const initRealtimeChart = () => {
  if (!realtimeChart.value) return

  const chart = getChartInstance(realtimeChart.value)
  if (!chart) return

  chart.setOption({
    title: {
      text: T.chartRealtimeTitle,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.realtimeLabels.length ? chartData.realtimeLabels : ['--']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: T.chartRealtimeSpeed,
        type: 'line',
        smooth: true,
        data: chartData.realtimeSpeed.length ? chartData.realtimeSpeed : [0]
      }
    ]
  })
}

const updateRealtimeChart = () => {
  if (!realtimeChart.value) return
  const chart = echarts.getInstanceByDom(realtimeChart.value)
  if (!chart) return

  chart.setOption({
    xAxis: {
      data: chartData.realtimeLabels.length ? chartData.realtimeLabels : ['--']
    },
    series: [
      {
        data: chartData.realtimeSpeed.length ? chartData.realtimeSpeed : [0]
      }
    ]
  })
}

const startRealtimeUpdate = () => {
  stopRealtimeUpdate()
  realtimeTimer.value = setInterval(() => {
    loadRealtimeData()
  }, REALTIME_REFRESH_MS)
}

const stopRealtimeUpdate = () => {
  if (realtimeTimer.value) {
    clearInterval(realtimeTimer.value)
    realtimeTimer.value = null
  }
}

const getTypeColor = (type) => {
  const colors = {
    matches: 'primary',
    odds: 'success',
    events: 'warning',
    statistics: 'info'
  }
  return colors[type] || 'info'
}

const getTypeText = (type) => {
  const texts = T.typeTextMap
  return texts[type] || type
}

const getStatusColor = (status) => {
  const colors = {
    normal: 'success',
    error: 'danger',
    warning: 'warning'
  }
  return colors[status] || 'info'
}

const getStatusText = (status) => {
  const texts = T.statusTextMap
  return texts[status] || status
}

const getQualityColor = (quality) => {
  if (quality >= 90) return '#67C23A'
  if (quality >= 70) return '#E6A23C'
  return '#F56C6C'
}
</script>

<style scoped lang="scss">

.data-center {
  padding: var(--spacing-xl);
  background-color: var(--color-bg-light);
  min-height: 100vh;

  .breadcrumb {
    margin-bottom: var(--spacing-lg);
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: var(--spacing-xl);
    padding: var(--spacing-xl);
    background: var(--color-white);
    border-radius: var(--border-radius-large);
    box-shadow: var(--box-shadow-sm);

    .header-left h2 {
      margin: 0 0 var(--spacing-sm) 0;
      color: var(--color-text-primary);
      font-size: var(--font-size-xl);
      font-weight: var(--font-weight-semibold);
      line-height: 1.2;
    }

    .subtitle {
      margin: 0;
      color: var(--color-text-secondary);
      font-size: var(--font-size-base);
      font-weight: var(--font-weight-normal);
    }

    .header-right {
      display: flex;
      gap: var(--spacing-sm);
    }
  }

  .stats-section {
    margin-bottom: var(--spacing-xl);

    .stat-card {
      transition: all var(--transition-base);
      cursor: pointer;
      border: none;
      position: relative;
      overflow: hidden;

      &::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--card-accent-color);
      }

      &:hover {
        transform: translateY(-4px);
        box-shadow: var(--box-shadow-lg);
      }

        .stat-content {
          text-align: center;
          padding: var(--spacing-md) var(--spacing-sm);

          .stat-number {
            font-size: var(--font-size-xxl);
            font-weight: var(--font-weight-bold);
            color: var(--card-accent-color);
            margin-bottom: var(--spacing-xs);
            line-height: 1.2;
          }

          .stat-label {
            font-size: var(--font-size-sm);
            color: var(--color-text-secondary);
            margin-bottom: var(--spacing-sm);
            font-weight: var(--font-weight-medium);
          }

          .stat-trend {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: var(--spacing-xs);
            font-size: var(--font-size-xs);
            padding: 2px 8px;
            border-radius: var(--border-radius-base);
            background: rgba(var(--trend-color), 0.1);
            color: rgb(var(--trend-color));

          &.positive {
            --trend-color: 103, 194, 58;
          }

          &.negative {
            --trend-color: 245, 108, 108;
          }

          &.warning {
            --trend-color: 230, 162, 60;
          }
        }
      }

      // Dynamic card accent colors via CSS variables
      &.primary { --card-accent-color: #409EFF; }
      &.success { --card-accent-color: #67C23A; }
      &.warning { --card-accent-color: #E6A23C; }
      &.danger { --card-accent-color: #F56C6C; }
      &.info { --card-accent-color: #909399; }
      &.purple { --card-accent-color: #722ED1; }
    }
  }

  .filter-section {
    margin-bottom: var(--spacing-xl);

    .filter-form {
      margin: 0;
      .el-form-item {
        margin-bottom: var(--spacing-md);
      }
    }
  }

  .content-section {
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: var(--spacing-md);

        .header-tabs {
          display: flex;
          gap: var(--spacing-xs);
        }

        .header-actions {
          display: flex;
          gap: var(--spacing-xs);
        }
      }

    .table-view {
      .pagination-wrapper {
        margin-top: var(--spacing-xl);
        display: flex;
        justify-content: center;
        padding-top: var(--spacing-lg);
        border-top: 1px solid var(--color-border-lighter);
      }

      // Table style optimization
      .el-table {
        border-radius: var(--border-radius-base);
        overflow: hidden;
        
        .el-table__header th {
          background-color: var(--color-bg-lighter);
          color: var(--color-text-primary);
          font-weight: var(--font-weight-semibold);
          height: 50px;
        }
        
        .el-table__row {
          height: 60px;
          
          &:hover {
            background-color: var(--color-bg-lighter);
          }
        }
        
        .el-progress {
          .el-progress-bar__outer {
            background-color: var(--color-border-lighter);
          }
        }
      }
    }

    .chart-view {
      .chart-container {
        display: flex;
        gap: var(--spacing-lg);

        .main-chart {
          flex: 1;
          height: 400px;
          background: var(--color-white);
          border-radius: var(--border-radius-base);
          padding: var(--spacing-md);
          box-shadow: var(--box-shadow-sm);
        }

        .chart-sidebar {
          width: 320px;
          display: flex;
          flex-direction: column;
          gap: var(--spacing-lg);

          .side-chart {
            height: 180px;
            background: var(--color-white);
            border-radius: var(--border-radius-base);
            padding: var(--spacing-sm);
            box-shadow: var(--box-shadow-sm);
          }
        }
      }
    }

    .dashboard-view {
      .realtime-chart {
        height: 400px;
        background: var(--color-white);
        border-radius: var(--border-radius-base);
        padding: var(--spacing-md);
        box-shadow: var(--box-shadow-sm);
      }

      .realtime-stats {
        .realtime-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: var(--spacing-md) 0;
          border-bottom: 1px solid var(--color-border-lighter);

          &:first-child {
            padding-top: 0;
          }

          &:last-child {
            border-bottom: none;
            padding-bottom: 0;
          }

          .label {
            color: var(--color-text-secondary);
            font-size: var(--font-size-base);
            font-weight: var(--font-weight-medium);
          }

          .value {
            font-weight: var(--font-weight-bold);
            color: var(--color-text-primary);
            font-size: var(--font-size-lg);
          }
        }
      }
    }
  }

  .text-danger {
    color: var(--color-danger);
  }
}

// Responsive layout
@media (max-width: 768px) {
  .data-center {
    padding: var(--spacing-md);

    .page-header {
      flex-direction: column;
      gap: var(--spacing-md);
      text-align: center;
      padding: var(--spacing-lg);
    }

    .stats-section {
      .el-col {
        margin-bottom: var(--spacing-md);
      }
    }

    .content-section {
      .card-header {
        flex-direction: column;
        align-items: stretch;
      }
    }

    .chart-view .chart-container {
      flex-direction: column;
      gap: var(--spacing-md);

      .chart-sidebar {
        width: 100%;
        flex-direction: row;

        .side-chart {
          flex: 1;
          min-height: 160px;
        }
      }
    }

    .table-view {
      .el-table {
        font-size: var(--font-size-sm);
        
        .el-table__header th,
        .el-table__row {
          height: 44px;
        }
      }
    }
  }
}
</style>

