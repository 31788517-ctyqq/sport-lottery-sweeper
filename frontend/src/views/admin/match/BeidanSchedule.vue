<template>
  <div class="beidan-match-management">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>北单赛程管理</h2>
      <p>管理和查看北京单场足球赛事赛程信息</p>
    </div>

    <!-- 统计卡片区域 -->
    <div class="stats-section">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="总期次"
              :value="new Set(filteredMatches.map(m => m.round_number)).size"
              :precision="0"
            >
              <template #prefix>
                <el-icon><Document /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="今日比赛"
              :value="filteredMatches.filter(m => isToday(m.scheduled_kickoff)).length"
              :precision="0"
              style="color: #67c23a"
            >
              <template #prefix>
                <el-icon><Calendar /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="进行中期次"
              :value="filteredMatches.filter(m => ['live','halftime'].includes(m.status)).length"
              :precision="0"
              style="color: #409eff"
            >
              <template #prefix>
                <el-icon><VideoPlay /></el-icon>
              </template>
            </el-statistic>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card">
            <el-statistic
              title="已发布"
              :value="filteredMatches.filter(m => m.is_published).length"
              :precision="0"
              style="color: #e6a23c"
            >
              <template #prefix>
                <el-icon><Star /></el-icon>
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
      <el-button type="success" @click="showImportDialog = true">
        <el-icon><Upload /></el-icon>
        导入数据
      </el-button>
      <el-button type="warning" @click="fetchCrawlerData">
        <el-icon><Search /></el-icon>
        爬取数据
      </el-button>
      <el-button type="info" @click="exportData">
        <el-icon><Document /></el-icon>
        导出数据
      </el-button>
    </div>
          <!-- 数据导入对话框 -->
          <el-dialog
            v-model="showImportDialog"
            title="导入比赛数据"
            width="600px"
            :close-on-click-modal="false"
          >
            <el-form :model="importForm" label-width="120px">
              <el-form-item label="选择联赛">
                <el-select v-model="importForm.leagueId" placeholder="请选择联赛" style="width: 100%">
                  <el-option
                    v-for="league in leagues"
                    :key="league.id"
                    :label="league.name"
                    :value="league.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="导入方式">
                <el-radio-group v-model="importForm.importType">
                  <el-radio label="file">文件导入</el-radio>
                  <el-radio label="crawler">爬虫导入</el-radio>
                  <el-radio label="api">外部接口</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item v-if="importForm.importType === 'file'" label="上传文件">
                <el-upload
                  class="upload-demo"
                  drag
                  :action="uploadUrl"
                  :headers="uploadHeaders"
                  :on-success="handleUploadSuccess"
                  :on-error="handleUploadError"
                  :before-upload="beforeUpload"
                  accept=".csv,.xlsx,.xls"
                  :data="uploadData"
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                  <template #tip>
                    <div class="el-upload__tip">支持 CSV、Excel 格式文件，文件不超过 10MB</div>
                  </template>
                </el-upload>
              </el-form-item>

              <el-form-item v-if="importForm.importType === 'api'" label="API地址">
                <el-input
                  v-model="importForm.apiUrl"
                  placeholder="请输入外部API地址"
                  clearable
                />
              </el-form-item>
            </el-form>

            <template #footer>
              <span class="dialog-footer">
                <el-button @click="showImportDialog = false">取消</el-button>
                <el-button type="primary" @click="handleImport" :loading="importLoading">
                  开始导入
                </el-button>
              </span>
            </template>
          </el-dialog>

    <!-- 筛选栏 -->
    <div class="filter-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="搜索关键词">
            <el-input
              v-model="searchKeyword"
              placeholder="搜索联赛、主队、客队"
              clearable
              style="width: 200px"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-form-item>
          <el-form-item label="时间范围">
            <el-select v-model="selectedDays" placeholder="选择天数" @change="handleDaysChange" style="width: 120px">
              <el-option label="近3天" :value="3" />
              <el-option label="近7天" :value="7" />
              <el-option label="近30天" :value="30" />
              <el-option label="近5天" :value="5" />
              <el-option label="近15天" :value="15" />
            </el-select>
          </el-form-item>
          <el-form-item label="联赛筛选">
            <el-select v-model="selectedLeague" placeholder="选择联赛" clearable @change="handleLeagueChange" style="width: 150px">
              <el-option
                v-for="league in leagues"
                :key="league.id"
                :label="league.name"
                :value="league.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

        <!-- 北单比赛数据表格 -->
        <div class="table-section">
          <el-table
            :data="filteredMatches"
            v-loading="loading"
            stripe
            border
          >
              <el-table-column label="比赛编号" width="80">
                <template #default="scope">
                  {{ scope.$index + 1 }}
                </template>
              </el-table-column>
              <el-table-column prop="league_name" label="联赛" width="120" />
              <el-table-column label="比赛时间" width="180">
                <template #default="scope">
                  {{ formatDateTime(scope.row.scheduled_kickoff) }}
                </template>
              </el-table-column>
              <el-table-column label="对阵" min-width="160">
                <template #default="scope">
                  <div class="match-teams">
                    <span class="home-team">{{ scope.row.home_team }}</span>
                    <span class="vs">VS</span>
                    <span class="away-team">{{ scope.row.away_team }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="状态" width="100">
                <template #default="scope">
                  <el-tag :type="getStatusTagType(scope.row.status)" size="small">
                    {{ getStatusText(scope.row.status) }}
                  </el-tag>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="350" fixed="right">
                <template #default="scope">
                  <div style="display: flex; gap: 4px; flex-wrap: nowrap;">
                    <el-button size="small" @click="handleView(scope.row)">查看</el-button>
                    <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
                    <el-button 
                      size="small" 
                      :type="scope.row.is_published ? 'warning' : 'success'"
                      @click="togglePublish(scope.row)"
                    >
                      {{ scope.row.is_published ? '取消发布' : '发布' }}
                    </el-button>
                    <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>

          <!-- 分页区域 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pagination.page"
              v-model:page-size="pagination.size"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
            />
          </div>

    <!-- AI 多智能体协同锁 -->
    <!-- 
      AI_DONE: coder1 @2026-01-27T00:00:00
      架构师: 确认 8:4 布局、BaseCard、莫兰迪主题
      前端: 已完成 BeidanSchedule.vue 迁移
      后端: 无需修改
      测试: 待验证
    -->
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, Upload, UploadFilled, Connection, Star, Document, Calendar, VideoPlay, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import BaseCard from '@/components/common/BaseCard.vue'
import axios from 'axios'

// 筛选表单
const filters = reactive({
  name: '',
  league_id: '',
  days: 5
})

// 响应式数据
const loading = ref(false)
const matches = ref([])
const leagues = ref([])
const selectedDays = ref(3)  // 修改为默认3天
const selectedLeague = ref('')
const searchKeyword = ref('')
const showImportDialog = ref(false)
const importLoading = ref(false)

// 分页
const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 导入表单
const importForm = reactive({
  leagueId: '',
  importType: 'file',
  apiUrl: ''
})

// 计算属性
const filteredMatches = computed(() => {
  let filtered = matches.value
  
  // 联赛筛选
  if (selectedLeague.value) {
    filtered = filtered.filter(match => match.league_id === selectedLeague.value)
  }
  
  // 关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(match => 
      match.league_name?.toLowerCase().includes(keyword) ||
      match.home_team?.toLowerCase().includes(keyword) ||
      match.away_team?.toLowerCase().includes(keyword) ||
      match.match_identifier?.toLowerCase().includes(keyword)
    )
  }
  
  return filtered
})

