<template>
  <div class="operation-log-container um-page">
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <h3>操作日志</h3>
          <div class="header-actions">
            <el-button type="primary" @click="handleExportLogs">
              <el-icon><Download /></el-icon>
              导出日志
            </el-button>
            <el-button @click="handleCleanupLogs">
              <el-icon><Delete /></el-icon>
              清理日志
            </el-button>
          </div>
        </div>
      </template>

      <div class="logs-controls">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="6" :lg="4">
            <el-input v-model="searchKeyword" placeholder="搜索操作内容" clearable class="search-input">
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select v-model="filters.userId" placeholder="操作用户" clearable filterable remote :remote-method="searchUsers" :loading="userLoading" class="user-selector">
              <el-option v-for="user in userOptions" :key="user.id" :label="user.realName || user.username" :value="user.id" />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select v-model="filters.module" placeholder="操作模块" clearable class="module-selector">
              <el-option label="全部模块" value="" />
              <el-option label="用户管理" value="user" />
              <el-option label="角色权限" value="role" />
              <el-option label="部门管理" value="department" />
              <el-option label="系统设置" value="system" />
              <el-option label="数据管理" value="data" />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="2">
            <el-select v-model="filters.action" placeholder="操作类型" clearable class="action-selector">
              <el-option label="全部" value="" />
              <el-option label="创建" value="create" />
              <el-option label="更新" value="update" />
              <el-option label="删除" value="delete" />
              <el-option label="登录" value="login" />
              <el-option label="登出" value="logout" />
            </el-select>
          </el-col>
          <el-col :xs="12" :sm="6" :md="4" :lg="3">
            <el-select v-model="filters.result" placeholder="操作结果" clearable class="result-selector">
              <el-option label="全部结果" value="" />
              <el-option label="成功" value="success" />
              <el-option label="失败" value="failed" />
            </el-select>
          </el-col>
          <el-col :xs="24" :sm="24" :md="8" :lg="9">
            <el-date-picker
              v-model="dateRange"
              type="datetimerange"
              range-separator="至"
              start-placeholder="开始时间"
              end-placeholder="结束时间"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DD HH:mm:ss"
              class="date-range-picker"
            />
          </el-col>
        </el-row>
        <el-row :gutter="20" style="margin-top: 16px;">
          <el-col :xs="24" :sm="24" :md="20" :lg="18">
            <el-button type="primary" @click="handleSearch" class="action-btn">查询</el-button>
            <el-button @click="handleReset" class="action-btn">重置</el-button>
            <el-button type="info" @click="refreshData" class="action-btn">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </el-col>
          <el-col :xs="24" :sm="24" :md="4" :lg="6">
            <el-checkbox v-model="autoRefresh" @change="handleAutoRefreshChange">自动刷新 (30s)</el-checkbox>
          </el-col>
        </el-row>
      </div>

      <div class="table-wrapper">
        <el-table
          :data="tableData"
          stripe
          style="width: 100%"
          v-loading="loading"
          height="calc(100vh - 420px)"
          class="modern-table"
        >
          <el-table-column prop="createdAt" label="操作时间" width="180">
            <template #default="scope">{{ formatDate(scope.row.createdAt) }}</template>
          </el-table-column>
          <el-table-column prop="userRealName" label="操作用户" width="140">
            <template #default="scope">
              <div class="user-info">
                <el-avatar :size="24">{{ (scope.row.userRealName || scope.row.username || 'U').charAt(0).toUpperCase() }}</el-avatar>
                <span>{{ scope.row.userRealName || scope.row.username || '-' }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="module" label="操作模块" width="120" />
          <el-table-column prop="action" label="操作类型" width="100" />
          <el-table-column prop="resource" label="操作资源" width="160" />
          <el-table-column prop="description" label="操作内容" min-width="220" show-overflow-tooltip />
          <el-table-column prop="ipAddress" label="IP地址" width="140" />
          <el-table-column prop="userAgent" label="浏览器" width="160">
            <template #default="scope">
              <span class="browser-text" :title="scope.row.userAgent">{{ getBrowserInfo(scope.row.userAgent) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.result === 'success' ? 'success' : 'danger'" size="small">{{ row.result === 'success' ? '成功' : '失败' }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="170" fixed="right">
            <template #default="scope">
              <div class="op-actions">
                <el-button type="primary" size="small" plain class="op-btn" @click="handleViewDetail(scope.row)">详情</el-button>
                <el-button type="danger" size="small" plain class="op-btn" @click="handleDeleteLog(scope.row.id)" v-if="canDeleteLog(scope.row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div v-if="tableData.length === 0" class="empty-state">
          <el-empty description="暂无操作日志" />
        </div>
      </div>

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <LogDetailDialog v-model="showDetailDialog" :log-data="currentLog" />

    <el-dialog class="um-dialog" v-model="showCleanupDialog" title="清理操作日志" width="500px">
      <el-form :model="cleanupForm" label-width="100px">
        <el-form-item label="清理条件">
          <el-radio-group v-model="cleanupForm.condition">
            <el-radio value="days">保留最近天数</el-radio>
            <el-radio value="count">保留最新数量</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="天数" v-if="cleanupForm.condition === 'days'">
          <el-input-number v-model="cleanupForm.days" :min="7" :max="365" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-form-item label="数量" v-if="cleanupForm.condition === 'count'">
          <el-input-number v-model="cleanupForm.count" :min="100" :max="10000" :step="100" controls-position="right" style="width: 100%" />
        </el-form-item>
        <el-alert title="清理后不可恢复，请谨慎操作。" type="warning" :closable="false" style="margin-top: 16px;" />
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCleanupDialog = false">取消</el-button>
          <el-button type="danger" @click="confirmCleanupLogs">确认清理</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Download, Delete, Refresh } from '@element-plus/icons-vue'
import LogDetailDialog from '@/components/admin/LogDetailDialog.vue'
import { getOperationLogs, deleteOperationLog, exportOperationLogs, cleanupOperationLogs } from '@/api/modules/operation-logs'
import { searchUsers as apiSearchUsers } from '@/api/modules/users'

const tableData = ref([])
const loading = ref(false)
const searchKeyword = ref('')
const dateRange = ref([])
const autoRefresh = ref(false)
const userOptions = ref([])
const userLoading = ref(false)
const showDetailDialog = ref(false)
const showCleanupDialog = ref(false)
const currentLog = ref({})
let autoRefreshTimer = null

const filters = reactive({
  userId: '',
  module: '',
  action: '',
  result: ''
})

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0,
  pages: 0
})

