<template>
  <div class="log-table-container">
    <!-- 筛选区域 -->
    <el-card v-if="showFilters" class="filter-card">
      <el-row :gutter="20">
        <el-col v-if="enableDateRangeFilter" :span="6">
          <el-date-picker
            v-model="filters.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            style="width: 100%;"
          />
        </el-col>
        <el-col v-if="enableLevelFilter" :span="4">
          <el-select v-model="filters.level" placeholder="日志级别" style="width: 100%;">
            <el-option label="全部" value="" />
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARN" value="WARN" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="CRITICAL" value="CRITICAL" />
          </el-select>
        </el-col>
        <el-col :span="enableLevelFilter ? 8 : 12">
          <el-input
            v-model="filters.search"
            placeholder="搜索消息内容..."
            suffix-icon="el-icon-search"
            style="width: 100%;"
            @keyup.enter="handleSearch"
          />
        </el-col>
        <el-col :span="6">
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- 操作区域 -->
    <div class="action-bar" v-if="showActions">
      <el-button type="primary" size="small" @click="handleExport" :loading="exporting">
        导出日志
      </el-button>
      <el-button type="danger" size="small" @click="handleBulkDelete" :disabled="selectedLogs.length === 0">
        批量删除 ({{ selectedLogs.length }})
      </el-button>
    </div>

    <!-- 日志表格 -->
    <el-table
      :data="logs"
      style="width: 100%"
      height="600"
      border
      v-loading="loading"
      @selection-change="handleSelectionChange"
      :row-key="getRowKey"
    >
      <el-table-column type="selection" width="55" v-if="showSelection" />

      <el-table-column prop="timestamp" label="时间" width="160" sortable>
        <template #default="scope">
          {{ formatDate(scope.row.timestamp) }}
        </template>
      </el-table-column>

      <el-table-column prop="level" label="级别" width="100">
        <template #default="scope">
          <el-tag :type="getTagType(scope.row.level)">{{ scope.row.level }}</el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="module" label="模块" width="120">
        <template #default="scope">
          {{ scope.row.module }}
        </template>
      </el-table-column>

      <el-table-column prop="message" label="消息" min-width="300">
        <template #default="scope">
          <el-popover placement="top-start" trigger="hover" :width="400" :content="scope.row.message">
            <template #reference>
              <span class="log-message">{{ truncateMessage(scope.row.message, 100) }}</span>
            </template>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column prop="ip_address" label="IP地址" width="150">
        <template #default="scope">
          {{ scope.row.ip_address || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="user_id" label="用户ID" width="100">
        <template #default="scope">
          {{ scope.row.user_id ?? '-' }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="150">
        <template #default="scope">
          <el-button size="small" type="link" @click="viewDetails(scope.row)">查看详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      v-if="showPagination"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      :current-page="currentPage"
      :page-sizes="[20, 50, 100, 200]"
      :page-size="pageSize"
      layout="total, sizes, prev, pager, next, jumper"
      :total="totalLogs"
      class="pagination-container"
    />
  </div>
</template>

<script setup>
import { ref, defineProps, defineEmits } from 'vue'
import { ElMessageBox } from 'element-plus'

const props = defineProps({
  logs: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  totalLogs: { type: Number, default: 0 },
  showFilters: { type: Boolean, default: true },
  showActions: { type: Boolean, default: true },
  showSelection: { type: Boolean, default: true },
  showPagination: { type: Boolean, default: true },
  enableLevelFilter: { type: Boolean, default: true },
  enableDateRangeFilter: { type: Boolean, default: true }
})

const emit = defineEmits([
  'search',
  'reset',
  'export',
  'bulk-delete',
  'size-change',
  'current-change',
  'selection-change',
  'view-details'
])

const filters = ref({
  dateRange: [],
  level: '',
  search: ''
})
const currentPage = ref(1)
const pageSize = ref(50)
const selectedLogs = ref([])
const exporting = ref(false)

const buildQueryParams = () => {
  const query = {
    search: filters.value.search || undefined,
    level: filters.value.level || undefined
  }

  // Align with backend: WARN -> WARNING
  if (query.level === 'WARN') query.level = 'WARNING'

  if (
    props.enableDateRangeFilter &&
    Array.isArray(filters.value.dateRange) &&
    filters.value.dateRange.length === 2
  ) {
    const [start, end] = filters.value.dateRange
    if (start instanceof Date && !Number.isNaN(start.getTime())) query.start_date = start.toISOString()
    if (end instanceof Date && !Number.isNaN(end.getTime())) query.end_date = end.toISOString()
  }

  return query
}

const handleSearch = () => {
  currentPage.value = 1
  emit('search', buildQueryParams())
}

const handleReset = () => {
  currentPage.value = 1
  filters.value = { dateRange: [], level: '', search: '' }
  emit('reset')
}

const handleExport = async () => {
  exporting.value = true
  try {
    await emit('export', buildQueryParams())
  } finally {
    exporting.value = false
  }
}

const handleBulkDelete = () => {
  if (selectedLogs.value.length === 0) return
  ElMessageBox.confirm(`确定要删除选中的 ${selectedLogs.value.length} 条日志吗？`, '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    emit(
      'bulk-delete',
      selectedLogs.value.map((log) => log.id)
    )
  })
}

const handleSelectionChange = (selection) => {
  selectedLogs.value = selection
  emit('selection-change', selection)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  emit('size-change', size, buildQueryParams())
}

const handleCurrentChange = (page) => {
  currentPage.value = page
  emit('current-change', page, buildQueryParams())
}

const viewDetails = (log) => {
  emit('view-details', log)
}

const getRowKey = (row) => `${row.id}_${row.timestamp}`

const getTagType = (level) => {
  switch (String(level || '').toUpperCase()) {
    case 'ERROR':
    case 'CRITICAL':
      return 'danger'
    case 'WARN':
    case 'WARNING':
      return 'warning'
    case 'INFO':
      return 'info'
    case 'DEBUG':
      return 'primary'
    default:
      return 'info'
  }
}

const formatDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString('zh-CN')
}

const truncateMessage = (message, length) => {
  if (!message) return '-'
  return message.length > length ? `${message.slice(0, length)}...` : message
}
</script>

<style scoped>
.filter-card {
  margin-bottom: 20px;
}

.action-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.log-message {
  cursor: pointer;
  color: #409eff;
  text-decoration: underline;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}
</style>

