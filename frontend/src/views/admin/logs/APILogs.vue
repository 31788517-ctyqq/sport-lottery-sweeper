<template>
  <div class="api-logs-container">
    <el-page-header title="返回" content="API日志" @back="$router.go(-1)" />
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

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LogTable from '@/components/LogTable.vue'
import LogEntryDetailDialog from '@/components/admin/LogEntryDetailDialog.vue'
import http from '@/utils/http'
import { processLogResponse } from '@/utils/logUtils.js'

const API_BASE = '/api/v1/admin/system'

export default {
  name: 'APILogs',
  components: {
    LogTable,
    LogEntryDetailDialog
  },
  setup() {
    const logs = ref([])
    const totalLogs = ref(0)
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(50)
    const detailVisible = ref(false)
    const selectedLog = ref(null)

    const loadLogs = async (params = {}) => {
      loading.value = true
      try {
        const logParams = {
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value,
          ...params
        }
        const response = await http.get(`${API_BASE}/logs/db/api`, { params: logParams })
        const { items, total } = processLogResponse(response)
        logs.value = items
        totalLogs.value = total
      } catch (error) {
        console.error('加载API日志失败:', error)
        ElMessage.error('加载API日志失败')
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

    const handleExport = async () => {
      ElMessage.info('导出功能开发中...')
    }

    const handleBulkDelete = async () => {
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

    return {
      logs,
      totalLogs,
      loading,
      detailVisible,
      selectedLog,
      handleSearch,
      handleReset,
      handleExport,
      handleBulkDelete,
      handleSizeChange,
      handleCurrentChange,
      viewLogDetails
    }
  }
}
</script>

<style scoped>
.api-logs-container {
  padding: 20px;
}
</style>
