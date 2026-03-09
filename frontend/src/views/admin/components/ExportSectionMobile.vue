<template>
  <div class="export-section-mobile">
    <div class="export-header">
      <h2 class="export-title">数据导出</h2>
      <p class="export-description">
        当前共有 {{ totalResults }} 条筛选结果，可选择以下格式导出数据
      </p>
    </div>
    
    <div class="export-options">
      <div class="export-option" v-for="option in exportOptions" :key="option.id">
        <button
          class="export-button"
          :class="option.className"
          @click="handleExport(option.id)"
          :disabled="totalResults === 0"
        >
          <div class="export-icon">
            <i :class="option.icon"></i>
          </div>
          <div class="export-info">
            <h3 class="export-name">{{ option.name }}</h3>
            <p class="export-desc">{{ option.description }}</p>
            <div class="export-stats" v-if="option.stats">
              <span v-for="stat in option.stats" :key="stat.label" class="stat-item">
                <strong>{{ stat.value }}</strong> {{ stat.label }}
              </span>
            </div>
          </div>
          <div class="export-action">
            <i class="el-icon-download"></i>
          </div>
        </button>
        <div v-if="option.tips" class="export-tips">
          <i class="el-icon-info"></i>
          <span>{{ option.tips }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="totalResults === 0" class="export-empty">
      <i class="el-icon-document"></i>
      <p>暂无数据可导出，请先进行筛选操作</p>
    </div>
    
    <div class="export-history" v-if="exportHistory.length > 0">
      <h3 class="history-title">最近导出记录</h3>
      <div class="history-list">
        <div v-for="item in exportHistory" :key="item.timestamp" class="history-item">
          <div class="history-info">
            <div class="history-name">{{ item.format.toUpperCase() }} 文件</div>
            <div class="history-time">{{ formatTime(item.timestamp) }}</div>
          </div>
          <div class="history-size">{{ item.size }}</div>
        </div>
      </div>
    </div>
    
    <div class="export-footer">
      <p class="footer-note">
        <i class="el-icon-warning"></i>
        导出文件将自动下载到您的设备，建议使用 Wi-Fi 网络进行大文件下载
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  pagedResults: {
    type: Array,
    default: () => []
  },
  totalResults: {
    type: Number,
    default: 0
  }
})

const emit = defineEmits(['export-results'])

// 导出选项配置
const exportOptions = ref([
  {
    id: 'csv',
    name: 'CSV 格式',
    description: '通用表格格式，适合 Excel、Numbers 等软件打开',
    icon: 'el-icon-document',
    className: 'csv-option',
    stats: [
      { label: '兼容性', value: '高' },
      { label: '文件大小', value: '较小' }
    ],
    tips: '推荐用于数据分析和交换'
  },
  {
    id: 'json',
    name: 'JSON 格式',
    description: '结构化数据格式，适合程序处理和数据迁移',
    icon: 'el-icon-data-analysis',
    className: 'json-option',
    stats: [
      { label: '可读性', value: '高' },
      { label: '完整性', value: '完整' }
    ],
    tips: '保留完整字段信息，适合开发人员使用'
  },
  {
    id: 'excel',
    name: 'Excel 格式',
    description: '专业表格格式，支持多工作表和数据格式化',
    icon: 'el-icon-files',
    className: 'excel-option',
    stats: [
      { label: '专业性', value: '高' },
      { label: '可视化', value: '优秀' }
    ],
    tips: '提供更好的阅读体验，适合商务场景'
  }
])

// 导出历史记录
const exportHistory = ref([])

// 处理导出
const handleExport = (format) => {
  if (props.totalResults === 0) {
    ElMessage.warning('没有数据可导出，请先进行筛选操作')
    return
  }
  
  emit('export-results', format)
  
  // 记录导出历史
  const historyItem = {
    format,
    timestamp: Date.now(),
    size: format === 'csv' ? '约 ' + Math.ceil(props.totalResults * 0.5) + ' KB' :
           format === 'json' ? '约 ' + Math.ceil(props.totalResults * 1.2) + ' KB' :
           '约 ' + Math.ceil(props.totalResults * 1.5) + ' KB'
  }
  
  exportHistory.value.unshift(historyItem)
  // 只保留最近5条记录
  if (exportHistory.value.length > 5) {
    exportHistory.value = exportHistory.value.slice(0, 5)
  }
  
  ElMessage.success(`正在导出 ${format.toUpperCase()} 文件，请稍候...`)
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  // 如果是一分钟内
  if (diff < 60000) {
    return '刚刚'
  }
  
  // 如果是一小时内
  if (diff < 3600000) {
    return Math.floor(diff / 60000) + '分钟前'
  }
  
  // 如果是今天
  if (date.getDate() === now.getDate() && 
      date.getMonth() === now.getMonth() && 
      date.getFullYear() === now.getFullYear()) {
    return date.getHours().toString().padStart(2, '0') + ':' + 
           date.getMinutes().toString().padStart(2, '0')
  }
  
  // 如果是昨天
  const yesterday = new Date(now)
  yesterday.setDate(yesterday.getDate() - 1)
  if (date.getDate() === yesterday.getDate() && 
      date.getMonth() === yesterday.getMonth() && 
      date.getFullYear() === yesterday.getFullYear()) {
    return '昨天 ' + date.getHours().toString().padStart(2, '0') + ':' + 
           date.getMinutes().toString().padStart(2, '0')
  }
  
  // 其他情况
  return date.getFullYear() + '-' + 
         (date.getMonth() + 1).toString().padStart(2, '0') + '-' + 
         date.getDate().toString().padStart(2, '0')
}