const cleanupForm = reactive({
  condition: 'days',
  days: 30,
  count: 1000
})

const buildParams = () => {
  const params = {
    page: pagination.page,
    size: pagination.size,
    search: searchKeyword.value,
    userId: filters.userId,
    module: filters.module,
    action: filters.action,
    result: filters.result
  }

  if (dateRange.value && dateRange.value.length === 2) {
    params.startTime = dateRange.value[0]
    params.endTime = dateRange.value[1]
  }
  return params
}

const toLowerText = (value) => (typeof value === 'string' ? value.toLowerCase() : value)

const normalizeLogRow = (row = {}) => ({
  ...row,
  module: toLowerText(row.module),
  action: toLowerText(row.action),
  resource: toLowerText(row.resource),
  result: toLowerText(row.result),
  ipAddress: row.ipAddress || row.ip_address || '-',
  userAgent: row.userAgent || row.user_agent || ''
})

const loadLogs = async () => {
  loading.value = true
  try {
    const response = await getOperationLogs(buildParams())
    if (response && response.data) {
      tableData.value = Array.isArray(response.data.items) ? response.data.items.map(normalizeLogRow) : []
      pagination.total = response.data.total || 0
      pagination.pages = response.data.pages || 0
    }
  } catch (error) {
    console.error('加载操作日志失败:', error)
    ElMessage.error('加载操作日志失败')
  } finally {
    loading.value = false
  }
}

const searchUsers = async (query) => {
  if (!query) {
    userOptions.value = []
    return
  }
  userLoading.value = true
  try {
    const response = await apiSearchUsers({ search: query, size: 10 })
    if (response && response.data) {
      userOptions.value = Array.isArray(response.data.items) ? response.data.items : []
    }
  } catch (error) {
    console.error('搜索用户失败:', error)
  } finally {
    userLoading.value = false
  }
}

const handleSearch = () => {
  pagination.page = 1
  loadLogs()
}

const handleReset = () => {
  searchKeyword.value = ''
  dateRange.value = []
  filters.userId = ''
  filters.module = ''
  filters.action = ''
  filters.result = ''
  pagination.page = 1
  userOptions.value = []
  loadLogs()
}

const refreshData = () => loadLogs()

const handleSizeChange = (size) => {
  pagination.size = size
  pagination.page = 1
  loadLogs()
}

