<template>
  <div class="league-management">
    <div class="page-header">
      <h2>联赛管理</h2>
      <p>管理联赛信息、筛选条件与统计概览</p>
    </div>

    <div class="stats-section">
      <el-row :gutter="12">
        <el-col :span="4"><el-card><el-statistic title="联赛总数" :value="leagueStats.totalLeagues" /></el-card></el-col>
        <el-col :span="4"><el-card><el-statistic title="国家/地区" :value="leagueStats.totalCountries" /></el-card></el-col>
        <el-col :span="4"><el-card><el-statistic title="进行中联赛" :value="leagueStats.activeLeagues" /></el-card></el-col>
        <el-col :span="4"><el-card><el-statistic title="球队总数" :value="leagueStats.totalTeams" /></el-card></el-col>
        <el-col :span="4"><el-card><el-statistic title="比赛总数" :value="leagueStats.totalMatches" /></el-card></el-col>
        <el-col :span="4"><el-card><el-statistic title="赛季完成率" :value="leagueStats.completionRate" suffix="%" :precision="1" /></el-card></el-col>
      </el-row>
    </div>

    <div class="operation-bar">
      <el-button type="primary" @click="refreshData">刷新</el-button>
      <el-button type="success" @click="openCreateDialog">添加联赛</el-button>
      <el-button type="warning" @click="exportData">导出数据</el-button>
      <el-button @click="syncWithDataSource">同步数据源</el-button>
    </div>

    <div class="filter-section">
      <el-card>
        <el-form :model="filters" inline>
          <el-form-item label="国家/地区">
            <el-select
              v-model="filters.country"
              placeholder="全部"
              clearable
              style="width: 160px"
              @change="applyFilters"
            >
              <el-option v-for="country in countries" :key="country" :label="country" :value="country" />
            </el-select>
          </el-form-item>

          <el-form-item label="联赛级别">
            <el-select
              v-model="filters.level"
              placeholder="全部"
              clearable
              style="width: 140px"
              @change="applyFilters"
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
              placeholder="全部"
              clearable
              style="width: 130px"
              @change="applyFilters"
            >
              <el-option label="进行中" value="active" />
              <el-option label="未激活" value="inactive" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </el-form-item>

          <el-form-item label="搜索">
            <el-input
              v-model="filters.searchKeyword"
              placeholder="联赛名称"
              clearable
              style="width: 220px"
              @keyup.enter="applyFilters"
              @clear="applyFilters"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="applyFilters">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>

    <div class="table-section">
      <el-table :data="leagues" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="联赛名称" min-width="180" />
        <el-table-column prop="country" label="国家/地区" width="140" />

        <el-table-column label="级别" width="110">
          <template #default="scope">
            <el-tag :type="getLevelTagType(scope.row.level)">{{ getLevelText(scope.row.level) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="season" label="赛季" width="130" />
        <el-table-column prop="total_teams" label="球队数" width="100" />
        <el-table-column prop="total_matches" label="总比赛" width="100" />
        <el-table-column prop="played_matches" label="已进行" width="100" />
        <el-table-column prop="remaining_matches" label="剩余" width="100" />

        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusTagType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="220" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="viewLeague(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editLeague(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteLeague(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

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

    <el-dialog
      v-model="showLeagueDialog"
      :title="editingLeague ? '编辑联赛' : '新增联赛'"
      width="620px"
      :close-on-click-modal="false"
    >
      <el-form :model="currentLeague" label-width="100px">
        <el-form-item label="联赛名称">
          <el-input v-model="currentLeague.name" />
        </el-form-item>

        <el-form-item label="国家/地区">
          <el-input v-model="currentLeague.country" />
        </el-form-item>

        <el-form-item label="联赛级别">
          <el-select v-model="currentLeague.level" style="width: 100%">
            <el-option label="顶级联赛" value="top" />
            <el-option label="次级联赛" value="second" />
            <el-option label="青年联赛" value="youth" />
            <el-option label="女子联赛" value="women" />
          </el-select>
        </el-form-item>

        <el-form-item label="赛季">
          <el-input v-model="currentLeague.season" placeholder="例如 2025-2026" />
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="currentLeague.status" style="width: 100%">
            <el-option label="进行中" value="active" />
            <el-option label="未激活" value="inactive" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>

        <el-form-item label="说明">
          <el-input v-model="currentLeague.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="showLeagueDialog = false">取消</el-button>
        <el-button type="primary" @click="saveLeague">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import request from '@/utils/request'

const loading = ref(false)
const leagues = ref([])
const countries = ref([])
const showLeagueDialog = ref(false)
const editingLeague = ref(false)

const currentLeague = reactive({
  id: null,
  name: '',
  country: '',
  level: 'top',
  season: '',
  status: 'active',
  description: ''
})

const filters = reactive({
  country: '',
  level: '',
  status: '',
  searchKeyword: ''
})

const pagination = reactive({
  currentPage: 1,
  pageSize: 20,
  total: 0
})

const leagueStats = reactive({
  totalLeagues: 0,
  totalCountries: 0,
  activeLeagues: 0,
  totalTeams: 0,
  totalMatches: 0,
  completionRate: 0
})

function normalizePayload(response) {
  return response?.data ?? response ?? {}
}

async function loadLeagues() {
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

    const response = await request.get('/api/v1/admin/leagues/', { params })
    const payload = normalizePayload(response)

    if (payload.success === false) {
      ElMessage.error(payload.message || '获取联赛列表失败')
      leagues.value = []
      return
    }

    const data = payload.data || {}
    leagues.value = Array.isArray(data.items) ? data.items : []
    pagination.total = Number(data.total || 0)
  } catch (error) {
    console.error('loadLeagues error:', error)
    ElMessage.error('获取联赛列表失败')
    leagues.value = []
  } finally {
    loading.value = false
  }
}

async function loadCountries() {
  try {
    const response = await request.get('/api/v1/admin/leagues/countries')
    const payload = normalizePayload(response)
    if (payload.success === false) {
      return
    }
    countries.value = Array.isArray(payload.data?.countries) ? payload.data.countries : []
  } catch (error) {
    console.error('loadCountries error:', error)
  }
}

async function loadStats() {
  try {
    const response = await request.get('/api/v1/admin/leagues/stats')
    const payload = normalizePayload(response)
    if (payload.success === false) {
      return
    }
    Object.assign(leagueStats, payload.data || {})
  } catch (error) {
    console.error('loadStats error:', error)
  }
}

function refreshData() {
  loadLeagues()
  loadStats()
  ElMessage.success('已刷新')
}

function openCreateDialog() {
  editingLeague.value = false
  Object.assign(currentLeague, {
    id: null,
    name: '',
    country: '',
    level: 'top',
    season: '',
    status: 'active',
    description: ''
  })
  showLeagueDialog.value = true
}

function editLeague(row) {
  editingLeague.value = true
  Object.assign(currentLeague, {
    id: row.id,
    name: row.name || '',
    country: row.country || '',
    level: row.level || 'top',
    season: row.season || '',
    status: row.status || 'active',
    description: row.description || ''
  })
  showLeagueDialog.value = true
}

function viewLeague(row) {
  ElMessage.info(`联赛：${row.name}`)
}

async function deleteLeague(row) {
  try {
    await ElMessageBox.confirm(`确认删除联赛「${row.name}」吗？`, '提示', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const response = await request.delete(`/api/v1/admin/leagues/${row.id}`)
    const payload = normalizePayload(response)
    if (payload.success === false) {
      ElMessage.error(payload.message || '删除失败')
      return
    }

    ElMessage.success('删除成功')
    await Promise.all([loadLeagues(), loadStats()])
  } catch (error) {
    if (error !== 'cancel') {
      console.error('deleteLeague error:', error)
      ElMessage.error('删除失败')
    }
  }
}

async function saveLeague() {
  try {
    const body = {
      name: currentLeague.name,
      country: currentLeague.country,
      level: currentLeague.level,
      season: currentLeague.season,
      status: currentLeague.status,
      description: currentLeague.description
    }

    let response
    if (editingLeague.value && currentLeague.id) {
      response = await request.put(`/api/v1/admin/leagues/${currentLeague.id}`, body)
    } else {
      response = await request.post('/api/v1/admin/leagues/', body)
    }

    const payload = normalizePayload(response)
    if (payload.success === false) {
      ElMessage.error(payload.message || '保存失败')
      return
    }

    ElMessage.success(editingLeague.value ? '更新成功' : '新增成功')
    showLeagueDialog.value = false
    await Promise.all([loadLeagues(), loadStats()])
  } catch (error) {
    console.error('saveLeague error:', error)
    ElMessage.error('保存失败')
  }
}

function exportData() {
  ElMessage.info('导出功能待完善')
}

function syncWithDataSource() {
  ElMessage.info('同步功能待完善')
}

function applyFilters() {
  pagination.currentPage = 1
  loadLeagues()
}

function resetFilters() {
  Object.assign(filters, {
    country: '',
    level: '',
    status: '',
    searchKeyword: ''
  })
  pagination.currentPage = 1
  loadLeagues()
}

function handleSizeChange(size) {
  pagination.pageSize = size
  pagination.currentPage = 1
  loadLeagues()
}

function handleCurrentChange(page) {
  pagination.currentPage = page
  loadLeagues()
}

function getLevelText(level) {
  const map = {
    top: '顶级',
    second: '次级',
    youth: '青年',
    women: '女子'
  }
  return map[level] || level || '-'
}

function getLevelTagType(level) {
  const map = {
    top: 'primary',
    second: 'success',
    youth: 'warning',
    women: 'danger'
  }
  return map[level] || 'info'
}

function getStatusText(status) {
  const map = {
    active: '进行中',
    inactive: '未激活',
    completed: '已完成'
  }
  return map[status] || status || '-'
}

function getStatusTagType(status) {
  const map = {
    active: 'success',
    inactive: 'info',
    completed: 'warning'
  }
  return map[status] || 'info'
}

onMounted(async () => {
  await Promise.all([loadCountries(), loadStats()])
  await loadLeagues()
})
</script>

<style scoped>
.league-management {
  padding: 20px;
  background: #f5f7fa;
}

.page-header {
  margin-bottom: 16px;
}

.page-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
}

.page-header p {
  margin: 0;
  color: #606266;
}

.stats-section,
.operation-bar,
.filter-section,
.table-section {
  margin-bottom: 16px;
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>
