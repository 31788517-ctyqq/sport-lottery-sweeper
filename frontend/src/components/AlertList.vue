<template>
  <div class="alert-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 空状态 -->
    <div v-else-if="!alerts.length" class="empty-container">
      <el-empty description="暂无告警信息">
        <el-button type="primary" @click="$emit('refresh')">
          刷新数据
        </el-button>
      </el-empty>
    </div>

    <!-- 告警列表 -->
    <div v-else class="alerts-container">
      <div 
        v-for="alert in alerts" 
        :key="alert.id"
        class="alert-item"
        :class="[`severity-${alert.severity}`, `status-${alert.status}`]"
      >
        <!-- 告警头部 -->
        <div class="alert-header">
          <div class="alert-title-section">
            <el-tag :type="getSeverityTag(alert.severity)" size="small" class="severity-tag">
              {{ getSeverityText(alert.severity) }}
            </el-tag>
            <el-tag :type="getStatusTag(alert.status)" size="small" class="status-tag">
              {{ getStatusText(alert.status) }}
            </el-tag>
            <h4 class="alert-title">{{ alert.title }}</h4>
          </div>
          
          <div class="alert-meta">
            <span class="alert-source">
              <el-icon><component :is="getSourceIcon(alert.source)" /></el-icon>
              {{ getSourceText(alert.source) }}
            </span>
            <span class="alert-time">{{ formatTime(alert.created_at) }}</span>
          </div>
        </div>

        <!-- 告警内容 -->
        <div class="alert-content">
          <p class="alert-condition">
            <strong>触发条件:</strong> {{ alert.condition }}
          </p>
          <p class="alert-description">{{ alert.description }}</p>
          
          <!-- 处理信息 -->
          <div v-if="alert.acknowledged_by" class="alert-handler">
            <el-icon><User /></el-icon>
            <span>处理人: {{ alert.acknowledged_by }}</span>
            <span class="handler-time">于 {{ formatTime(alert.updated_at) }}</span>
          </div>
        </div>

        <!-- 告警操作 -->
        <div class="alert-actions">
          <el-button-group size="small">
            <el-button 
              v-if="alert.status === 'unresolved'"
              type="primary" 
              @click="$emit('acknowledge', alert)"
            >
              <el-icon><Check /></el-icon>
              确认
            </el-button>
            
            <el-button 
              v-if="['unresolved', 'acknowledged'].includes(alert.status)"
              type="success" 
              @click="$emit('resolve', alert)"
            >
              <el-icon><CircleCheck /></el-icon>
              解决
            </el-button>
            
            <el-button 
              v-if="alert.status === 'unresolved'"
              type="warning" 
              @click="$emit('ignore', alert)"
            >
              <el-icon><Close /></el-icon>
              忽略
            </el-button>
            
            <el-button size="small">
              <el-icon><Document /></el-icon>
              详情
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { 
  Check, CircleCheck, Close, Document, User,
  Monitor, Setting, DataAnalysis, Network, Warning 
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  alerts: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

// Emits
const emit = defineEmits(['acknowledge', 'resolve', 'ignore', 'refresh'])

// 方法
const getSeverityTag = (severity) => {
  const map = {
    critical: 'danger',
    high: 'warning',
    medium: 'info',
    low: 'success'
  }
  return map[severity] || 'info'
}

const getSeverityText = (severity) => {
  const map = {
    critical: '严重',
    high: '高危',
    medium: '中等',
    low: '低危'
  }
  return map[severity] || severity
}

const getStatusTag = (status) => {
  const map = {
    unresolved: 'danger',
    acknowledged: 'warning',
    resolved: 'success',
    ignored: 'info'
  }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = {
    unresolved: '未处理',
    acknowledged: '处理中',
    resolved: '已解决',
    ignored: '已忽略'
  }
  return map[status] || status
}

const getSourceIcon = (source) => {
  const iconMap = {
    system: Monitor,
    application: Setting,
    database: DataAnalysis,
    network: Network,
    security: Warning
  }
  return iconMap[source] || Monitor
}

const getSourceText = (source) => {
  const textMap = {
    system: '系统监控',
    application: '应用服务',
    database: '数据库',
    network: '网络设备',
    security: '安全检测'
  }
  return textMap[source] || source
}

const formatTime = (time) => {
  if (!time) return '-'
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  return date.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.alert-list {
  width: 100%;
}

.loading-container,
.empty-container {
  padding: 40px;
  text-align: center;
}

.alerts-container {
  space-y: 12px;
}

.alert-item {
  background: white;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 12px;
  border-left: 4px solid;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.alert-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 严重程度边框颜色 */
.alert-item.severity-critical {
  border-left-color: var(--el-color-danger);
}

.alert-item.severity-high {
  border-left-color: var(--el-color-warning);
}

.alert-item.severity-medium {
  border-left-color: var(--el-color-info);
}

.alert-item.severity-low {
  border-left-color: var(--el-color-success);
}

/* 状态背景色 */
.alert-item.status-resolved {
  opacity: 0.7;
  background: var(--el-color-success-light-9);
}

.alert-item.status-ignored {
  opacity: 0.6;
  background: var(--el-color-info-light-9);
}

.alert-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.alert-title-section {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.severity-tag,
.status-tag {
  flex-shrink: 0;
}

.alert-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--el-text-color-primary);
}

.alert-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  flex-shrink: 0;
}

.alert-source {
  display: flex;
  align-items: center;
  gap: 4px;
}

.alert-time {
  white-space: nowrap;
}

.alert-content {
  margin-bottom: 16px;
}

.alert-condition {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.alert-description {
  margin: 0 0 8px 0;
  color: var(--el-text-color-primary);
  line-height: 1.5;
}

.alert-handler {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--el-text-color-regular);
  padding: 8px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.handler-time {
  margin-left: auto;
  opacity: 0.8;
}

.alert-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid var(--el-border-color-lighter);
}

@media (max-width: 768px) {
  .alert-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .alert-meta {
    align-items: flex-start;
  }
  
  .alert-title-section {
    flex-wrap: wrap;
  }
  
  .alert-actions {
    flex-direction: column;
  }
  
  .alert-actions .el-button-group {
    width: 100%;
    display: flex;
  }
  
  .alert-actions .el-button {
    flex: 1;
  }
}</style>