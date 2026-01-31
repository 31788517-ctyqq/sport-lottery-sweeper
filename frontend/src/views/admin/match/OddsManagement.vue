<template>
  <div class="odds-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>赔率管理</h2>
      <p>实时监控赔率变化、分析历史趋势、检测异常赔率</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="总赔率记录"
              :value="oddsStats.totalRecords"
              :precision="0"
            >
              <template #prefix>
                <el-icon><TrendCharts /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="今日更新"
              :value="oddsStats.todayUpdates"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><Calendar /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="异常赔率"
              :value="oddsStats.anomalyCount"
              :precision="0"
              style="color: #f56c6c"
            >
              <template #prefix>
                <el-icon><Warning /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="监控比赛"
              :value="oddsStats.monitoredMatches"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><Monitor /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="变化幅度>5%"
              :value="oddsStats.bigChanges"
              :precision="0"
              style="color: #e6a23c"
            >
              <template #prefix>
                <el-icon><Histogram /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="数据源数量"
              :value="oddsStats.dataSourceCount"
              :precision="0"
              style="color: #909399"
            >
              <template #prefix>
                <el-icon><Connection /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="refreshData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
      <el-button type="success" @click="addOddsRecord">
        <el-icon><Plus /></el-icon>
        添加赔率
      </el-button>
      <el-button type="warning" @click="detectAnomalies">
        <el-icon><WarningFilled /></el-icon>
        异常检测
      </el-button>
      <el-button type="info" @click="showTrendAnalysis">
        <el-icon><DataLine /></el-icon>
        趋势分析
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="联赛筛选">
            <el-select 
              v-model="filters.leagueId" 
              placeholder="选择联赛" 
              clearable 
              @change="applyFilters"
              style="width: 150px"
            >
              <el-option
                v-for="league in leagues"
                :key="league.id"
                :label="league.name"
                :value="league.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="比赛筛选">
            <el-select 
              v-model="filters.matchId" 
              placeholder="选择比赛" 
              clearable 
              @change="applyFilters"
              style="width: 200px"
            >
              <el-option
                v-for="match in filteredMatches"
                :key="match.id"
                :label="`${match.home_team} VS ${match.away_team}`"
                :value="match.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="数据源">
            <el-select 
              v-model="filters.dataSource" 
              placeholder="选择数据源" 
              clearable 
              @change="applyFilters"
              style="width: 120px"
            >
              <el-option label="竞彩" value="jc" />
              <el-option label="Bet365" value="bet365" />
              <el-option label="威廉希尔" value="williamhill" />
              <el-option label="其他" value="other" />
            </el-select>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="filters.dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 赔率数据表格 -->
    <div class="table-section">
      <el-table
        :data="filteredOdds"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        height="500"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="match_info" label="比赛" min-width="180">
          <template #default="scope">
            <div>
              <div>{{ scope.row.home_team }} VS {{ scope.row.away_team }}</div>
              <div class="text-muted">{{ scope.row.league_name }} | {{ scope.row.match_date }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="赔率" width="200">
          <template #default="scope">
            <div class="odds-display">
              <div class="odd-item">
                <span class="label">胜:</span>
                <span class="value">{{ scope.row.odds_home }}</span>
              </div>
              <div class="odd-item">
                <span class="label">平:</span>
                <span class="value">{{ scope.row.odds_draw }}</span>
              </div>
              <div class="odd-item">
                <span class="label">负:</span>
                <span class="value">{{ scope.row.odds_away }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="概率" width="200">
          <template #default="scope">
            <div class="probability-display">
              <div class="prob-item">
                <span class="label">胜:</span>
                <el-progress 
                  :percentage="scope.row.probability_home" 
                  :stroke-width="12" 
                  :format="() => ''" 
                  class="progress"
                />
                <span class="percent">{{ scope.row.probability_home }}%</span>
              </div>
              <div class="prob-item">
                <span class="label">平:</span>
                <el-progress 
                  :percentage="scope.row.probability_draw" 
                  :stroke-width="12" 
                  :format="() => ''" 
                  class="progress"
                />
                <span class="percent">{{ scope.row.probability_draw }}%</span>
              </div>
              <div class="prob-item">
                <span class="label">负:</span>
                <el-progress 
                  :percentage="scope.row.probability_away" 
                  :stroke-width="12" 
                  :format="() => ''" 
                  class="progress"
                />
                <span class="percent">{{ scope.row.probability_away }}%</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="update_time" label="更新时间" width="150">
          <template #default="scope">
            {{ formatDateTime(scope.row.update_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="source" label="数据源" width="120" />
        <el-table-column label="变化" width="120">
          <template #default="scope">
            <el-tag 
              :type="getChangeType(scope.row.change_percentage)" 
              size="small"
            >
              {{ scope.row.change_percentage }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="viewTrend(scope.row)">趋势</el-button>
              <el-button size="small" type="primary" @click="editOdds(scope.row)">编辑</el-button>
              <el-button size="small" type="warning" @click="markAsAnomaly(scope.row)">异常</el-button>
              <el-button size="small" type="danger" @click="deleteOdds(scope.row)">删除</el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 分页区域 -->
    <div class="pagination-wrapper">
      <el-pagination
        v-model:current-page="pagination.currentPage"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>

    <!-- 赔率趋势图表对话框 -->
    <el-dialog
      v-model="showTrendDialog"
      title="赔率趋势分析"
      width="90%"
      top="5vh"
    >
      <div class="trend-chart-container">
        <el-card>
          <template #header>
            <div class="trend-header">
              <span>{{ trendMatchInfo }}</span>
              <el-button type="primary" @click="generateTrendReport">生成报告</el-button>
            </div>
          </template>
          <div id="trend-chart" style="height: 400px;"></div>
        </el-card>
      </div>
      <template #footer>
        <el-button @click="showTrendDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 异常检测结果对话框 -->
    <el-dialog
      v-model="showAnomalyDialog"
      title="异常赔率检测结果"
      width="800px"
    >
      <el-table :data="anomalyResults" v-loading="anomalyLoading">
        <el-table-column prop="match_info" label="比赛" width="200" />
        <el-table-column prop="odds_info" label="赔率" width="150" />
        <el-table-column prop="anomaly_type" label="异常类型" width="120">
          <template #default="scope">
            <el-tag :type="getAnomalyTypeTag(scope.row.anomaly_type)">
              {{ scope.row.anomaly_type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="confidence" label="可信度" width="100">
          <template #default="scope">
            {{ scope.row.confidence }}%
          </template>
        </el-table-column>
        <el-table-column prop="details" label="详情" />
      </el-table>
      <template #footer>
        <el-button @click="showAnomalyDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Refresh, 
  Plus, 
  WarningFilled, 
  DataLine, 
  TrendCharts, 
  Calendar, 
  Warning, 
  Monitor, 
  Histogram, 
  Connection 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const showTrendDialog = ref(false)
const showAnomalyDialog = ref(false)
const anomalyLoading = ref(false)

// 赔率数据
const oddsData = ref([])
const matches = ref([])
const leagues = ref([])

// 统计数据
const oddsStats = reactive({
  totalRecords: 0,
  todayUpdates: 0,
  anomalyCount: 0,
  monitoredMatches: 0,
  bigChanges: 0,
  dataSourceCount: 0
})

// 过滤器
const filters = reactive({
  leagueId: '',
  matchId: '',
  dataSource: '',
  dateRange: []
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 趋势相关
const trendMatchInfo = ref('')
const anomalyResults = ref([])

// 计算属性
const filteredMatches = computed(() => {
  let result = matches.value
  
  if (filters.leagueId) {
    result = result.filter(match => match.league_id === filters.leagueId)
  }
  
  return result
})

const filteredOdds = computed(() => {
  let result = oddsData.value
  
  // 联赛筛选
  if (filters.leagueId) {
    result = result.filter(odds => odds.league_id === filters.leagueId)
  }
  
  // 比赛筛选
  if (filters.matchId) {
    result = result.filter(odds => odds.match_id === filters.matchId)
  }
  
  // 数据源筛选
  if (filters.dataSource) {
    result = result.filter(odds => odds.source === filters.dataSource)
  }
  
  // 时间范围筛选
  if (filters.dateRange && filters.dateRange.length === 2) {
    const [startDate, endDate] = filters.dateRange
    result = result.filter(odds => {
      const updateTime = new Date(odds.update_time)
      return updateTime >= new Date(startDate) && updateTime <= new Date(endDate + ' 23:59:59')
    })
  }
  
  // 分页处理
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return result.slice(start, end)
})

// 方法
const loadOddsData = async () => {
  loading.value = true
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // 模拟赔率数据
    oddsData.value = [
      {
        id: 1,
        match_id: 1,
        home_team: '曼城',
        away_team: '利物浦',
        league_name: '英超',
        league_id: 1,
        odds_home: 2.1,
        odds_draw: 3.2,
        odds_away: 3.4,
        probability_home: 42,
        probability_draw: 28,
        probability_away: 25,
        change_percentage: 2.5,
        update_time: '2026-01-30 12:30:00',
        source: '竞彩'
      },
      {
        id: 2,
        match_id: 1,
        home_team: '曼城',
        away_team: '利物浦',
        league_name: '英超',
        league_id: 1,
        odds_home: 2.0,
        odds_draw: 3.3,
        odds_away: 3.5,
        probability_home: 44,
        probability_draw: 27,
        probability_away: 24,
        change_percentage: -4.8,
        update_time: '2026-01-30 10:15:00',
        source: 'Bet365'
      },
      {
        id: 3,
        match_id: 2,
        home_team: '阿森纳',
        away_team: '切尔西',
        league_name: '英超',
        league_id: 1,
        odds_home: 1.8,
        odds_draw: 3.4,
        odds_away: 4.2,
        probability_home: 48,
        probability_draw: 26,
        probability_away: 20,
        change_percentage: 1.2,
        update_time: '2026-01-30 09:45:00',
        source: '威廉希尔'
      },
      {
        id: 4,
        match_id: 3,
        home_team: '皇马',
        away_team: '巴萨',
        league_name: '西甲',
        league_id: 2,
        odds_home: 2.5,
        odds_draw: 3.1,
        odds_away: 2.8,
        probability_home: 38,
        probability_draw: 30,
        probability_away: 28,
        change_percentage: 5.6,
        update_time: '2026-01-29 22:30:00',
        source: '竞彩'
      },
      {
        id: 5,
        match_id: 4,
        home_team: '拜仁',
        away_team: '多特',
        league_name: '德甲',
        league_id: 3,
        odds_home: 1.6,
        odds_draw: 3.8,
        odds_away: 5.0,
        probability_home: 55,
        probability_draw: 20,
        probability_away: 18,
        change_percentage: -2.1,
        update_time: '2026-01-29 21:00:00',
        source: 'Bet365'
      }
    ]
    
    pagination.total = oddsData.value.length
    
    // 更新统计数据
    oddsStats.totalRecords = oddsData.value.length
    oddsStats.todayUpdates = oddsData.value.filter(o => o.update_time.includes('2026-01-30')).length
    oddsStats.anomalyCount = oddsData.value.filter(o => Math.abs(o.change_percentage) > 5).length
    oddsStats.monitoredMatches = [...new Set(oddsData.value.map(o => o.match_id))].length
    oddsStats.bigChanges = oddsData.value.filter(o => Math.abs(o.change_percentage) > 5).length
    oddsStats.dataSourceCount = [...new Set(oddsData.value.map(o => o.source))].length
  } catch (error) {
    console.error('获取赔率数据失败:', error)
    ElMessage.error('获取赔率数据失败')
  } finally {
    loading.value = false
  }
}

const loadMatches = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    matches.value = [
      { id: 1, league_id: 1, home_team: '曼城', away_team: '利物浦', league_name: '英超', match_date: '2026-01-30' },
      { id: 2, league_id: 1, home_team: '阿森纳', away_team: '切尔西', league_name: '英超', match_date: '2026-01-30' },
      { id: 3, league_id: 2, home_team: '皇马', away_team: '巴萨', league_name: '西甲', match_date: '2026-01-29' },
      { id: 4, league_id: 3, home_team: '拜仁', away_team: '多特', league_name: '德甲', match_date: '2026-01-29' },
      { id: 5, league_id: 4, home_team: '尤文', away_team: '国米', league_name: '意甲', match_date: '2026-01-31' }
    ]
  } catch (error) {
    console.error('获取比赛数据失败:', error)
  }
}

const loadLeagues = async () => {
  try {
    // 模拟API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    leagues.value = [
      { id: 1, name: '英超', country: '英格兰' },
      { id: 2, name: '西甲', country: '西班牙' },
      { id: 3, name: '德甲', country: '德国' },
      { id: 4, name: '意甲', country: '意大利' },
      { id: 5, name: '法甲', country: '法国' },
      { id: 6, name: '中超', country: '中国' }
    ]
  } catch (error) {
    console.error('获取联赛数据失败:', error)
  }
}

const refreshData = () => {
  loadOddsData()
  ElMessage.success('数据已刷新')
}

const addOddsRecord = () => {
  ElMessage.info('添加赔率功能开发中...')
}

const detectAnomalies = async () => {
  anomalyLoading.value = true
  showAnomalyDialog.value = true
  
  try {
    // 模拟异常检测
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    anomalyResults.value = [
      {
        match_info: '曼城 VS 利物浦',
        odds_info: '胜:2.1 平:3.2 负:3.4',
        anomaly_type: '大幅波动',
        confidence: 92,
        details: '短时间内胜率赔率下降0.3，可能存在异常'
      },
      {
        match_info: '皇马 VS 巴萨',
        odds_info: '胜:2.5 平:3.1 负:2.8',
        anomaly_type: '偏离均值',
        confidence: 87,
        details: '平局赔率显著高于其他数据源平均值'
      },
      {
        match_info: '拜仁 VS 多特',
        odds_info: '胜:1.6 平:3.8 负:5.0',
        anomaly_type: '逻辑异常',
        confidence: 95,
        details: '主胜赔率过低，与其他因素不符'
      }
    ]
  } catch (error) {
    console.error('异常检测失败:', error)
  } finally {
    anomalyLoading.value = false
  }
}

const showTrendAnalysis = () => {
  ElMessage.info('趋势分析功能开发中...')
}

const viewTrend = (row) => {
  trendMatchInfo.value = `${row.home_team} VS ${row.away_team} (${row.league_name})`
  showTrendDialog.value = true
  // 这里应该集成图表库来展示赔率趋势
}

const editOdds = (row) => {
  ElMessage.info(`编辑赔率: ${row.home_team} VS ${row.away_team}`)
}

const markAsAnomaly = (row) => {
  ElMessage.warning(`标记为异常: ${row.home_team} VS ${row.away_team}`)
}

const deleteOdds = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除赔率记录 "${row.home_team} VS ${row.away_team}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 模拟删除
    const index = oddsData.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      oddsData.value.splice(index, 1)
      pagination.total--
      ElMessage.success('删除成功')
      loadOddsData() // 重新加载统计数据
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const applyFilters = () => {
  // 分页重置到第一页
  pagination.currentPage = 1
  // 在computed中已处理过滤逻辑
}

const resetFilters = () => {
  filters.leagueId = ''
  filters.matchId = ''
  filters.dataSource = ''
  filters.dateRange = []
  pagination.currentPage = 1
  // 过滤器改变会自动触发computed
}

const getChangeType = (change) => {
  if (Math.abs(change) > 5) return 'danger'
  if (Math.abs(change) > 2) return 'warning'
  return 'success'
}

const getAnomalyTypeTag = (type) => {
  const typeMap = {
    '大幅波动': 'danger',
    '偏离均值': 'warning',
    '逻辑异常': 'info'
  }
  return typeMap[type] || 'info'
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}

const generateTrendReport = () => {
  ElMessage.success('趋势报告生成中...')
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadOddsData()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  // 过滤后的数据已自动更新
}

// 生命周期
onMounted(() => {
  loadOddsData()
  loadMatches()
  loadLeagues()
})
</script>

<style scoped>
.odds-management {
  padding: 20px;
  background-color: var(--bg-body, #f5f7fa);
}

.page-header {
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: var(--text-primary, #303133);
  font-size: 24px;
  font-weight: 600;
}

.page-header p {
  margin: 0;
  color: var(--text-secondary, #909399);
  font-size: 14px;
}

.stats-section {
  margin-bottom: 24px;
}

.stat-card {
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.operation-bar {
  margin-bottom: 24px;
}

.operation-bar .el-button {
  margin-right: 12px;
  margin-bottom: 8px;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-section :deep(.el-card) {
  border-radius: 8px;
}

.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.odds-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.odd-item {
  display: flex;
  justify-content: space-between;
}

.odd-item .label {
  font-weight: bold;
  color: #909399;
  margin-right: 8px;
}

.odd-item .value {
  font-weight: bold;
  color: #303133;
}

.probability-display {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.prob-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.prob-item .label {
  font-weight: bold;
  color: #909399;
  width: 20px;
}

.prob-item .progress {
  flex: 1;
}

.prob-item .percent {
  width: 40px;
  text-align: right;
  font-size: 12px;
}

.text-muted {
  color: #909399;
  font-size: 12px;
}

.action-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: nowrap;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

.trend-chart-container {
  height: 500px;
}

.trend-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

:deep(.el-progress__text) {
  font-size: 12px;
}
</style>