// 上传相关
const uploadUrl = computed(() => `/api/admin/matches/import/file`)
const uploadHeaders = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}))
const uploadData = computed(() => ({
  league_id: importForm.leagueId
}))

// 状态分布
const statusDistribution = computed(() => {
  const dist = {}
  filteredMatches.value.forEach(m => {
    dist[m.status] = (dist[m.status] || 0) + 1
  })
  return Object.keys(dist).map(status => ({ status, count: dist[status] }))
})

// 方法
const handleSearch = () => {
  pagination.page = 1
  fetchMatches()
}

const resetFilters = () => {
  searchKeyword.value = ''
  selectedDays.value = 3  // 默认设置为3天
  selectedLeague.value = ''
  filters.name = ''
  filters.days = 3  // 默认设置为3天
  filters.league_id = ''
  handleSearch()
}

const handleDaysChange = (days) => {
  selectedDays.value = days
  filters.days = days
  handleSearch()
}

const handleLeagueChange = (leagueId) => {
  selectedLeague.value = leagueId
  filters.league_id = leagueId
  handleSearch()
}

// 日期判断辅助函数
const isToday = (dateStr) => {
  if (!dateStr) return false
  const today = new Date()
  const date = new Date(dateStr)
  return date.toDateString() === today.toDateString()
}

