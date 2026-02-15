<template>
  <div class="log-viewer">
    <div class="log-toolbar">
      <el-row :gutter="10">
        <el-col :span="6">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索日志内容"
            clearable
            @clear="handleSearch"
            @change="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-col>
        <el-col :span="12">
          <div class="log-level-filter">
            <span class="filter-label">日志级别:</span>
            <el-checkbox-group v-model="selectedLevels" @change="handleLevelFilter">
              <el-checkbox value="DEBUG">DEBUG</el-checkbox>
              <el-checkbox value="INFO">INFO</el-checkbox>
              <el-checkbox value="WARNING">WARNING</el-checkbox>
              <el-checkbox value="ERROR">ERROR</el-checkbox>
              <el-checkbox value="CRITICAL">CRITICAL</el-checkbox>
            </el-checkbox-group>
          </div>
        </el-col>
        <el-col :span="6" class="toolbar-actions">
          <el-button-group>
            <el-button type="primary" @click="toggleAutoScroll" :class="{ active: autoScroll }">
              <el-icon><VideoPlay /></el-icon>
              {{ autoScroll ? '暂停' : '实时' }}
            </el-button>
            <el-button @click="clearLogs">
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
            <el-button @click="downloadLogs">
              <el-icon><Download /></el-icon>
              下载
            </el-button>
          </el-button-group>
        </el-col>
      </el-row>
    </div>

    <div class="log-content-container">
      <div ref="logContentRef" class="log-content" @scroll="handleScroll">
        <div
          v-for="log in filteredLogs"
          :key="log.id"
          class="log-entry"
          :class="{
            highlighted: isHighlighted(log),
            debug: log.log_level === 'DEBUG',
            info: log.log_level === 'INFO',
            warning: log.log_level === 'WARNING',
            error: log.log_level === 'ERROR',
            critical: log.log_level === 'CRITICAL'
          }"
        >
          <div class="log-timestamp">{{ formatDateTime(log.timestamp) }}</div>
          <div class="log-level">
            <el-tag :type="getLevelType(log.log_level)" size="small" effect="plain">
              {{ log.log_level }}
            </el-tag>
          </div>
          <div class="log-message">
            <span v-html="highlightSearch(log.message)" />
          </div>
          <div v-if="log.details" class="log-details">
            <el-button size="small" text @click="toggleLogDetails(log.id)">
              {{ expandedLogs.includes(log.id) ? '隐藏详情' : '查看详情' }}
            </el-button>
            <div v-if="expandedLogs.includes(log.id)" class="log-details-content">
              <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <div v-if="websocketConnected" class="connection-status">
          <el-alert title="实时连接已建立" type="success" :closable="false" show-icon />
        </div>
        <div v-else class="connection-status">
          <el-alert title="实时连接未启用，当前为接口轮询模式" type="info" :closable="false" show-icon />
        </div>
      </div>
    </div>

    <div class="log-stats">
      <el-row :gutter="10">
        <el-col :span="4"><div class="stat-item"><div class="stat-label">总日志数</div><div class="stat-value">{{ totalLogs }}</div></div></el-col>
        <el-col :span="4"><div class="stat-item"><div class="stat-label">过滤后</div><div class="stat-value">{{ filteredLogs.length }}</div></div></el-col>
        <el-col :span="4"><div class="stat-item"><div class="stat-label">信息级</div><div class="stat-value">{{ getLevelCount('INFO') }}</div></div></el-col>
        <el-col :span="4"><div class="stat-item"><div class="stat-label">警告级</div><div class="stat-value">{{ getLevelCount('WARNING') }}</div></div></el-col>
        <el-col :span="4"><div class="stat-item"><div class="stat-label">错误级</div><div class="stat-value">{{ getLevelCount('ERROR') }}</div></div></el-col>
        <el-col :span="4"><div class="stat-item"><div class="stat-label">严重级</div><div class="stat-value">{{ getLevelCount('CRITICAL') }}</div></div></el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { Download, Search, VideoPlay, Delete } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { getExecutionLogs } from '@/api/taskMonitorApi'

const props = defineProps({
  executionId: {
    type: Number,
    required: true
  },
  websocketConnected: {
    type: Boolean,
    default: false
  }
})

const logs = ref([])
const searchKeyword = ref('')
const selectedLevels = ref(['INFO', 'WARNING', 'ERROR', 'CRITICAL'])
const autoScroll = ref(true)
const expandedLogs = ref([])
const logContentRef = ref(null)
const isScrollingManually = ref(false)
let pollTimer = null

const fallbackLogs = [
  {
    id: 1,
    execution_id: props.executionId,
    log_level: 'INFO',
    message: '暂无后端日志，已展示本地示例日志',
    details: { source: 'fallback' },
    timestamp: dayjs().toISOString()
  }
]

const normalizeLevel = (value) => {
  if (!value) return 'INFO'
  const upper = String(value).toUpperCase()
  if (upper.includes('WARN')) return 'WARNING'
  if (upper.includes('ERR') || upper.includes('FAIL')) return 'ERROR'
  if (upper.includes('CRIT')) return 'CRITICAL'
  if (upper.includes('DEBUG')) return 'DEBUG'
  return 'INFO'
}

