<template>
  <div class="service-status">
    <el-card class="status-card">
      <template #header>
        <div class="card-header">
          <span class="card-title">
            <el-icon><Monitor /></el-icon>
            服务状态监控
          </span>
          <el-button 
            type="primary" 
            :icon="Refresh" 
            circle 
            size="small"
            @click="refreshStatus"
            :loading="loading"
          />
        </div>
      </template>
      
      <div class="status-content">
        <!-- 服务状态指示器 -->
        <div class="status-indicators">
          <div class="indicator-item" :class="{ 'online': serviceHealth, 'offline': !serviceHealth }">
            <el-icon class="indicator-icon">
              <CircleCheck v-if="serviceHealth" />
              <CircleClose v-else />
            </el-icon>
            <div class="indicator-info">
              <span class="indicator-label">后端服务</span>
              <span class="indicator-value">{{ serviceHealth ? '在线' : '离线' }}</span>
            </div>
          </div>
          
          <div class="indicator-item" :class="{ 'online': apiHealth, 'offline': !apiHealth }">
            <el-icon class="indicator-icon">
              <CircleCheck v-if="apiHealth" />
              <CircleClose v-else />
            </el-icon>
            <div class="indicator-info">
              <span class="indicator-label">API接口</span>
              <span class="indicator-value">{{ apiHealth ? '正常' : '异常' }}</span>
            </div>
          </div>
        </div>

        <!-- 详细信息 -->
        <div v-if="statusInfo.service" class="status-details">
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="服务状态">
              <el-tag :type="serviceHealth ? 'success' : 'danger'">
                {{ statusInfo.service.status }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="API版本">
              {{ statusInfo.service.version || '未知' }}
            </el-descriptions-item>
            <el-descriptions-item label="时间戳">
              {{ formatTime(statusInfo.service.timestamp) }}
            </el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- 错误信息 -->
        <div v-if="errorMessage" class="error-message">
          <el-alert 
            :title="errorMessage" 
            type="error" 
            show-icon 
            :closable="false"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { 
  Monitor, Refresh, CircleCheck, CircleClose 
} from '@element-plus/icons-vue'
import { checkServiceHealth, checkApiHealth } from '@/api/example.js'

// Props
const props = defineProps({
  autoRefresh: {
    type: Boolean,
    default: true
  },
  refreshInterval: {
    type: Number,
    default: 30000 // 30秒
  }
})

// Emits
const emit = defineEmits(['status-change'])

// 响应式数据
const loading = ref(false)
const serviceHealth = ref(false)
const apiHealth = ref(false)
const statusInfo = ref({})
const errorMessage = ref('')
let refreshTimer = null

// 格式化时间
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  return new Date(timestamp * 1000).toLocaleString('zh-CN')
}

// 检查服务状态
const checkStatus = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    // 并行检查服务和API状态
    const [serviceResult, apiResult] = await Promise.allSettled([
      checkServiceHealth(),
      checkApiHealth()
    ])

    // 处理服务状态
    if (serviceResult.status === 'fulfilled') {
      serviceHealth.value = serviceResult.value.status === 'healthy'
      statusInfo.value.service = serviceResult.value
    } else {
      serviceHealth.value = false
      errorMessage.value = '后端服务连接失败'
    }

    // 处理API状态
    if (apiResult.status === 'fulfilled') {
      apiHealth.value = apiResult.value.status === 'healthy'
      statusInfo.value.api = apiResult.value
    } else {
      apiHealth.value = false
      if (!errorMessage.value) {
        errorMessage.value = 'API接口连接失败'
      }
    }

    // 发送状态变更事件
    emit('status-change', {
      service: serviceHealth.value,
      api: apiHealth.value,
      timestamp: Date.now()
    })

  } catch (error) {
    console.error('检查服务状态失败:', error)
    errorMessage.value = error.message || '服务状态检查失败'
    serviceHealth.value = false
    apiHealth.value = false
  } finally {
    loading.value = false
  }
}

// 刷新状态
const refreshStatus = () => {
  checkStatus()
}

// 启动自动刷新
const startAutoRefresh = () => {
  if (props.autoRefresh && props.refreshInterval > 0) {
    refreshTimer = setInterval(checkStatus, props.refreshInterval)
  }
}

// 停止自动刷新
const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 生命周期
onMounted(() => {
  checkStatus()
  startAutoRefresh()
})

// 暴露方法给父组件
defineExpose({
  checkStatus,
  refreshStatus,
  startAutoRefresh,
  stopAutoRefresh
})
</script>

<style scoped>
.service-status {
  width: 100%;
}

.status-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.status-content {
  space-y: 16px;
}

.status-indicators {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.indicator-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  background: var(--el-fill-color-light);
  transition: all 0.3s ease;
}

.indicator-item.online {
  background: var(--el-color-success-light-9);
  border: 1px solid var(--el-color-success-light-5);
}

.indicator-item.offline {
  background: var(--el-color-danger-light-9);
  border: 1px solid var(--el-color-danger-light-5);
}

.indicator-icon {
  font-size: 20px;
}

.indicator-item.online .indicator-icon {
  color: var(--el-color-success);
}

.indicator-item.offline .indicator-icon {
  color: var(--el-color-danger);
}

.indicator-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.indicator-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
}

.indicator-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.status-details {
  margin-top: 16px;
}

.error-message {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .status-indicators {
    flex-direction: column;
  }
  
  .indicator-item {
    justify-content: center;
  }
}</style>