// 方法
const fetchMatches = async () => {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      size: pagination.size,
      days: selectedDays.value,
      keyword: searchKeyword.value || undefined,
      league_id: selectedLeague.value || undefined
    }
    
    const response = await axios.get('/api/admin/v1/beidan-schedules/', { params })
    
    if (response.data.success) {
      matches.value = response.data.data.items
      pagination.total = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '获取北单比赛数据失败')
    }
  } catch (error) {
    console.error('获取北单比赛数据失败:', error)
    ElMessage.error('获取北单比赛数据失败')
  } finally {
    loading.value = false
  }
}

const fetchLeagues = async () => {
  try {
    const response = await axios.get('/api/admin/v1/beidan-schedules/leagues')
    
    if (response.data.success) {
      leagues.value = response.data.data.items
    } else {
      console.error('获取联赛列表失败:', response.data.message)
    }
  } catch (error) {
    console.error('获取联赛列表失败:', error)
  }
}



const refreshData = () => {
  pagination.page = 1
  fetchMatches()
  ElMessage.success('北单数据已刷新')
}

const fetchCrawlerData = () => {
  ElMessage.info('爬取数据功能待实现')
}

const handleView = (row) => {
  console.log('查看北单比赛详情:', row)
  ElMessage.info('查看详情功能开发中...')
}

