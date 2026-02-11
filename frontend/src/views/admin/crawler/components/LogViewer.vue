<template>
  <div class="log-viewer">
    <!-- 工具栏 -->
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
            <el-button 
              type="primary" 
              @click="toggleAutoScroll"
              :class="{ 'active': autoScroll }"
            >
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
    
    <!-- 日志内容区域 -->
    <div class="log-content-container">
      <div 
        ref="logContentRef"
        class="log-content"
        @scroll="handleScroll"
      >
        <!-- 日志条目 -->
        <div 
          v-for="log in filteredLogs" 
          :key="log.id"
          class="log-entry"
          :class="{
            'highlighted': isHighlighted(log),
            'debug': log.log_level === 'DEBUG',
            'info': log.log_level === 'INFO',
            'warning': log.log_level === 'WARNING',
            'error': log.log_level === 'ERROR',
            'critical': log.log_level === 'CRITICAL'
          }"
        >
          <div class="log-timestamp">
            {{ formatDateTime(log.timestamp) }}
          </div>
          <div class="log-level">
            <el-tag 
              :type="getLevelType(log.log_level)" 
              size="small"
              effect="plain"
            >
              {{ log.log_level }}
            </el-tag>
          </div>
          <div class="log-message">
            <span v-html="highlightSearch(log.message)"></span>
          </div>
          <div class="log-details" v-if="log.details">
            <el-button 
              size="small" 
              text 
              @click="toggleLogDetails(log.id)"
            >
              {{ expandedLogs.includes(log.id) ? '隐藏详情' : '查看详情' }}
            </el-button>
            <div 
              v-if="expandedLogs.includes(log.id)" 
              class="log-details-content"
            >
              <pre>{{ JSON.stringify(log.details, null, 2) }}</pre>
            </div>
          </div>
        </div>
        
        <!-- WebSocket连接状态 -->
        <div v-if="websocketConnected" class="connection-status">
          <el-alert
            title="WebSocket连接正常，实时接收日志更新"
            type="success"
            :closable="false"
            show-icon
          />
        </div>
        <div v-else class="connection-status">
          <el-alert
            title="WebSocket连接断开，尝试重连中..."
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </div>
    
    <!-- 底部统计信息 -->
    <div class="log-stats">
      <el-row :gutter="10">
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">总日志数</div>
            <div class="stat-value">{{ totalLogs }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">过滤后</div>
            <div class="stat-value">{{ filteredLogs.length }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">信息级</div>
            <div class="stat-value">{{ getLevelCount('INFO') }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">警告级</div>
            <div class="stat-value">{{ getLevelCount('WARNING') }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">错误级</div>
            <div class="stat-value">{{ getLevelCount('ERROR') }}</div>
          </div>
        </el-col>
        <el-col :span="4">
          <div class="stat-item">
            <div class="stat-label">临界级</div>
            <div class="stat-value">{{ getLevelCount('CRITICAL') }}</div>
          </div>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { 
  Search, 
  VideoPlay, 
  Delete, 
  Download 
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

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

// 模拟日志数据
const mockLogs = [
  {
    id: 1,
    execution_id: props.executionId,
    log_level: 'INFO',
    message: '任务开始执行，目标数据源：500彩票网',
    details: { source: '500彩票网', task_type: '赛程采集' },
    timestamp: dayjs().subtract(10, 'minute').toISOString()
  },
  {
    id: 2,
    execution_id: props.executionId,
    log_level: 'INFO',
    message: '已成功获取第1页数据，共20条记录',
    details: { page: 1, records: 20 },
    timestamp: dayjs().subtract(9, 'minute').toISOString()
  },
  {
    id: 3,
    execution_id: props.executionId,
    log_level: 'WARNING',
    message: '第2页数据获取超时，正在重试...',
    details: { page: 2, retry_count: 1 },
    timestamp: dayjs().subtract(8, 'minute').toISOString()
  },
  {
    id: 4,
    execution_id: props.executionId,
    log_level: 'INFO',
    message: '重试成功，获取第2页数据，共18条记录',
    details: { page: 2, records: 18 },
    timestamp: dayjs().subtract(7, 'minute').toISOString()
  },
  {
    id: 5,
    execution_id: props.executionId,
    log_level: 'ERROR',
    message: '第3页数据解析失败，跳过该页',
    details: { page: 3, error: 'HTML结构变更' },
    timestamp: dayjs().subtract(6, 'minute').toISOString()
  },
  {
    id: 6,
    execution_id: props.executionId,
    log_level: 'INFO',
    message: '任务执行完成，总计处理58条记录',
    details: { total_records: 58, success: 38, failed: 1, skipped: 19 },
    timestamp: dayjs().subtract(5, 'minute').toISOString()
  }
]

// 初始化日志数据
onMounted(() => {
  logs.value = mockLogs
  scrollToBottom()
})

// 格式化日期时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return dayjs(dateTime).format('YYYY-MM-DD HH:mm:ss')
}

// 获取日志级别对应的颜色类型
const getLevelType = (level) => {
  const typeMap = {
    'DEBUG': 'info',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return typeMap[level] || 'info'
}

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑已经在计算属性中处理
}

// 处理日志级别筛选
const handleLevelFilter = () => {
  // 筛选逻辑已经在计算属性中处理
}

// 切换自动滚动
const toggleAutoScroll = () => {
  autoScroll.value = !autoScroll.value
  if (autoScroll.value) {
    scrollToBottom()
  }
}

// 清空日志
const clearLogs = () => {
  logs.value = []
}

// 下载日志
const downloadLogs = () => {
  const logText = filteredLogs.value.map(log => 
    `[${formatDateTime(log.timestamp)}] [${log.log_level}] ${log.message}`
  ).join('\n')
  
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

// 切换日志详情展开状态
const toggleLogDetails = (logId) => {
  const index = expandedLogs.value.indexOf(logId)
  if (index > -1) {
    expandedLogs.value.splice(index, 1)
  } else {
    expandedLogs.value.push(logId)
  }
}

// 滚动到底部
const scrollToBottom = async () => {
  if (!autoScroll.value || !logContentRef.value || isScrollingManually.value) return
  
  await nextTick()
  const container = logContentRef.value
  container.scrollTop = container.scrollHeight
}

// 处理滚动事件
const handleScroll = (event) => {
  const container = event.target
  const isAtBottom = container.scrollHeight - container.scrollTop <= container.clientHeight + 10
  
  if (!isAtBottom) {
    isScrollingManually.value = true
  } else {
    isScrollingManually.value = false
  }
}

// 检查日志是否高亮（包含搜索关键词）
const isHighlighted = (log) => {
  if (!searchKeyword.value) return false
  return log.message.toLowerCase().includes(searchKeyword.value.toLowerCase())
}

// 高亮搜索关键词
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

// 过滤后的日志列表
const filteredLogs = computed(() => {
  return logs.value.filter(log => {
    // 按级别筛选
    if (selectedLevels.value.length > 0 && !selectedLevels.value.includes(log.log_level)) {
      return false
    }
    
    // 按关键词搜索
    if (searchKeyword.value && !log.message.toLowerCase().includes(searchKeyword.value.toLowerCase())) {
      return false
    }
    
    return true
  })
})

const totalLogs = computed(() => logs.value.length)

// 获取指定级别的日志数量
const getLevelCount = (level) => {
  return logs.value.filter(log => log.log_level === level).length
}

// 监听日志变化，自动滚动到底部
watch(() => logs.value.length, () => {
  scrollToBottom()
})

// 监听过滤后的日志变化
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
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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

/* 日志级别颜色 */
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

/* 搜索高亮 */
.search-highlight {
  background-color: #ffeb3b;
  color: #000;
  padding: 1px 2px;
  border-radius: 2px;
  font-weight: bold;
}

/* WebSocket连接状态指示器 */
.connection-status {
  position: sticky;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(4px);
}
</style>