const handlePageChange = (page) => {
  pagination.page = page
  loadLogs()
}

const handleAutoRefreshChange = (enabled) => {
  if (enabled) {
    autoRefreshTimer = setInterval(() => loadLogs(), 30000)
  } else if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
    autoRefreshTimer = null
  }
}

const handleViewDetail = (log) => {
  currentLog.value = {
    ...log,
    realName: log.userRealName,
    requestUrl: log.raw?.request_path || '',
    executionTime: log.raw?.duration_ms || 0,
    affectedRows: 0,
    details: log.raw?.extra_data || ''
  }
  showDetailDialog.value = true
}

const handleDeleteLog = async (logId) => {
  try {
    await ElMessageBox.confirm('确认删除这条日志记录？', '确认删除', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await deleteOperationLog(logId)
    ElMessage.success('删除成功')
    loadLogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleExportLogs = async () => {
  try {
    const response = await exportOperationLogs(buildParams())
    const blobData = response?.data instanceof Blob ? response.data : new Blob([response?.data ?? ''])
    const url = window.URL.createObjectURL(blobData)
    const link = document.createElement('a')
    link.href = url
    link.download = `operation_logs_${new Date().toISOString().slice(0, 10)}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

const handleCleanupLogs = () => {
  showCleanupDialog.value = true
}

const confirmCleanupLogs = async () => {
  try {
    const params = { condition: cleanupForm.condition }
    if (cleanupForm.condition === 'days') {
      params.days = cleanupForm.days
    } else {
      params.count = cleanupForm.count
    }
    await cleanupOperationLogs(params)
    ElMessage.success('清理成功')
    showCleanupDialog.value = false
    loadLogs()
  } catch (error) {
    console.error('清理失败:', error)
    ElMessage.error('清理失败')
  }
}

const canDeleteLog = () => true

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const getBrowserInfo = (userAgent) => {
  if (!userAgent) return '-'
  if (userAgent.includes('Chrome')) return 'chrome'
  if (userAgent.includes('Firefox')) return 'firefox'
  if (userAgent.includes('Safari')) return 'safari'
  if (userAgent.includes('Edge')) return 'edge'
  return 'unknown'
}

onMounted(() => {
  loadLogs()
})

onUnmounted(() => {
  if (autoRefreshTimer) clearInterval(autoRefreshTimer)
})
</script>

<style scoped>
.operation-log-container {
  --m-bg: #f5f7fa;
  --m-card: #ffffff;
  --m-border: #ebeef5;
  --m-head: #ffffff;
  --m-text: #303133;
  --m-subtext: #909399;
  padding: 20px;
  background: var(--m-bg);
  min-height: calc(100vh - 110px);
}

.logs-card {
  border-radius: 4px;
  border: 1px solid var(--m-border);
  box-shadow: none;
  background: var(--m-card);
}

.logs-card :deep(.el-card__header) {
  background: var(--m-head);
  border-bottom: 1px solid var(--m-border);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--m-text);
}

.card-header h3 {
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.logs-controls {
  padding: 16px;
  background: #ffffff;
  border-bottom: 1px solid var(--m-border);
}

.search-input,
.user-selector,
.module-selector,
.action-selector,
.result-selector,
.date-range-picker {
  width: 100%;
}

.action-btn {
  border-radius: 8px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.browser-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.op-actions {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  gap: 8px;
}

.op-actions .el-button + .el-button {
  margin-left: 0;
}

.op-actions :deep(.el-button) {
  opacity: 1;
  min-width: 56px;
}

.op-actions :deep(.el-button .el-button__text) {
  opacity: 1 !important;
  color: inherit !important;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--m-subtext);
}

.pagination-wrapper {
  padding: 16px;
  background: #ffffff;
  border-top: 1px solid var(--m-border);
  display: flex;
  justify-content: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

:deep(.um-dialog.el-dialog) {
  border: 1px solid var(--m-border);
  border-radius: 4px;
  box-shadow: none;
  overflow: hidden;
}

:deep(.um-dialog .el-dialog__header) {
  margin-right: 0;
  padding: 14px 16px;
  border-bottom: 1px solid var(--m-border);
}

:deep(.um-dialog .el-dialog__title) {
  font-size: 16px;
  font-weight: 600;
  color: var(--m-text);
}

:deep(.um-dialog .el-dialog__body) {
  padding: 16px;
}

:deep(.um-dialog .el-dialog__footer) {
  padding: 12px 16px;
  border-top: 1px solid var(--m-border);
}
</style>