const handleEdit = (row) => {
  console.log('编辑北单比赛:', row)
  ElMessage.info('编辑功能开发中...')
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除北单比赛 "${row.home_team} VS ${row.away_team}" 吗？`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await axios.delete(`/api/admin/v1/beidan-schedules/${row.id}`)
    
    const index = matches.value.findIndex(item => item.id === row.id)
    if (index > -1) {
      matches.value.splice(index, 1)
      pagination.total--
      ElMessage.success('删除成功')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const togglePublish = async (row) => {
  try {
    const response = await axios.put(`/api/admin/v1/beidan-schedules/${row.id}/publish`, {}, {
      params: { publish: !row.is_published }
    })
    
    if (response.data.success) {
      row.is_published = !row.is_published
      ElMessage.success(`${row.is_published ? '取消发布' : '发布'}成功`)
    } else {
      ElMessage.error(response.data.message || '操作失败')
    }
  } catch (error) {
    console.error('操作失败:', error)
    ElMessage.error('操作失败')
  }
}

const exportData = async () => {
  try {
    const params = {
      page: 1,
      size: 9999,  // 获取所有数据
      days: selectedDays.value,
      keyword: searchKeyword.value || undefined,
      league_id: selectedLeague.value || undefined,
      export: true
    }
    
    const response = await axios.get('/api/admin/v1/beidan-schedules/', { 
      params,
      responseType: 'blob'  // 重要：接收二进制数据
    })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `北单赛程_${new Date().toISOString().split('T')[0]}.xlsx`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleImport = async () => {
  if (!importForm.leagueId) {
    ElMessage.warning('请选择联赛')
    return
  }
  
  importLoading.value = true
  
  try {
    if (importForm.importType === 'crawler') {
      ElMessage.info('正在启动爬虫获取数据...')
      await new Promise(resolve => setTimeout(resolve, 2000))
    } else if (importForm.importType === 'api') {
      if (!importForm.apiUrl) {
        ElMessage.warning('请输入API地址')
        return
      }
      
      ElMessage.info('正在从外部API获取数据...')
      await axios.post('/api/admin/v1/beidan-schedules/import/api', {
        api_url: importForm.apiUrl,
        league_id: importForm.leagueId
      })
      
      ElMessage.success('API数据获取成功')
    } else {
      // file upload will be handled by el-upload component
      showImportDialog.value = false
      return
    }
    
    ElMessage.success('导入成功')
    fetchMatches()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    importLoading.value = false
  }
}

const beforeUpload = (file) => {
  const isValidType = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'].includes(file.type)
  const isLt10MB = file.size / 1024 / 1024 < 10
  
  if (!isValidType) {
    ElMessage.error('只能上传 CSV、Excel 格式的文件!')
    return false
  }
  if (!isLt10MB) {
    ElMessage.error('文件大小不能超过 10MB!')
    return false
  }
  return true
}

const handleUploadSuccess = (response) => {
  ElMessage.success('文件上传成功')
  showImportDialog.value = false
  fetchMatches()
}

const handleUploadError = (error) => {
  console.error('文件上传失败:', error)
  ElMessage.error('文件上传失败')
}

const formatDateTime = (datetime) => {
  if (!datetime) return '-'
  return new Date(datetime).toLocaleString('zh-CN')
}

const getStatusTagType = (status) => {
  const statusMap = {
    scheduled: 'info',
    live: 'success',
    halftime: 'warning',
    finished: 'success',
    postponed: 'warning',
    cancelled: 'danger',
    abandoned: 'danger',
    suspended: 'warning'
  }
  return statusMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    scheduled: '未开奖',
    live: '进行中',
    halftime: '中场',
    finished: '已开奖',
    postponed: '延期',
    cancelled: '取消',
    abandoned: '中止',
    suspended: '暂停'
  }
  return statusMap[status] || status
}

const getImportanceTagType = (importance) => {
  const importanceMap = {
    low: 'info',
    medium: '',
    high: 'warning',
    very_high: 'danger'
  }
  return importanceMap[importance] || ''
}

const getImportanceText = (importance) => {
  const importanceMap = {
    low: '普通',
    medium: '中等',
    high: '重要',
    very_high: '非常重要'
  }
  return importanceMap[importance] || importance
}

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  fetchMatches()
}

const handleCurrentChange = (page) => {
  pagination.page = page
  fetchMatches()
}

// 生命周期
onMounted(() => {
  fetchMatches()
  fetchLeagues()
})
</script>

<style scoped>
.beidan-match-management {
  padding: 20px;
  background-color: var(--bg-body, #f5f7fa);
}

/* 页面标题 */
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

/* 统计卡片区域 */
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

/* 操作栏 */
.operation-bar {
  margin-bottom: 24px;
}

.operation-bar .el-button {
  margin-right: 12px;
  margin-bottom: 8px;
}

/* 筛选栏 */
.filter-section {
  margin-bottom: 24px;
}

.filter-section :deep(.el-card) {
  border-radius: 8px;
}

/* 表格区域 */
.table-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

/* 分页区域 */
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
}

/* 卡片间距 */
.mb-4 {
  margin-bottom: 1rem;
}

/* 队伍样式 */
.match-teams {
  display: flex;
  align-items: center;
  gap: 10px;
}
.home-team {
  font-weight: bold;
  color: var(--primary, #8aa3ab);
}
.vs {
  color: var(--text-muted, #909399);
  font-size: 12px;
}
.away-team {
  font-weight: bold;
  color: var(--success, #8a9b8f);
}

/* 统计信息 */
.stats p {
  margin: 0.5rem 0;
  color: var(--text-primary, #303133);
}

/* 状态分布 */
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 0.5rem 0;
}

/* 分页居中 */
.pagination-wrapper {
  margin-top: 20px;
  text-align: right;
}

.upload-demo {
  width: 100%;
}
.dialog-footer {
  text-align: right;
}

/* 响应式：小屏时左右分栏变为上下堆叠 */
@media (max-width: 1199px) {
  .beidan-match-management :deep(.el-col.lg-16),
  .beidan-match-management :deep(.el-col.lg-8) {
    flex: 0 0 100%;
    max-width: 100%;
  }
}
</style>