const fetchLogs = async () => {
  try {
    const res = await getExecutionLogs(props.executionId)
    const payload = Array.isArray(res) ? res : (res?.data || [])
    const apiLogs = payload.map((item) => ({
      id: item.id || `${item.timestamp || ''}-${item.message || ''}`,
      execution_id: props.executionId,
      log_level: normalizeLevel(item.log_level || item.level),
      message: item.message || '',
      details: item.details || null,
      timestamp: item.timestamp || item.created_at || new Date().toISOString()
    }))
    logs.value = apiLogs.length > 0 ? apiLogs : fallbackLogs
  } catch (error) {
    console.error('获取执行日志失败:', error)
    logs.value = fallbackLogs
  }
  scrollToBottom()
}

onMounted(() => {
  fetchLogs()
  pollTimer = setInterval(fetchLogs, 5000)
})

onUnmounted(() => {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
})

const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

const getLevelType = (level) => {
  const typeMap = {
    DEBUG: 'info',
    INFO: 'success',
    WARNING: 'warning',
    ERROR: 'danger',
    CRITICAL: 'danger'
  }
  return typeMap[level] || 'info'
}

const handleSearch = () => {}

const handleLevelFilter = () => {}

const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  if (autoScroll.value) scrollToBottom()
}

const clearLogs = () => {
  logs.value = []
}

const downloadLogs = () => {
  const logText = filteredLogs.value
    .map((log) => `[${formatDateTime(log.timestamp)}] [${log.log_level}] ${log.message}`)
    .join('\n')

  const blob = new Blob([logText], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `task-execution-${props.executionId}-logs.txt`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const toggleLogDetails = (logId) => {
  const index = expandedLogs.value.indexOf(logId)
  if (index > -1) expandedLogs.value.splice(index, 1)
  else expandedLogs.value.push(logId)
}

const scrollToBottom = async () => {
  if (!autoScroll.value || !logContentRef.value || isScrollingManually.value) return
  await nextTick()
  const container = logContentRef.value
  container.scrollTop = container.scrollHeight
}

const handleScroll = (event) => {
  const container = event.target
  const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10
  isScrollingManually.value = !isAtBottom
}

const isHighlighted = (log) => {
  if (!searchKeyword.value) return false
  return log.message.toLowerCase().includes(searchKeyword.value.toLowerCase())
}

const highlightSearch = (text) => {
  if (!searchKeyword.value || !text) return text
  const keyword = searchKeyword.value.toLowerCase()
  const lowerText = text.toLowerCase()
  let result = ''
  let lastIndex = 0

  let index = lowerText.indexOf(keyword, lastIndex)
  while (index !== -1) {
    result += text.substring(lastIndex, index)
    result += `<mark class="search-highlight">${text.substring(index, index + keyword.length)}</mark>`
    lastIndex = index + keyword.length
    index = lowerText.indexOf(keyword, lastIndex)
  }
  result += text.substring(lastIndex)
  return result
}

const filteredLogs = computed(() => {
  return logs.value.filter((log) => {
    if (selectedLevels.value.length > 0 && !selectedLevels.value.includes(log.log_level)) {
      return false
    }
    if (searchKeyword.value && !log.message.toLowerCase().includes(searchKeyword.value.toLowerCase())) {
      return false
    }
    return true
  })
})

const totalLogs = computed(() => logs.value.length)

const getLevelCount = (level) => logs.value.filter((log) => log.log_level === level).length

watch(() => logs.value.length, () => {
  scrollToBottom()
})

watch(() => filteredLogs.value.length, () => {
  scrollToBottom()
})
</script>

<style scoped>
.log-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #fff;
}

.log-toolbar {
  padding: 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.log-level-filter {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
}

.toolbar-actions {
  display: flex;
  justify-content: flex-end;
}

.log-content-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.log-content {
  height: 100%;
  overflow-y: auto;
  padding: 16px;
  font-family: Monaco, Menlo, 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  background: #1e1e1e;
  color: #d4d4d4;
}

.log-entry {
  padding: 8px 0;
  border-bottom: 1px solid #2d2d2d;
  display: grid;
  grid-template-columns: 180px 80px 1fr;
  gap: 12px;
  align-items: start;
}

.log-entry:hover {
  background: #2a2d2e;
}

.log-entry.highlighted {
  background: rgba(255, 235, 59, 0.1);
}

.log-timestamp {
  color: #6a9955;
  font-size: 11px;
  white-space: nowrap;
}

.log-level {
  min-width: 60px;
}

.log-message {
  word-break: break-word;
  white-space: pre-wrap;
}

.log-details {
  grid-column: 1 / -1;
  margin-top: 8px;
}

.log-details-content {
  background: #252526;
  border-radius: 4px;
  padding: 12px;
  margin-top: 8px;
  border: 1px solid #3e3e42;
}

.log-details-content pre {
  margin: 0;
  font-size: 11px;
  line-height: 1.4;
  color: #9cdcfe;
  overflow-x: auto;
  white-space: pre-wrap;
}

.connection-status {
  position: sticky;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
  padding: 16px;
}

.log-stats {
  padding: 12px 16px;
  background: #f5f7fa;
  border-top: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
  padding: 8px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-label {
  font-size: 10px;
  color: #909399;
  margin-bottom: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.log-entry.debug .log-message {
  color: #569cd6;
}

.log-entry.info .log-message {
  color: #4ec9b0;
}

.log-entry.warning .log-message {
  color: #d7ba7d;
}

.log-entry.error .log-message {
  color: #f44747;
}

.log-entry.critical .log-message {
  color: #ff6b6b;
  font-weight: bold;
}

.search-highlight {
  background-color: #ffeb3b;
  color: #000;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: bold;
}
</style>
