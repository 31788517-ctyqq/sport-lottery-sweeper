<template>
  <div class="intelligence-list">
    <div class="list-header">
      <h2 class="list-title">情报筛查列表</h2>
      <button @click="loadIntelligenceData" class="refresh-btn">
        🔄 刷新
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载情报数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="errorMessage" class="error-container">
      <div class="error-icon">❌</div>
      <h3>加载失败</h3>
      <p>{{ errorMessage }}</p>
      <button @click="loadIntelligenceData" class="retry-btn">重新加载</button>
    </div>

    <!-- 空数据状态 -->
    <div v-else-if="!intelligenceItems.length" class="empty-container">
      <div class="empty-icon">📋</div>
      <h3>暂无情报数据</h3>
      <p>当前没有需要筛查的情报信息</p>
    </div>

    <!-- 数据列表 -->
    <div v-else class="list-container">
      <!-- 统计信息 -->
      <div class="list-stats">
        <span class="stats-item">共 {{ intelligenceData.total || intelligenceItems.length }} 条</span>
        <span class="stats-item">显示 {{ intelligenceItems.length }} 条</span>
      </div>

      <!-- 情报项目列表 -->
      <div class="items-list">
        <div 
          v-for="item in intelligenceItems" 
          :key="item.id || Math.random()"
          class="intelligence-item"
          :class="getItemClass(item)"
        >
          <!-- 项目头部 -->
          <div class="item-header">
            <div class="item-title">
              <span class="item-type-badge" :class="getItemTypeClass(item.type)">
                {{ getItemTypeText(item.type) }}
              </span>
              {{ item.title || '未命名情报' }}
            </div>
            <div class="item-meta">
              <span class="item-date">{{ formatDate(item.created_at || item.date) }}</span>
              <span class="item-priority" :class="getPriorityClass(item.priority)">
                {{ getPriorityText(item.priority) }}
              </span>
            </div>
          </div>

          <!-- 项目内容 -->
          <div class="item-content">
            <p class="item-description">{{ item.description || item.content || '暂无描述' }}</p>
            
            <!-- 标签 -->
            <div v-if="item.tags && item.tags.length" class="item-tags">
              <span 
                v-for="tag in item.tags" 
                :key="tag"
                class="tag"
              >
                {{ tag }}
              </span>
            </div>
          </div>

          <!-- 项目操作 -->
          <div class="item-actions">
            <button 
              @click="handleView(item)"
              class="action-btn view-btn"
            >
              👁️ 查看
            </button>
            <button 
              @click="handleReview(item)"
              class="action-btn review-btn"
            >
              ✅ 审核
            </button>
            <button 
              @click="handleIgnore(item)"
              class="action-btn ignore-btn"
            >
              ⏭️ 忽略
            </button>
          </div>
        </div>
      </div>

      <!-- 分页 (预留) -->
      <div v-if="intelligenceData.total > intelligenceItems.length" class="pagination">
        <p>还有更多数据，当前显示前 {{ intelligenceItems.length }} 条</p>
        <button class="load-more-btn">加载更多</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getIntelligenceScreeningList } from '@/api/example.js'

// 响应式数据
const loading = ref(false)
const errorMessage = ref('')
const intelligenceData = ref({})
const intelligenceItems = ref([])

