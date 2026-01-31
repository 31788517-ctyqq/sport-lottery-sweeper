<template>
  <div class="league-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>联赛管理</h2>
      <p>管理联赛信息、配置联赛参数、查看联赛统计</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="联赛总数"
              :value="leagueStats.totalLeagues"
              :precision="0"
            >
              <template #prefix>
                <el-icon><Trophy /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="国家/地区"
              :value="leagueStats.totalCountries"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><Location /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="进行中联赛"
              :value="leagueStats.activeLeagues"
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
              title="球队总数"
              :value="leagueStats.totalTeams"
              :precision="0"
              style="color: #e6a23c"
            >
              <template #prefix>
                <el-icon><User /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="4">
          <el-card class="stat-card">
            <el-statistic
              title="比赛总数"
              :value="leagueStats.totalMatches"
              :precision="0"
              style="color: #f56c6c"
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
              title="赛季完成率"
              :value="leagueStats.completionRate"
              :precision="1"
              suffix="%"
              style="color: #909399"
            >
              <template #prefix>
                <el-icon><DataLine /></el-icon>
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
      <el-button type="success" @click="showAddLeagueDialog = true">
        <el-icon><Plus /></el-icon>
        添加联赛
      </el-button>
      <el-button type="warning" @click="exportData">
        <el-icon><Download /></el-icon>
        导出数据
      </el-button>
      <el-button @click="syncWithDataSource">
        <el-icon><Connection /></el-icon>
        同步数据源
      </el-button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="国家/地区">
            <el-select 
              v-model="filters.country" 
              placeholder="选择国家/地区" 
              clearable 
              @change="applyFilters"
              style="width: 150px"
            >
              <el-option
                v-for="country in countries"
                :key="country"
                :label="country"
                :value="country"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="联赛级别">
            <el-select 
              v-model="filters.level" 
              placeholder="选择级别" 
              clearable 
              @change="applyFilters"
              style="width: 120px"
            >
              <el-option label="顶级联赛" value="top" />
              <el-option label="次级联赛" value="second" />
              <el-option label="青年联赛" value="youth" />
              <el-option label="女子联赛" value="women" />
            </el-select>
          </el-form-item>
          <el-form-item label="状态">
            <el-select 
              v-model="filters.status" 
              placeholder="选择状态" 
              clearable 
              @change="applyFilters"
              style="width: 120px"
            >
              <el-option label="进行中" value="active" />
              <el-option label="休赛期" value="inactive" />
              <el-option label="已结束" value="completed" />
            </el-select>
          </el-form-item>
          <el-form-item label="搜索">
            <el-input
              v-model="filters.searchKeyword"
              placeholder="搜索联赛名称"
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

    <!-- 联赛数据表格 -->
    <div class="table-section">
      <el-table
        :data="filteredLeagues"
        v-loading="loading"
        stripe
        border
        style="width: 100%"
        height="500"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="联赛名称" width="150" />
        <el-table-column prop="country" label="国家/地区" width="120" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="scope">
            <el-tag :type="getLevelType(scope.row.level)">
              {{ getLevelText(scope.row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="season" label="赛季" width="100" />
        <el-table-column label="比赛信息" min-width="150">
          <template #default="scope">
            <div class="match-info">
              <div>总比赛: {{ scope.row.total_matches }}</div>
              <div>已进行: {{ scope.row.played_matches }}</div>
              <div>剩余: {{ scope.row.remaining_matches }}</div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">
              {{ getStatusText(scope.row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="scope">
            <div class="action-buttons">
              <el-button size="small" @click="viewLeague(scope.row)">查看</el-button>
              <el-button size="small" type="primary" @click="editLeague(scope.row)">编辑</el-button>
              <el-button size="small" type="warning" @click="configureLeague(scope.row)">配置</el-button>
              <el-button size="small" type="danger" @click="deleteLeague(scope.row)">删除</el-button>
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

    <!-- 添加/编辑联赛对话框 -->
    <el-dialog
      v-model="showAddLeagueDialog"
      :title="editingLeague ? '编辑联赛' : '添加联赛'"
      width="600px"
      :close-on-click-modal="false"
    >
      <el-form :model="currentLeague" label-width="100px">
        <el-form-item label="联赛名称">
          <el-input v-model="currentLeague.name" placeholder="请输入联赛名称" />
        </el-form-item>
        <el-form-item label="国家/地区">
          <el-select v-model="currentLeague.country" placeholder="请选择国家/地区">
            <el-option
              v-for="country in countries"
              :key="country"
              :label="country"
              :value="country"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="联赛级别">
          <el-select v-model="currentLeague.level" placeholder="请选择联赛级别">
            <el-option label="顶级联赛" value="top" />
            <el-option label="次级联赛" value="second" />
            <el-option label="青年联赛" value="youth" />
            <el-option label="女子联赛" value="women" />
          </el-select>
        </el-form-item>
        <el-form-item label="赛季">
          <el-input v-model="currentLeague.season" placeholder="例如: 2025-2026" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="currentLeague.status" placeholder="请选择状态">
            <el-option label="进行中" value="active" />
            <el-option label="休赛期" value="inactive" />
            <el-option label="已结束" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input 
            v-model="currentLeague.description" 
            type="textarea" 
            placeholder="联赛描述信息"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showAddLeagueDialog = false">取消</el-button>
          <el-button type="primary" @click="saveLeague">确定</el-button>
        </span>
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
  Download, 
  Connection, 
  Trophy, 
  Location, 
  VideoPlay, 
  User, 
  Football, 
  DataLine,
  Search
} from '@element-plus/icons-vue'
import axios from 'axios'

// 响应式数据
const loading = ref(false)
const showAddLeagueDialog = ref(false)
const editingLeague = ref(false)

// 联赛数据
const leagues = ref([])

// 当前编辑的联赛
const currentLeague = ref({
  id: null,
  name: '',
  country: '',
  level: 'top',
  season: '',
  status: 'active',
  description: ''
})

// 国家列表
const countries = ref([])

// 统计数据
const leagueStats = reactive({
  totalLeagues: 0,
  totalCountries: 0,
  activeLeagues: 0,
  totalTeams: 0,
  totalMatches: 0,
  completionRate: 0
})

// 过滤器
const filters = reactive({
  country: '',
  level: '',
  status: '',
  searchKeyword: ''
})

// 分页
const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

// 计算属性
const filteredLeagues = computed(() => {
  let result = leagues.value
  
  // 国家筛选
  if (filters.country) {
    result = result.filter(league => league.country === filters.country)
  }
  
  // 级别筛选
  if (filters.level) {
    result = result.filter(league => league.level === filters.level)
  }
  
  // 状态筛选
  if (filters.status) {
    result = result.filter(league => league.status === filters.status)
  }
  
  // 搜索关键词
  if (filters.searchKeyword) {
    const keyword = filters.searchKeyword.toLowerCase()
    result = result.filter(league => 
      league.name.toLowerCase().includes(keyword)
    )
  }
  
  // 分页处理
  const start = (pagination.currentPage - 1) * pagination.pageSize
  const end = start + pagination.pageSize
  return result.slice(start, end)
})

// 方法
const loadLeagues = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.currentPage,
      size: pagination.pageSize,
      country: filters.country || undefined,
      level: filters.level || undefined,
      status: filters.status || undefined,
      search_keyword: filters.searchKeyword || undefined
    }
    
    const response = await axios.get('/api/admin/v1/leagues/', { params })
    
    if (response.data.success) {
      leagues.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取联赛数据失败')
    }
  } catch (error) {
    console.error('获取联赛数据失败:', error)
    ElMessage.error('获取联赛数据失败')
  } finally {
    loading.value = false
  }
}

const loadCountries = async () => {
  try {
    const response = await axios.get('/api/admin/v1/leagues/countries')
    
    if (response.data.success) {
      countries.value = response.data.data.countries
    } else {
      console.error('获取国家列表失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取国家列表失败:', error)
  }
}

const loadStats = async () => {
  try {
    const response = await axios.get('/api/admin/v1/leagues/stats')
    
    if (response.data.success) {
      Object.assign(leagueStats, response.data.data)
    } else {
      console.error('获取统计信息失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取统计信息失败:', error)
  }
}

const refreshData = () => {
  loadLeagues()
  loadStats()
  ElMessage.success('数据已刷新')
}

const viewLeague = (league) => {
  ElMessage.info(`查看联赛: ${league.name}`)
}

const editLeague = (league) => {
  Object.assign(currentLeague.value, league)
  editingLeague.value = true
  showAddLeagueDialog.value = true
}

const deleteLeague = async (league) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除联赛 "${league.name}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/api/admin/v1/leagues/${league.id}`)
    
    const index = leagues.value.findIndex(item => item.id === league.id)
    if (index > -1) {
      leagues.value.splice(index, 1)
      pagination.total--
      ElMessage.success('删除成功')
      loadStats() // 重新加载统计数据
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const saveLeague = async () => {
  try {
    if (editingLeague.value) {
      // 更新现有联赛
      const response = await axios.put(`/api/admin/v1/leagues/${currentLeague.value.id}`, {
        name: currentLeague.value.name,
        country: currentLeague.value.country,
        level: currentLeague.value.level,
        season: currentLeague.value.season,
        status: currentLeague.value.status,
        description: currentLeague.value.description
      })
      
      if (response.data.success) {
        ElMessage.success('联赛更新成功')
      } else {
        ElMessage.error(response.data.message || '更新失败')
        return
      }
    } else {
      // 添加新联赛
      const response = await axios.post('/api/admin/v1/leagues/', {
        name: currentLeague.value.name,
        country: currentLeague.value.country,
        level: currentLeague.value.level,
        season: currentLeague.value.season,
        status: currentLeague.value.status,
        description: currentLeague.value.description
      })
      
      if (response.data.success) {
        ElMessage.success('联赛添加成功')
      } else {
        ElMessage.error(response.data.message || '添加失败')
        return
      }
    }
    
    showAddLeagueDialog.value = false
    editingLeague.value = false
    currentLeague.value = {
      id: null,
      name: '',
      country: '',
      level: 'top',
      season: '',
      status: 'active',
      description: ''
    }
    loadLeagues() // 重新加载联赛列表
    loadStats() // 重新加载统计数据
  } catch (error) {
    console.error('保存联赛失败:', error)
    ElMessage.error('保存联赛失败')
  }
}

const configureLeague = (league) => {
  ElMessage.info(`配置联赛: ${league.name}`)
}

const applyFilters = () => {
  // 分页重置到第一页
  pagination.currentPage = 1
  loadLeagues()
}

const resetFilters = () => {
  filters.country = ''
  filters.level = ''
  filters.status = ''
  filters.searchKeyword = ''
  pagination.currentPage = 1
  loadLeagues()
}

const exportData = () => {
  ElMessage.info('导出功能开发中...')
}

const syncWithDataSource = () => {
  ElMessage.info('同步数据源功能开发中...')
}

const getLevelType = (level) => {
  const levelMap = {
    top: 'primary',
    second: 'success',
    youth: 'warning',
    women: 'danger'
  }
  return levelMap[level] || 'info'
}

const getLevelText = (level) => {
  const levelMap = {
    top: '顶级',
    second: '次级',
    youth: '青年',
    women: '女子'
  }
  return levelMap[level] || level
}

const getStatusType = (status) => {
  const statusMap = {
    active: 'success',
    inactive: 'info',
    completed: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    active: '进行中',
    inactive: '休赛期',
    completed: '已结束'
  }
  return statusMap[status] || status
}

const handleSizeChange = (size) => {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadLeagues()
}

const handleCurrentChange = (page) => {
  pagination.currentPage = page
  loadLeagues()
}

// 生命周期
onMounted(() => {
  loadLeagues()
  loadCountries()
  loadStats()
})
</script>

<style scoped>
.league-management {
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

.match-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: #606266;
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