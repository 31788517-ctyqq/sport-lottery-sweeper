<template>
  <el-dialog v-model="visible" title="日志详情" width="720px">
    <div v-if="log" class="detail">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="时间">{{ formatDate(log.timestamp) }}</el-descriptions-item>
        <el-descriptions-item label="级别">
          <el-tag :type="getLevelTagType(log.level)">{{ log.level || '-' }}</el-tag>
        </el-descriptions-item>

        <el-descriptions-item label="类型">{{ log.log_type || '-' }}</el-descriptions-item>
        <el-descriptions-item label="模块">{{ log.module || '-' }}</el-descriptions-item>

        <el-descriptions-item label="用户ID">{{ log.user_id ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP">{{ log.ip_address || '-' }}</el-descriptions-item>

        <el-descriptions-item label="请求路径" :span="2">{{ log.request_path || '-' }}</el-descriptions-item>
        <el-descriptions-item label="响应状态">{{ log.response_status ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="耗时(ms)">{{ log.duration_ms ?? '-' }}</el-descriptions-item>

        <el-descriptions-item label="会话ID" :span="2">{{ log.session_id || '-' }}</el-descriptions-item>
        <el-descriptions-item label="UA" :span="2">{{ log.user_agent || '-' }}</el-descriptions-item>

        <el-descriptions-item label="消息" :span="2">
          <div class="message">{{ log.message || '-' }}</div>
        </el-descriptions-item>
      </el-descriptions>

      <div v-if="extraPretty" class="extra">
        <div class="extra-title">额外数据</div>
        <pre class="extra-pre">{{ extraPretty }}</pre>
      </div>
    </div>

    <template #footer>
      <span class="footer">
        <el-button @click="visible = false">关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  log: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get() {
    return props.modelValue
  },
  set(v) {
    emit('update:modelValue', v)
  }
})

const formatDate = (v) => {
  if (!v) return '-'
  const d = new Date(v)
  if (Number.isNaN(d.getTime())) return String(v)
  return d.toLocaleString('zh-CN')
}

const getLevelTagType = (level) => {
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

const extraPretty = computed(() => {
  const raw = props.log?.extra_data
  if (!raw) return ''
  try {
    if (typeof raw === 'string') return JSON.stringify(JSON.parse(raw), null, 2)
    return JSON.stringify(raw, null, 2)
  } catch {
    return String(raw)
  }
})
</script>

<style scoped>
.detail {
  max-height: 70vh;
  overflow: auto;
}

.message {
  white-space: pre-wrap;
  word-break: break-word;
}

.extra {
  margin-top: 16px;
}

.extra-title {
  font-weight: 600;
  margin-bottom: 8px;
}

.extra-pre {
  background: var(--el-fill-color-lighter);
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 12px;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.5;
}

.footer {
  display: flex;
  justify-content: flex-end;
}
</style>

