<template>
  <div class="api-logs-container">
    <el-page-header title="API日志" @back="$router.go(-1)" />
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
    <!-- 日志详情弹窗 -->
    <el-dialog title="日志详情" :visible.sync="showDetailDialog" width="60%">
      <div v-if="selectedLog">
        <p><strong>时间:</strong> {{ selectedLog.timestamp }}</p>
        <p><strong>级别:</strong> <el-tag :type="getTagType(selectedLog.level)">{{ selectedLog.level }}</el-tag></p>
        <p><strong>请求路径:</strong> {{ selectedLog.request_path }}</p>
        <p><strong>响应状态:</strong> {{ selectedLog.response_status }}</p>
        <p><strong>耗时:</strong> {{ selectedLog.duration_ms }}ms</p>
        <p><strong>IP地址:</strong> {{ selectedLog.ip_address || '-' }}</p>
        <p><strong>用户代理:</strong> {{ selectedLog.user_agent }}</p>
        <p><strong>会话ID:</strong> {{ selectedLog.session_id }}</p>
        <p><strong>消息:</strong> {{ selectedLog.message }}</p>
        <p v-if="selectedLog.extra_data"><strong>额外数据:</strong></p>
        <pre v-if="selectedLog.extra_data" style="margin-left: 20px;">{{ formatExtraData(selectedLog.extra_data) }}</pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="showDetailDialog = false">关闭</el-button>
        <el-button type="primary" @click="showDetailDialog = false">确认</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import LogTable from '@/components/LogTable.vue'
import http from '@/utils/http'
import { processLogResponse, getLogLevelType } from '@/utils/logUtils.js'

const API_BASE = '/api/admin/system';

export default {
  name: 'APILogs',
  components: {
    LogTable
  },
  setup() {
    const logs = ref([])
    const totalLogs = ref(0)
    const loading = ref(false)
    const currentPage = ref(1)
    const pageSize = ref(50)
    const showDetailDialog = ref(false)
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
      selectedLog.value = log
      showDetailDialog.value = true
    }

    const getTagType = (level) => {
      return getLogLevelType(level)
    }

    const formatExtraData = (extraData) => {
      try {
        if (typeof extraData === 'string') {
          const parsed = JSON.parse(extraData)
          return JSON.stringify(parsed, null, 2)
        }
        return JSON.stringify(extraData, null, 2)
      } catch (e) {
        return String(extraData)
      }
    }

    onMounted(() => {
      loadLogs()
    })

    return {
      logs,
      totalLogs,
      loading,
      currentPage,
      pageSize,
      showDetailDialog,
      selectedLog,
      handleSearch,
      handleReset,
      handleExport,
      handleBulkDelete,
      handleSizeChange,
      handleCurrentChange,
      viewLogDetails,
      getTagType,
      formatExtraData
    }
  }
}
</script>

<style scoped>
.api-logs-container {
  padding: 20px;
}
</style>