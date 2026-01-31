<template>
  <div class="match-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>比赛管理</h2>
      <p>管理比赛、联赛、球队数据，进行数据验证和关联数据展示</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="总比赛数"
              :value="matchStats.totalMatches"
              :precision="0"
            >
              <template #prefix>
                <el-icon><Football /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="今日比赛"
              :value="matchStats.todayMatches"
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
              title="进行中比赛"
              :value="matchStats.liveMatches"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="已完成比赛"
              :value="matchStats.finishedMatches"
              :precision="0"
              style="color: #e6a23c"
            >
              <template #prefix>
                <el-icon><Finished /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="异常数据"
              :value="matchStats.anomalyCount"
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
              title="联赛数"
              :value="matchStats.totalLeagues"
              :precision="0"
              style="color: #909399"
            >
              <template #prefix>
                <el-icon><Trophy /></el-icon>
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
      <el-button type="success" @click="showAddMatchDialog = true">
        <el-icon><Plus /></el-icon>
        添加比赛
      </el-button>
      <el-button type="warning" @click="validateData">
        <el-icon><CircleCheck /></el-icon>
        数据验证
      </el-button>
      <el-button type="danger" @click="detectAnomalies">
        <el-icon><WarningFilled /></el-icon>
        异常检测
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
          <el-form-item label="比赛状态">
            <el-select 
              v-model="filters.status" 
              placeholder="选择状态" 
              clearable 
              @change="applyFilters"
              style="width: 120px"
            >
              <el-option label="未开始" value="upcoming" />
              <el-option label="进行中" value="live" />
              <el-option label="已结束" value="finished" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
          </el-form-item>
          <el-form-item label="搜索">
            <el-input
              v-model="filters.searchKeyword"
              placeholder="搜索主队或客队"
              clearable
              style="width: 200px"
              @clear="applyFilters"
              @keyup.enter="applyFilters"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <!-- 比赛数据表格 -->
    <div class="table-section">
      <el-table
        :data="filteredMatches"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        height="500"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="league_name" label="联赛" width="120" />
        <el-table-column prop="match_date" label="比赛日期" width="120">
          <template #default="scope">
            {{ formatDate(scope.row.match_date) }}
          </template>
        </el-table-column>
        <el-table-column prop="match_time" label="比赛时间" width="120" />
        <el-table-column label="对阵" min-width="200">
          <template #default="scope">
            <div class="match-teams">
              <span class="home-team">{{ scope.row.home_team }}</span>
              <span class="vs">VS</span>
              <span class="away-team">{{ scope.row.away_team }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="score" label="比分" width="100">
          <template #default="scope">
            {{ scope.row.score || '-' }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="数据质量" width="120">
          <template #default="scope">
            <el-tag 
              :type="getDataQualityType(scope.row.data_quality)" 
              size="small"
            >
              {{ getDataQualityText(scope.row.data_quality) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="viewMatch(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="editMatch(scope.row)">编辑</el-button>
              <el-button size="small" type="warning" @click="viewOdds(scope.row)">赔率</el-button>
              <el-button size="small" type="danger" @click="deleteMatch(scope.row)">删除</el-button>
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

    <!-- 添加/编辑比赛对话框 -->
    <el-dialog
      v-model="showAddMatchDialog"
      :title="editingMatch ? '编辑比赛' : '添加比赛'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="currentMatch" label-width="100px">
        <el-form-item label="联赛">
          <el-select v-model="currentMatch.league_id" placeholder="请选择联赛">
            <el-option
              v-for="league in leagues"
              :key="league.id"
              :label="league.name"
              :value="league.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="主队">
          <el-input v-model="currentMatch.home_team" placeholder="请输入主队名称" />
        </el-form-item>
        <el-form-item label="客队">
          <el-input v-model="currentMatch.away_team" placeholder="请输入客队名称" />
        </el-form-item>
        <el-form-item label="比赛日期">
          <el-date-picker
            v-model="currentMatch.match_date"
            type="date"
            placeholder="选择日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="比赛时间">
          <el-time-picker
            v-model="currentMatch.match_time"
            placeholder="选择时间"
            format="HH:mm"
          />
        </el-form-item>
        <el-form-item label="比赛状态">
          <el-select v-model="currentMatch.status" placeholder="请选择状态">
            <el-option label="未开始" value="upcoming" />
            <el-option label="进行中" value="live" />
            <el-option label="已结束" value="finished" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddMatchDialog = false">取消</el-button>
          <el-button type="primary" @click="saveMatch">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 数据验证结果对话框 -->
    <el-dialog
      v-model="showValidationDialog"
      title="数据验证结果"
      width="800px"
    >
      <el-table :data="validationResults" v-loading="validationLoading">
        <el-table-column prop="field" label="字段" width="150" />
        <el-table-column prop="problem" label="问题" width="200" />
        <el-table-column prop="severity" label="严重程度" width="120">
          <template #default="scope">
            <el-tag :type="getSeverityType(scope.row.severity)">
              {{ scope.row.severity }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="details" label="详情" />
      </el-table>
      <template #footer>
        <el-button @click="showValidationDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import axios from 'axios'
import { 
  Refresh, 
  Plus, 
  Search, 
  Football, 
  Calendar, 
  VideoPlay, 
  Finished, 
  Warning, 
  Trophy, 
  WarningFilled, 
  CircleCheck 
} from '@element-plus/icons-vue'

// 响应式数据
const loading = ref(false)
const showAddMatchDialog = ref(false)
const showValidationDialog = ref(false)
const validationLoading = ref(false)
const editingMatch = ref(false)

// 比赛数据
const matches = ref([])
const leagues = ref([])

// 当前编辑的比赛
const currentMatch = ref({
  id: null,
  league_id: '',
  home_team: '',
  away_team: '',
  match_date: '',
  match_time: '',
  status: 'upcoming',
  score: ''
})

// 统计数据
const matchStats = reactive({
  totalMatches: 0,
  todayMatches: 0,
  liveMatches: 0,
  finishedMatches: 0,
  anomalyCount: 0,
  totalLeagues: 0
})

// 过滤器
const filters = reactive({
  leagueId: '',
  status: '',
  searchKeyword: ''
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 验证结果
const validationResults = ref([])

// 计算属性 - 现在直接返回所有数据，分页由后端处理
const filteredMatches = computed(() => {
  return matches.value
})

// 方法
const loadMatches = async () => {
  loading.value = true
  try {
    const response = await axios.get('/api/admin/v1/matches', {
      params: {
        page: pagination.currentPage,
        size: pagination.pageSize
      }
    })
    
    if (response.data.success) {
      matches.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取比赛数据失败')
    }
  } catch (error) {
    console.error('获取比赛数据失败:', error)
    ElMessage.error('获取比赛数据失败')
  } finally {
    loading.value = false
  }
}

const loadLeagues = async () => {
  try {
    const response = await axios.get('/api/admin/v1/matches/leagues')
    
    if (response.data.success) {
      leagues.value = response.data.data
    } else {
      ElMessage.error(response.data.message || '获取联赛数据失败')
    }
  } catch (error) {
    console.error('获取联赛数据失败:', error)
    ElMessage.error('获取联赛数据失败')
  }
}

const loadStats = async () => {
  try {
    const response = await axios.get('/api/admin/v1/matches/stats')
    
    if (response.data.success) {
      Object.assign(matchStats, response.data.data)
    } else {
      ElMessage.error(response.data.message || '获取统计数据失败')
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    ElMessage.error('获取统计数据失败')
  }
}

const refreshData = async () => {
  await Promise.all([
    loadMatches(),
    loadStats()
  ])
  ElMessage.success('数据已刷新')
}

const viewMatch = async (match) => {
  try {
    const response = await axios.get(`/api/admin/v1/matches/${match.id}/details`)
    
    if (response.data.success) {
      ElMessage.info(`比赛详情: ${response.data.data.home_team.name} VS ${response.data.data.away_team.name}`)
    } else {
      ElMessage.error(response.data.message || '获取比赛详情失败')
    }
  } catch (error) {
    console.error('获取比赛详情失败:', error)
    ElMessage.error('获取比赛详情失败')
  }
}

const editMatch = async (match) => {
  try {
    const response = await axios.get(`/api/admin/v1/matches/${match.id}`)
    
    if (response.data.success) {
      Object.assign(currentMatch.value, response.data.data)
      editingMatch.value = true
      showAddMatchDialog.value = true
    } else {
      ElMessage.error(response.data.message || '获取比赛详情失败')
    }
  } catch (error) {
    console.error('获取比赛详情失败:', error)
    ElMessage.error('获取比赛详情失败')
  }
}

const deleteMatch = async (match) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除比赛 "${match.home_team} VS ${match.away_team}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const response = await axios.delete(`/api/admin/v1/matches/${match.id}`)
    
    if (response.data.success) {
      ElMessage.success('删除成功')
      loadMatches()
      loadStats()
    } else {
      ElMessage.error(response.data.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const saveMatch = async () => {
  try {
    let response
    if (editingMatch.value) {
      // 更新现有比赛
      response = await axios.put(`/api/admin/v1/matches/${currentMatch.value.id}`, {}, {
        params: {
          league_id: currentMatch.value.league_id,
          home_team_id: currentMatch.value.home_team_id,
          away_team_id: currentMatch.value.away_team_id,
          match_date: currentMatch.value.match_date,
          match_time: currentMatch.value.match_time,
          status: currentMatch.value.status,
          home_score: currentMatch.value.home_score,
          away_score: currentMatch.value.away_score
        }
      })
    } else {
      // 添加新比赛
      response = await axios.post('/api/admin/v1/matches', {}, {
        params: {
          league_id: currentMatch.value.league_id,
          home_team_id: currentMatch.value.home_team_id,
          away_team_id: currentMatch.value.away_team_id,
          match_date: currentMatch.value.match_date,
          match_time: currentMatch.value.match_time
        }
      })
    }
    
    if (response.data.success) {
      ElMessage.success(editingMatch.value ? '比赛更新成功' : '比赛添加成功')
      showAddMatchDialog.value = false
      editingMatch.value = false
      currentMatch.value = {
        id: null,
        league_id: '',
        home_team: '',
        away_team: '',
        match_date: '',
        match_time: '',
        status: 'upcoming',
        score: ''
      }
      
      loadMatches()
      loadStats()
    } else {
      ElMessage.error(response.data.message || (editingMatch.value ? '更新失败' : '添加失败'))
    }
  } catch (error) {
    console.error('保存比赛失败:', error)
    ElMessage.error('保存比赛失败')
  }
}

const applyFilters = async () => {
  // 分页重置到第一页
  pagination.currentPage = 1
  
  loading.value = true
  try {
    const response = await axios.get('/api/admin/v1/matches', {
      params: {
        page: pagination.currentPage,
        size: pagination.pageSize,
        league_id: filters.leagueId,
        status: filters.status,
        search_keyword: filters.searchKeyword
      }
    })
    
    if (response.data.success) {
      matches.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取比赛数据失败')
    }
  } catch (error) {
    console.error('获取比赛数据失败:', error)
    ElMessage.error('获取比赛数据失败')
  } finally {
    loading.value = false
  }
}

const resetFilters = async () => {
  filters.leagueId = ''
  filters.status = ''
  filters.searchKeyword = ''
  pagination.currentPage = 1
  
  await loadMatches()
}

const validateData = async () => {
  validationLoading.value = true
  showValidationDialog.value = true
  
  try {
    // 模拟数据验证
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    validationResults.value = [
      { field: 'match_date', problem: '日期格式不正确', severity: '高', details: '比赛ID 4 的日期格式应为 YYYY-MM-DD' },
      { field: 'score', problem: '比分缺失', severity: '中', details: '比赛ID 1 的比分字段为空' },
      { field: 'home_team', problem: '字段长度异常', severity: '低', details: '比赛ID 2 的主队名称过长' }
    ]
  } catch (error) {
    console.error('数据验证失败:', error)
  } finally {
    validationLoading.value = false
  }
}

const detectAnomalies = () => {
  ElMessage.info('异常检测功能开发中...')
}

const viewOdds = (match) => {
  ElMessage.info(`查看比赛 ${match.home_team} VS ${match.away_team} 的赔率`)
}

const getStatusTagType = (status) => {
  const statusMap = {
    upcoming: 'info',
    live: 'success',
    finished: 'warning',
    cancelled: 'danger'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    upcoming: '未开始',
    live: '进行中',
    finished: '已结束',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

const getDataQualityType = (quality) => {
  const qualityMap = {
    high: 'success',
    medium: 'warning',
    low: 'danger'
  }
  return qualityMap[quality] || 'info'
}

const getDataQualityText = (quality) => {
  const qualityMap = {
    high: '高质量',
    medium: '中等',
    low: '低质量'
  }
  return qualityMap[quality] || '未知'
}

const getSeverityType = (severity) => {
  const severityMap = {
    高: 'danger',
    中: 'warning',
    低: 'info'
  }
  return severityMap[severity] || 'info'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const handleSizeChange = async (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  await loadMatches()
}

const handleCurrentChange = async (page) => {
  pagination.currentPage = page
  await loadMatches()
}

// 生命周期
onMounted(async () => {
  await Promise.all([
    loadMatches(),
    loadLeagues(),
    loadStats()
  ])
})
</script>

<style scoped>
.match-management {
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

.match-teams {
  display: flex;
  align-items: center;
  gap: 10px;
}

.home-team {
  font-weight: bold;
  color: var(--primary, #409eff);
}

.vs {
  color: var(--text-muted, #909399);
  font-size: 12px;
}

.away-team {
  font-weight: bold;
  color: var(--success, #67c23a);
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

.dialog-footer {
  text-align: right;
}
</style>