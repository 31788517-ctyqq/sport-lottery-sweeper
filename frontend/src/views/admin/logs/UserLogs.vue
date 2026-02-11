<template>
  <div class="user-logs-container">
    <el-page-header title="用户日志" @back="$router.go(-1)" />
    <LogTable
      :logs="logs"
      :loading="loading"
      :total-logs="totalLogs"
      @search="handleSearch"
      @reset="handleReset"
      @export="handleExport"
      @bulk-delete="handleBulkDelete"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
      @view-details="viewLogDetails"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LogTable from '@/components/LogTable.vue'
import http from '@/utils/http'
import { processLogResponse } from '@/utils/logUtils.js'

const API_BASE = '/api/v1/admin/system';

export default {
  name: 'UserLogs',
  components: {
    LogTable
  },
  setup() {
    const logs = ref([])
    const totalLogs = ref(0)
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(50)

    const loadLogs = async (params = {}) => {
      loading.value = true
      try {
        const logParams = {
          skip: (currentPage.value - 1) * pageSize.value,
          limit: pageSize.value,
          ...params
        }
        const response = await http.get(`${API_BASE}/logs/db/user`, { params: logParams })
        const { items, total } = processLogResponse(response)
        logs.value = items
        totalLogs.value = total
      } catch (error) {
        console.error('加载用户日志失败:', error)
        ElMessage.error('加载用户日志失败')
        logs.value = []
        totalLogs.value = 0
      } finally {
        loading.value = false
      }
    }

    const handleSearch = (filters) => {
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

    const handleSizeChange = (size) => {
      pageSize.value = size
      loadLogs()
    }

    const handleCurrentChange = (page) => {
      currentPage.value = page
      loadLogs()
    }

    const viewLogDetails = (log) => {
      console.log('查看用户日志详情:', log)
      ElMessage.info('用户日志详情功能开发中...')
    }

    onMounted(() => {
      loadLogs()
    })

    return {
      logs,
      totalLogs,
      loading,
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
.user-logs-container {
  padding: 20px;
}
</style>