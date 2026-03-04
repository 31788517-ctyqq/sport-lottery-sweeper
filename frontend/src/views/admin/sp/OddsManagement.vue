<template>
  <div class="odds-management-container">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>赔率管理</h2>
      <p class="page-description">实时监控、分析和管理赔率数据</p>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-button type="primary" :icon="VideoPlay" @click="startMonitoring">
        开始监控
      </el-button>
      <el-button type="success" :icon="Histogram" @click="analyzeTrends">
        趋势分析
      </el-button>
      <el-button type="warning" :icon="Warning" @click="detectAnomalies">
        异常检测
      </el-button>
      <el-button type="info" :icon="Download" @click="exportData">
        导出数据
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.totalOdds }}</div>
              <div class="stats-label">总赔率记录</div>
            </div>
            <el-icon class="stats-icon"><Document /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.monitoredMatches }}</div>
              <div class="stats-label">监控比赛</div>
            </div>
            <el-icon class="stats-icon"><Monitor /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.anomaliesDetected }}</div>
              <div class="stats-label">异常检测</div>
            </div>
            <el-icon class="stats-icon"><Warning /></el-icon>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stats-card">
            <div class="stats-content">
              <div class="stats-number">{{ stats.changesToday }}%</div>
              <div class="stats-label">今日变动</div>
            </div>
            <el-icon class="stats-icon"><TrendCharts /></el-icon>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 主要内容区域 -->
    <el-tabs v-model="activeTab" class="management-tabs">
      <!-- 赔率监控 -->
      <el-tab-pane label="赔率监控" name="monitoring">
        <div class="tab-content">
          <el-card class="monitoring-card">
            <template #header>
              <div class="card-header">
                <span>实时赔率监控</span>
                <div class="header-actions">
                  <el-button size="small" @click="refreshMonitoring">刷新</el-button>
                  <el-button size="small" type="primary" @click="setupAlerts">设置提醒</el-button>
                </div>
              </div>
            </template>

            <div class="monitoring-filters">
              <el-form :model="monitoringFilters" :inline="true">
                <el-form-item label="联赛">
                  <el-select v-model="monitoringFilters.league" placeholder="选择联赛" clearable>
                    <el-option label="英超" value="premier_league" />
                    <el-option label="西甲" value="la_liga" />
                    <el-option label="意甲" value="serie_a" />
                    <el-option label="德甲" value="bundesliga" />
                    <el-option label="法甲" value="ligue_1" />
                  </el-select>
                </el-form-item>
                <el-form-item label="比赛时间">
                  <el-date-picker
                    v-model="monitoringFilters.dateRange"
                    type="daterange"
                    range-separator="至"
                    start-placeholder="开始日期"
                    end-placeholder="结束日期"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="applyMonitoringFilters">筛选</el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table :data="monitoringData" style="width: 100%" v-loading="monitoringLoading">
              <el-table-column prop="matchId" label="比赛ID" width="120" />
              <el-table-column label="对阵" min-width="200">
                <template #default="scope">
                  <div class="match-teams">
                    <span class="home-team">{{ scope.row.homeTeam }}</span>
                    <span class="vs">VS</span>
                    <span class="away-team">{{ scope.row.awayTeam }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="league" label="联赛" width="120" />
              <el-table-column label="赔率" min-width="200">
                <template #default="scope">
                  <div class="odds-display">
                    <div class="odds-item">
                      <span class="odds-label">胜</span>
                      <span class="odds-value" :class="{ 'changed': scope.row.oddsChanged.win }">{{ scope.row.odds.win }}</span>
                    </div>
                    <div class="odds-item">
                      <span class="odds-label">平</span>
                      <span class="odds-value" :class="{ 'changed': scope.row.oddsChanged.draw }">{{ scope.row.odds.draw }}</span>
                    </div>
                    <div class="odds-item">
                      <span class="odds-label">负</span>
                      <span class="odds-value" :class="{ 'changed': scope.row.oddsChanged.lose }">{{ scope.row.odds.lose }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="lastUpdate" label="最后更新" width="160" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="viewOddsHistory(scope.row)">历史</el-button>
                  <el-button size="small" type="primary" @click="setAlert(scope.row)">提醒</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="monitoringPagination.currentPage"
                v-model:page-size="monitoringPagination.pageSize"
                :total="monitoringPagination.total"
                layout="total, prev, pager, next, jumper"
                @current-change="handleMonitoringPageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 历史对比 -->
      <el-tab-pane label="历史对比" name="history">
        <div class="tab-content">
          <el-card class="history-card">
            <template #header>
              <div class="card-header">
                <span>赔率历史对比分析</span>
                <div class="header-actions">
                  <el-button size="small" @click="compareMultiple">多场比赛对比</el-button>
                  <el-button size="small" type="primary" @click="generateReport">生成报告</el-button>
                </div>
              </div>
            </template>

            <div class="history-filters">
              <el-form :model="historyFilters" :inline="true">
                <el-form-item label="比赛">
                  <el-input v-model="historyFilters.matchId" placeholder="输入比赛ID" style="width: 200px" />
                </el-form-item>
                <el-form-item label="时间范围">
                  <el-date-picker
                    v-model="historyFilters.timeRange"
                    type="datetimerange"
                    range-separator="至"
                    start-placeholder="开始时间"
                    end-placeholder="结束时间"
                  />
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="loadHistoryData">查询</el-button>
                </el-form-item>
              </el-form>
            </div>

            <div class="chart-container">
              <div ref="oddsChartRef" style="height: 400px;"></div>
            </div>

            <el-table :data="historyData" style="width: 100%" v-loading="historyLoading">
              <el-table-column prop="timestamp" label="时间" width="160" />
              <el-table-column prop="winOdds" label="胜赔率" width="100" />
              <el-table-column prop="drawOdds" label="平赔率" width="100" />
              <el-table-column prop="loseOdds" label="负赔率" width="100" />
              <el-table-column prop="change" label="变化" width="100">
                <template #default="scope">
                  <span :class="scope.row.change > 0 ? 'positive-change' : scope.row.change < 0 ? 'negative-change' : ''">
                    {{ scope.row.change > 0 ? '+' : '' }}{{ scope.row.change }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="totalStakes" label="总投注额" width="120" />
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- 异常检测 -->
      <el-tab-pane label="异常检测" name="anomaly">
        <div class="tab-content">
          <el-card class="anomaly-card">
            <template #header>
              <div class="card-header">
                <span>异常赔率检测</span>
                <div class="header-actions">
                  <el-button size="small" @click="runFullScan">全量扫描</el-button>
                  <el-button size="small" type="primary" @click="configureDetection">配置检测规则</el-button>
                </div>
              </div>
            </template>

            <div class="anomaly-filters">
              <el-form :model="anomalyFilters" :inline="true">
                <el-form-item label="检测类型">
                  <el-select v-model="anomalyFilters.type" placeholder="选择类型" clearable>
                    <el-option label="急剧变化" value="sharp_change" />
                    <el-option label="偏离市场" value="market_deviation" />
                    <el-option label="异常波动" value="abnormal_fluctuation" />
                    <el-option label="数据缺失" value="data_missing" />
                  </el-select>
                </el-form-item>
                <el-form-item label="严重程度">
                  <el-select v-model="anomalyFilters.severity" placeholder="选择等级" clearable>
                    <el-option label="高" value="high" />
                    <el-option label="中" value="medium" />
                    <el-option label="低" value="low" />
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <el-button type="primary" @click="filterAnomalies">筛选</el-button>
                </el-form-item>
              </el-form>
            </div>

            <el-table :data="anomalyData" style="width: 100%" v-loading="anomalyLoading">
              <el-table-column prop="id" label="ID" width="80" />
              <el-table-column prop="matchId" label="比赛ID" width="120" />
              <el-table-column label="对阵" min-width="180">
                <template #default="scope">
                  <div class="match-teams">
                    <span class="home-team">{{ scope.row.homeTeam }}</span>
                    <span class="vs">VS</span>
                    <span class="away-team">{{ scope.row.awayTeam }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="120" />
              <el-table-column prop="severity" label="严重程度" width="100">
                <template #default="scope">
                  <el-tag :type="getSeverityTagType(scope.row.severity)">{{ scope.row.severityText }}</el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="description" label="描述" min-width="200" />
              <el-table-column prop="detectedTime" label="检测时间" width="160" />
              <el-table-column label="操作" width="150">
                <template #default="scope">
                  <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
                  <el-button size="small" type="warning" @click="markAsHandled(scope.row)">标记处理</el-button>
                </template>
              </el-table-column>
            </el-table>
            
            <div class="pagination-wrapper">
              <el-pagination
                v-model:current-page="anomalyPagination.currentPage"
                v-model:page-size="anomalyPagination.pageSize"
                :total="anomalyPagination.total"
                layout="total, prev, pager, next, jumper"
                @current-change="handleAnomalyPageChange"
              />
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 查看历史对话框 -->
    <el-dialog 
      v-model="showHistoryDialog" 
      title="赔率历史记录" 
      width="80%"
      :before-close="closeHistoryDialog"
    >
      <div v-if="selectedMatch" class="history-dialog-content">
        <h4>{{ selectedMatch.homeTeam }} VS {{ selectedMatch.awayTeam }}</h4>
        <div ref="matchOddsChartRef" style="height: 300px;"></div>
        <el-table :data="matchHistoryData" style="width: 100%" v-loading="matchHistoryLoading">
          <el-table-column prop="timestamp" label="时间" width="160" />
          <el-table-column prop="winOdds" label="胜赔率" width="100" />
          <el-table-column prop="drawOdds" label="平赔率" width="100" />
          <el-table-column prop="loseOdds" label="负赔率" width="100" />
          <el-table-column prop="change" label="变化" width="100">
            <template #default="scope">
              <span :class="scope.row.change > 0 ? 'positive-change' : scope.row.change < 0 ? 'negative-change' : ''">
                {{ scope.row.change > 0 ? '+' : '' }}{{ scope.row.change }}
              </span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'
import { 
  VideoPlay, 
  Histogram, 
  Warning, 
  Download, 
  Document, 
  Monitor, 
  TrendCharts 
} from '@element-plus/icons-vue'

// 激活的标签页
const activeTab = ref('monitoring')

// 统计数据
const stats = reactive({
  totalOdds: 0,
  monitoredMatches: 0,
  anomaliesDetected: 0,
  changesToday: 0
})

// 监控相关数据
const monitoringData = ref([])
const monitoringLoading = ref(false)
const monitoringFilters = reactive({
  league: '',
  dateRange: null
})
const monitoringPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 100
})

// 历史对比相关数据
const historyData = ref([])
const historyLoading = ref(false)
const historyFilters = reactive({
  matchId: '',
  timeRange: null
})
const oddsChartRef = ref(null)

// 异常检测相关数据
const anomalyData = ref([])
const anomalyLoading = ref(false)
const anomalyFilters = reactive({
  type: '',
  severity: ''
})
const anomalyPagination = reactive({
  currentPage: 1,
  pageSize: 10,
  total: 50
})

// 历史对话框相关
const showHistoryDialog = ref(false)
const selectedMatch = ref(null)
const matchHistoryData = ref([])
const matchHistoryLoading = ref(false)
const matchOddsChartRef = ref(null)

// 方法
const startMonitoring = () => {
  ElMessage.success('开始监控赔率变化')
}

const analyzeTrends = () => {
  ElMessage.success('开始分析赔率趋势')
}

const detectAnomalies = () => {
  ElMessage.success('开始检测异常赔率')
}

const exportData = () => {
  ElMessage.success('开始导出数据')
}

const refreshMonitoring = async () => {
  monitoringLoading.value = true
  try {
    const response = await request.get('/api/v1/admin/odds/monitoring', {
      params: {
        page: monitoringPagination.currentPage,
        size: monitoringPagination.pageSize
      }
    })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []
    const total = payload?.data?.total ?? payload?.total ?? list.length

    if (success) {
      monitoringData.value = Array.isArray(list) ? list : []
      monitoringPagination.total = Number(total) || 0
    } else {
      ElMessage.error(payload?.message || '获取监控数据失败')
    }
  } catch (error) {
    console.error('获取监控数据失败:', error)
    ElMessage.error('获取监控数据失败')
  } finally {
    monitoringLoading.value = false
  }
}

const setupAlerts = () => {
  ElMessage.info('进入设置提醒页面')
}

const applyMonitoringFilters = async () => {
  monitoringLoading.value = true
  try {
    const params = {
      page: monitoringPagination.currentPage,
      size: monitoringPagination.pageSize
    }
    
    if (monitoringFilters.league) {
      params.league = monitoringFilters.league
    }
    
    if (monitoringFilters.dateRange && monitoringFilters.dateRange.length === 2) {
      params.date_from = monitoringFilters.dateRange[0]
      params.date_to = monitoringFilters.dateRange[1]
    }
    
    const response = await request.get('/api/v1/admin/odds/monitoring', { params })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []
    const total = payload?.data?.total ?? payload?.total ?? list.length

    if (success) {
      monitoringData.value = Array.isArray(list) ? list : []
      monitoringPagination.total = Number(total) || 0
    } else {
      ElMessage.error(payload?.message || '筛选监控数据失败')
    }
  } catch (error) {
    console.error('筛选监控数据失败:', error)
    ElMessage.error('筛选监控数据失败')
  } finally {
    monitoringLoading.value = false
  }
}

const handleMonitoringPageChange = async (page) => {
  monitoringPagination.currentPage = page
  await refreshMonitoring()
}

const loadHistoryData = async () => {
  historyLoading.value = true
  try {
    const params = {}
    
    if (historyFilters.matchId) {
      params.match_id = historyFilters.matchId
    }
    
    if (historyFilters.timeRange && historyFilters.timeRange.length === 2) {
      params.time_from = historyFilters.timeRange[0]
      params.time_to = historyFilters.timeRange[1]
    }
    
    const response = await request.get('/api/v1/admin/odds/history', { params })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []

    if (success) {
      historyData.value = Array.isArray(list) ? list : []
    } else {
      ElMessage.error(payload?.message || '获取历史数据失败')
    }
  } catch (error) {
    console.error('获取历史数据失败:', error)
    ElMessage.error('获取历史数据失败')
  } finally {
    historyLoading.value = false
  }
}

const compareMultiple = () => {
  ElMessage.info('进入多场比赛对比')
}

const generateReport = () => {
  ElMessage.info('生成分析报告')
}

const runFullScan = async () => {
  try {
    const response = await request.get('/api/v1/admin/odds/anomalies', {
      params: {
        page: anomalyPagination.currentPage,
        size: anomalyPagination.pageSize
      }
    })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []
    const total = payload?.data?.total ?? payload?.total ?? list.length

    if (success) {
      anomalyData.value = Array.isArray(list) ? list : []
      anomalyPagination.total = Number(total) || 0
      ElMessage.success('全量扫描完成')
    } else {
      ElMessage.error(payload?.message || '全量扫描失败')
    }
  } catch (error) {
    console.error('全量扫描失败:', error)
    ElMessage.error('全量扫描失败')
  }
}

const configureDetection = () => {
  ElMessage.info('配置检测规则')
}

const filterAnomalies = async () => {
  anomalyLoading.value = true
  try {
    const params = {
      page: anomalyPagination.currentPage,
      size: anomalyPagination.pageSize
    }
    
    if (anomalyFilters.type) {
      params.anomaly_type = anomalyFilters.type
    }
    
    if (anomalyFilters.severity) {
      params.severity = anomalyFilters.severity
    }
    
    const response = await request.get('/api/v1/admin/odds/anomalies', { params })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []
    const total = payload?.data?.total ?? payload?.total ?? list.length

    if (success) {
      anomalyData.value = Array.isArray(list) ? list : []
      anomalyPagination.total = Number(total) || 0
    } else {
      ElMessage.error(payload?.message || '筛选异常数据失败')
    }
  } catch (error) {
    console.error('筛选异常数据失败:', error)
    ElMessage.error('筛选异常数据失败')
  } finally {
    anomalyLoading.value = false
  }
}

const handleAnomalyPageChange = async (page) => {
  anomalyPagination.currentPage = page
  await filterAnomalies()
}

const getSeverityTagType = (severity) => {
  switch(severity) {
    case 'high': return 'danger'
    case 'medium': return 'warning'
    case 'low': return 'info'
    default: return 'info'
  }
}

const viewDetails = (row) => {
  ElMessage.info(`查看异常详情: ${row.id}`)
}

const markAsHandled = (row) => {
  ElMessage.success(`标记异常已处理: ${row.id}`)
}

const viewOddsHistory = async (match) => {
  selectedMatch.value = match
  showHistoryDialog.value = true
  
  matchHistoryLoading.value = true
  try {
    const response = await request.get('/api/v1/admin/odds/history', {
      params: {
        match_id: parseInt(match.matchId.replace('M', ''))
      }
    })

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const list = payload?.data?.items ?? payload?.items ?? payload?.data ?? []

    if (success) {
      matchHistoryData.value = Array.isArray(list) ? list : []
    } else {
      ElMessage.error(payload?.message || '获取比赛历史数据失败')
    }
  } catch (error) {
    console.error('获取比赛历史数据失败:', error)
    ElMessage.error('获取比赛历史数据失败')
  } finally {
    matchHistoryLoading.value = false
  }
}

const closeHistoryDialog = () => {
  showHistoryDialog.value = false
  selectedMatch.value = null
}

// 加载统计数据
const loadStats = async () => {
  try {
    const response = await request.get('/api/v1/admin/odds/stats')

    const payload = response?.data ?? response
    const success = payload?.success ?? true
    const data = payload?.data ?? payload ?? {}

    if (success) {
      Object.assign(stats, data)
    } else {
      ElMessage.error(payload?.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

// 初始化数据
onMounted(async () => {
  await loadStats()
  await refreshMonitoring()
  await filterAnomalies()
})
</script>

<style scoped>
.odds-management-container {
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
  color: #909399;
  font-size: 14px;
  margin: 0;
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
  float: left;
}

.stats-number {
  font-size: 24px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 4px;
}

.stats-label {
  font-size: 14px;
  color: #909399;
}

.stats-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 32px;
  color: #409EFF;
  opacity: 0.3;
}

.management-tabs {
  background: white;
  padding: 0;
  border-radius: 4px;
}

.tab-content {
  padding: 20px 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.match-teams {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.home-team {
  color: #67C23A;
  font-weight: 500;
}

.away-team {
  color: #F56C6C;
  font-weight: 500;
}

.vs {
  color: #909399;
}

.odds-display {
  display: flex;
  justify-content: space-around;
}

.odds-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.odds-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 2px;
}

.odds-value {
  font-weight: 600;
  color: #303133;
}

.odds-value.changed {
  color: #E6A23C;
  font-weight: 700;
}

.positive-change {
  color: #67C23A;
}

.negative-change {
  color: #F56C6C;
}

.chart-container {
  margin: 20px 0;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  padding: 10px;
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.history-dialog-content h4 {
  margin: 0 0 20px 0;
  text-align: center;
  color: #303133;
}
</style>
