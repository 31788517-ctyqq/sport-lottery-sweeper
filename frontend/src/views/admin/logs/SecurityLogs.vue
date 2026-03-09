<template>
  <div class="security-logs-container">
    <el-page-header title="返回" content="安全日志" @back="$router.go(-1)" />
    <LogTable
      :logs="logs"
      :loading="loading"
      :total-logs="totalLogs"
      :show-actions="false"
      :show-selection="false"
      :enable-level-filter="false"
      @search="handleSearch"
      @reset="handleReset"
      @export="handleExport"
      @bulk-delete="handleBulkDelete"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      @view-details="viewLogDetails"
    />

    <LogEntryDetailDialog v-model="detailVisible" :log="selectedLog" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LogTable from '@/components/LogTable.vue'
import LogEntryDetailDialog from '@/components/admin/LogEntryDetailDialog.vue'
import http from '@/utils/http'
import { processLogResponse } from '@/utils/logUtils.js'

const API_BASE = '/api/v1/admin/system';

const logs = ref([])
const totalLogs = ref(0)
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(50)
const statistics = ref({})
const detailVisible = ref(false)
const selectedLog = ref(null)

const loadLogs = async (params = {}) => {
  loading.value = true
  try {
    // 加载安全日志
    const logParams = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value,
      ...params
    }
    const response = await http.get(`${API_BASE}/logs/db/security`, { params: logParams })
    const { items, total } = processLogResponse(response)
    logs.value = items
    totalLogs.value = total

    // 加载统计信息
    const statsResponse = await http.get(`${API_BASE}/logs/db/statistics`)
    statistics.value = statsResponse.data || {}
  } catch (error) {
    console.error('加载安全日志失败:', error)
    ElMessage.error('加载安全日志失败')
    logs.value = []
    totalLogs.value = 0
  } finally {
    loading.value = false
  }
}

const handleSearch = (filters) => {
  currentPage.value = 1
  loadLogs(filters)
}

const handleReset = () => {
  currentPage.value = 1
  loadLogs()
}

const handleExport = async (filters) => {
  ElMessage.info('导出功能开发中...')
}

const handleBulkDelete = async (ids) => {
  ElMessage.info('批量删除功能开发中...')
}

const handleSizeChange = (size, filters) => {
  pageSize.value = size
  currentPage.value = 1
  loadLogs(filters || {})
}

const handleCurrentChange = (page, filters) => {
  currentPage.value = page
  loadLogs(filters || {})
}

const viewLogDetails = (log) => {
  selectedLog.value = log
  detailVisible.value = true
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped>
.security-logs-container {
  padding: 20px;
}
</style>