// 初始化时加载历史记录（示例数据）
onMounted(() => {
  // 这里可以从 localStorage 加载真实历史记录
  const savedHistory = localStorage.getItem('beidan_export_history')
  if (savedHistory) {
    try {
      exportHistory.value = JSON.parse(savedHistory)
    } catch (e) {
      console.error('Failed to parse export history:', e)
    }
  }
  
  // 保存历史记录到 localStorage
  const saveHistory = () => {
    localStorage.setItem('beidan_export_history', JSON.stringify(exportHistory.value))
  }
  
  // 监听历史记录变化
  watch(exportHistory, saveHistory, { deep: true })
})
</script>

<style scoped>
.export-section-mobile {
  padding: 16px;
  background-color: var(--bg-body);
  min-height: 100%;
}

.export-header {
  margin-bottom: 24px;
}

.export-title {
  margin: 0 0 8px 0;
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.export-description {
  margin: 0;
  font-size: var(--font-size-base);
  color: var(--text-secondary);
  line-height: 1.4;
}

.export-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.export-option {
  position: relative;
}

.export-button {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  background-color: var(--bg-card);
  cursor: pointer;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transition: all 0.2s ease;
  text-align: left;
  min-height: 100px;
  box-sizing: border-box;
}

.export-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary);
}

.export-button:active {
  transform: translateY(0);
}

.export-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
  border-color: var(--border-color);
}

.export-button:disabled:hover {
  border-color: var(--border-color);
}

.export-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  margin-right: 16px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 24px;
  flex-shrink: 0;
}

.export-info {
  flex: 1;
  min-width: 0;
}

.export-name {
  margin: 0 0 4px 0;
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
  line-height: 1.2;
}

.export-desc {
  margin: 0 0 8px 0;
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.4;
}

.export-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
  padding: 2px 8px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.stat-item strong {
  color: var(--text-secondary);
}

.export-action {
  margin-left: 12px;
  color: var(--primary);
  font-size: 20px;
  flex-shrink: 0;
}

.export-tips {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 8px 12px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-md);
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  border-left: 3px solid var(--primary);
}

.export-tips i {
  color: var(--primary);
}

.export-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 16px;
  text-align: center;
  color: var(--text-tertiary);
}

.export-empty i {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--border-color);
}

.export-empty p {
  margin: 0;
  font-size: var(--font-size-base);
}

.export-history {
  margin-top: 32px;
  padding: 16px;
  background-color: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.history-title {
  margin: 0 0 12px 0;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-semibold);
  color: var(--text-primary);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: var(--bg-body);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.history-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--text-primary);
}

.history-time {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.history-size {
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  font-weight: var(--font-weight-medium);
  padding: 2px 8px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.export-footer {
  margin-top: 24px;
  padding: 12px 16px;
  background-color: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border-left: 4px solid var(--warning);
}

.footer-note {
  margin: 0;
  font-size: var(--font-size-xs);
  color: var(--text-secondary);
  line-height: 1.4;
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.footer-note i {
  color: var(--warning);
  margin-top: 2px;
}

/* 主题适配 */
[data-theme="dark"] .export-button {
  background-color: var(--bg-card);
  border-color: var(--border-dark);
}

[data-theme="dark"] .export-button:hover {
  border-color: var(--primary);
}

[data-theme="dark"] .export-history {
  background-color: var(--bg-card);
  border-color: var(--border-dark);
}

[data-theme="dark"] .history-item {
  background-color: var(--bg-body);
  border-color: var(--border-dark);
}

/* 触摸优化 */
@media (hover: none) and (pointer: coarse) {
  .export-button:hover {
    transform: none;
  }
  
  .export-button:active {
    transform: scale(0.98);
  }
}

/* 响应式调整 */
@media (max-width: 480px) {
  .export-section-mobile {
    padding: 12px;
  }
  
  .export-button {
    padding: 12px;
    min-height: 90px;
  }
  
  .export-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
    margin-right: 12px;
  }
  
  .export-name {
    font-size: var(--font-size-base);
  }
  
  .export-desc {
    font-size: var(--font-size-xs);
  }
}
</style>