// 加载情报数据
const loadIntelligenceData = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const result = await getIntelligenceScreeningList()
    
    if (result.code === 200) {
      intelligenceData.value = result.data || {}
      intelligenceItems.value = result.data.items || result.data || []
      
      console.log('情报数据:', intelligenceData.value)
      
      // 触发数据加载事件
      emit('data-loaded', intelligenceData.value)
    } else {
      errorMessage.value = result.message || '获取情报数据失败'
    }
  } catch (error) {
    console.error('加载情报数据错误:', error)
    errorMessage.value = error.message || '网络错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 格式化日期
const formatDate = (dateString: string): string => {
  if (!dateString) return '未知时间'
  
  try {
    const date = new Date(dateString)
    return date.toLocaleString('zh-CN')
  } catch {
    return dateString
  }
}

// 获取项目CSS类名
const getItemClass = (item: any): string => {
  const classes = []
  
  if (item.priority === 'high' || item.priority === 3) classes.push('high-priority')
  if (item.priority === 'medium' || item.priority === 2) classes.push('medium-priority')
  if (item.priority === 'low' || item.priority === 1) classes.push('low-priority')
  
  if (item.status === 'reviewed') classes.push('reviewed')
  if (item.status === 'ignored') classes.push('ignored')
  
  return classes.join(' ')
}

// 获取项目类型样式
const getItemTypeClass = (type: string): string => {
  const typeMap = {
    match: 'type-match',
    odds: 'type-odds', 
    news: 'type-news',
    analysis: 'type-analysis',
    default: 'type-default'
  }
  return typeMap[type] || typeMap.default
}

// 获取项目类型文本
const getItemTypeText = (type: string): string => {
  const textMap = {
    match: '比赛',
    odds: '赔率',
    news: '新闻',
    analysis: '分析',
    default: '其他'
  }
  return textMap[type] || textMap.default
}

// 获取优先级样式
const getPriorityClass = (priority: string | number): string => {
  const priorityMap = {
    high: 'priority-high',
    medium: 'priority-medium', 
    low: 'priority-low',
    3: 'priority-high',
    2: 'priority-medium',
    1: 'priority-low',
    default: 'priority-default'
  }
  return priorityMap[priority] || priorityMap.default
}

// 获取优先级文本
const getPriorityText = (priority: string | number): string => {
  const textMap = {
    high: '高',
    medium: '中',
    low: '低', 
    3: '高',
    2: '中',
    1: '低',
    default: '普通'
  }
  return textMap[priority] || textMap.default
}

// 事件处理函数
const handleView = (item: any) => {
  console.log('查看情报:', item)
  emit('view-item', item)
  // 这里可以实现查看详情的逻辑，比如打开模态框或跳转页面
}

const handleReview = (item: any) => {
  console.log('审核情报:', item)
  emit('review-item', item)
  // 这里可以实现审核逻辑
  item.status = 'reviewed'
}

const handleIgnore = (item: any) => {
  console.log('忽略情报:', item)
  emit('ignore-item', item)
  // 这里可以实现忽略逻辑  
  item.status = 'ignored'
}

// 组件挂载时加载数据
onMounted(() => {
  loadIntelligenceData()
})

// 定义事件
const emit = defineEmits(['data-loaded', 'view-item', 'review-item', 'ignore-item'])

// 暴露方法给父组件
defineExpose({
  loadIntelligenceData,
  intelligenceItems,
  loading
})
</script>

<style scoped>
.intelligence-list {
  padding: 24px;
  background-color: #fff;
  min-height: 100vh;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 16px;
  border-bottom: 2px solid #f0f0f0;
}

.list-title {
  margin: 0;
  color: #333;
  font-size: 24px;
  font-weight: 600;
}

.refresh-btn {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.refresh-btn:hover {
  background: #e9ecef;
  transform: rotate(180deg);
}

.loading-container, .error-container, .empty-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  text-align: center;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon, .empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  background-color: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 16px;
}

.retry-btn:hover {
  background-color: #5a6fd8;
}

.list-container {
  max-width: 1200px;
}

.list-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 6px;
}

.stats-item {
  color: #666;
  font-size: 14px;
}

.items-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.intelligence-item {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.intelligence-item:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.intelligence-item.high-priority {
  border-left: 4px solid #dc3545;
}

.intelligence-item.medium-priority {
  border-left: 4px solid #ffc107;
}

.intelligence-item.low-priority {
  border-left: 4px solid #28a745;
}

.intelligence-item.reviewed {
  opacity: 0.7;
  background: #f8f9fa;
}

.intelligence-item.ignored {
  opacity: 0.5;
  background: #fff5f5;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 16px;
}

.item-title {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 12px;
}

.item-type-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  color: white;
}

.type-match { background-color: #007bff; }
.type-odds { background-color: #28a745; }
.type-news { background-color: #17a2b8; }
.type-analysis { background-color: #6f42c1; }
.type-default { background-color: #6c757d; }

.item-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
  font-size: 12px;
  color: #666;
}

.item-date {
  white-space: nowrap;
}

.item-priority {
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 500;
  color: white;
}

.priority-high { background-color: #dc3545; }
.priority-medium { background-color: #ffc107; color: #333; }
.priority-low { background-color: #28a745; }
.priority-default { background-color: #6c757d; }

.item-content {
  margin-bottom: 16px;
}

.item-description {
  color: #666;
  line-height: 1.5;
  margin: 0 0 12px 0;
}

.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag {
  background: #e9ecef;
  color: #495057;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
}

.item-actions {
  display: flex;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
}

.view-btn {
  background: #17a2b8;
  color: white;
}

.view-btn:hover {
  background: #138496;
}

.review-btn {
  background: #28a745;
  color: white;
}

.review-btn:hover {
  background: #218838;
}

.ignore-btn {
  background: #6c757d;
  color: white;
}

.ignore-btn:hover {
  background: #5a6268;
}

.pagination {
  text-align: center;
  padding: 20px;
  color: #666;
}

.load-more-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
}

.load-more-btn:hover {
  background: #5a6fd8;
}

@media (max-width: 768px) {
  .intelligence-list {
    padding: 16px;
  }
  
  .list-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .item-header {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .item-meta {
    align-items: flex-start;
  }
  
  .item-actions {
    flex-wrap: wrap;
  }
}
</style>