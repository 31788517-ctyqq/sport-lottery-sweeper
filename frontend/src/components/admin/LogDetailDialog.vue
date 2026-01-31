<template>
  <el-dialog
    title="操作日志详情"
    v-model="visible"
    width="700px"
    @close="handleClose"
  >
    <div class="log-detail" v-if="logData">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="日志ID">{{ logData.id }}</el-descriptions-item>
        <el-descriptions-item label="操作用户">{{ logData.realName }} ({{ logData.username }})</el-descriptions-item>
        
        <el-descriptions-item label="操作模块">{{ logData.module }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getActionTypeColor(logData.action)">
            {{ logData.action }}
          </el-tag>
        </el-descriptions-item>
        
        <el-descriptions-item label="操作结果">
          <el-tag :type="logData.result === 'success' ? 'success' : 'danger'">
            {{ logData.result === 'success' ? '成功' : '失败' }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作时间">
          {{ formatDateTime(logData.createdAt) }}
        </el-descriptions-item>
        
        <el-descriptions-item label="请求IP" :span="2">{{ logData.ipAddress }}</el-descriptions-item>
        
        <el-descriptions-item label="用户代理" :span="2">
          <el-tooltip :content="logData.userAgent" placement="top">
            <div class="user-agent-text">{{ truncateText(logData.userAgent, 80) }}</div>
          </el-tooltip>
        </el-descriptions-item>
        
        <el-descriptions-item label="请求URL" :span="2">
          <el-tooltip :content="logData.requestUrl" placement="top">
            <div class="url-text">{{ truncateText(logData.requestUrl, 80) }}</div>
          </el-tooltip>
        </el-descriptions-item>
        
        <el-descriptions-item label="执行时长">{{ logData.executionTime }}ms</el-descriptions-item>
        <el-descriptions-item label="影响行数">{{ logData.affectedRows || 0 }}</el-descriptions-item>
      </el-descriptions>
      
      <!-- 操作详情JSON -->
      <div class="detail-section" v-if="logData.details">
        <h4>操作详情</h4>
        <div class="json-viewer">
          <pre>{{ formatJson(logData.details) }}</pre>
        </div>
      </div>
      
      <!-- 错误信息 -->
      <div class="detail-section" v-if="logData.errorMessage">
        <h4>错误信息</h4>
        <el-alert
          :title="logData.errorMessage"
          type="error"
          :description="logData.errorStack"
          show-icon
          :closable="false"
        />
      </div>
      
      <!-- 扩展信息 -->
      <div class="detail-section" v-if="logData.extendedInfo">
        <h4>扩展信息</h4>
        <div class="json-viewer">
          <pre>{{ formatJson(logData.extendedInfo) }}</pre>
        </div>
      </div>
    </div>
    
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleExport">导出详情</el-button>
        <el-button @click="handleClose">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps({
  modelValue: Boolean,
  logData: Object
})

// Emits
const emit = defineEmits(['update:modelValue', 'export'])

// 响应式数据
const visible = ref(false)

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const formatDateTime = (dateTime) => {
  if (!dateTime) return '-'
  return new Date(dateTime).toLocaleString('zh-CN')
}

const getActionTypeColor = (action) => {
  const colorMap = {
    CREATE: 'success',
    UPDATE: 'warning',
    DELETE: 'danger',
    LOGIN: 'info',
    LOGOUT: 'info',
    EXPORT: 'primary',
    IMPORT: 'primary',
    VIEW: 'info'
  }
  return colorMap[action] || 'info'
}

const truncateText = (text, maxLength) => {
  if (!text) return '-'
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

const formatJson = (obj) => {
  try {
    if (typeof obj === 'string') {
      return JSON.stringify(JSON.parse(obj), null, 2)
    }
    return JSON.stringify(obj, null, 2)
  } catch (error) {
    return String(obj)
  }
}

const handleExport = () => {
  emit('export', props.logData)
  ElMessage.success('正在导出日志详情...')
}

const handleClose = () => {
  visible.value = false
}

// 暴露方法
defineExpose({
  visible
})
</script>

<style scoped>
.log-detail {
  max-height: 600px;
  overflow-y: auto;
}

.detail-section {
  margin-top: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 500;
}

.user-agent-text,
.url-text {
  font-family: monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
  word-break: break-all;
}

.json-viewer {
  background-color: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  padding: 16px;
  max-height: 200px;
  overflow-y: auto;
}

.json-viewer pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
  color: var(--el-text-color-primary);
  white-space: pre-wrap;
  word-break: break-all;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>